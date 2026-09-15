import os
import re
from datetime import datetime

from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.utils import platform


PAGE_WIDTH = 595
PAGE_HEIGHT = 842


# Apply the WalletCore rounded popup style globally.
# Every Popup in the app uses this rule because this module is loaded at startup.
Builder.load_string(
    """
#:import dp kivy.metrics.dp
<Popup>:
    background_color: 0, 0, 0, 0
    border: 0, 0, 0, 0
    canvas.before:
        Color:
            rgba: 0.035, 0.055, 0.10, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(20), dp(20), dp(20), dp(20)]
"""
)


def _pdf_text(value):
    """Return safe PDF text using the built-in Helvetica encoding."""
    text = "" if value is None else str(value)
    replacements = {
        "č": "c", "ć": "c", "š": "s", "ž": "z", "đ": "dj",
        "Č": "C", "Ć": "C", "Š": "S", "Ž": "Z", "Đ": "Dj",
        "€": "EUR", "–": "-", "—": "-", "“": '"', "”": '"',
        "’": "'", "•": "-",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = text.encode("latin-1", "replace").decode("latin-1")
    return text


def _escape_pdf(text):
    return _pdf_text(text).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _show_message(title, message):
    label = Label(
        text=message,
        font_size="15sp",
        halign="center",
        valign="middle",
        padding=(dp(12), dp(8)),
    )

    def update_label(*args):
        label.text_size = (max(1, label.width - dp(24)), None)

    label.bind(size=update_label)
    update_label()

    Popup(
        title=title,
        content=label,
        size_hint=(0.88, 0.42),
    ).open()


def _save_pdf(pdf_bytes, filename):
    if platform == "android":
        download_dir = "/storage/emulated/0/Download"
        try:
            os.makedirs(download_dir, exist_ok=True)
            path = os.path.join(download_dir, filename)
            with open(path, "wb") as handle:
                handle.write(pdf_bytes)
            return path
        except Exception as exc:
            print("Public PDF save error:", exc)

    app = App.get_running_app()
    path = os.path.join(app.user_data_dir, filename)
    os.makedirs(app.user_data_dir, exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(pdf_bytes)
    return path


def _build_pdf(lines):
    """Create a small valid A4 PDF without external Python dependencies."""
    commands = []
    y = 800

    for text, size, bold in lines:
        if y < 42:
            break
        font = "/F2" if bold else "/F1"
        commands.append(f"BT {font} {size} Tf 42 {y} Td ({_escape_pdf(text)}) Tj ET")
        y -= size + 9

    stream = "\n".join(commands).encode("latin-1", "replace")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>",
    ]

    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]

    for number, obj in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{number} 0 obj\n".encode("ascii"))
        output.extend(obj)
        output.extend(b"\nendobj\n")

    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))

    output.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode("ascii")
    )
    return bytes(output)


def _format_amount(value, currency):
    try:
        amount = float(value)
        return f"{amount:,.2f} {currency}".replace(",", ".")
    except Exception:
        return f"{value} {currency}"


def export_pdf_for_home(screen):
    app = App.get_running_app()
    t = __import__("translations").translations[app.language]

    try:
        rows = screen.db.get_all()
        currency = app.currency

        total_income = sum(float(row[1]) for row in rows if row[2] == "income")
        total_expense = sum(float(row[1]) for row in rows if row[2] == "expense")
        balance = total_income - total_expense

        lines = [
            ("WalletCore", 22, True),
            (t.get("pdf_export", "PDF Export"), 13, True),
            (datetime.now().strftime("%Y-%m-%d %H:%M"), 9, False),
            ("", 6, False),
            (f"{t.get('balance', 'Balance')}: {_format_amount(balance, currency)}", 11, True),
            (f"{t.get('income', 'Income')}: {_format_amount(total_income, currency)}", 10, False),
            (f"{t.get('expense', 'Expense')}: {_format_amount(total_expense, currency)}", 10, False),
            ("", 8, False),
            ("TRANSACTIONS", 12, True),
            ("# | Category | Amount | Type | Note | Date", 8, True),
        ]

        for number, row in enumerate(rows, start=1):
            transaction_id, amount, ttype, category, note, time = row
            try:
                category_text = screen.translate_category(category)
            except Exception:
                category_text = category

            type_text = t.get(ttype, ttype)
            note_text = "" if note is None else str(note).replace("\n", " ")
            date_text = str(time).split(" ")[0]

            row_text = (
                f"{number} | {category_text} | {_format_amount(amount, currency)} | "
                f"{type_text} | {note_text} | {date_text}"
            )
            row_text = re.sub(r"\s+", " ", row_text).strip()

            # Keep each transaction on one readable PDF line.
            if len(row_text) > 105:
                row_text = row_text[:102] + "..."
            lines.append((row_text, 7.5, False))

        lines.append(("", 8, False))
        lines.append((f"{t.get('transaction', 'Transaction')} count: {len(rows)}", 9, True))

        pdf_bytes = _build_pdf(lines)
        filename = "WalletCore_Report.pdf"
        path = _save_pdf(pdf_bytes, filename)

        _show_message(
            t.get("pdf_export", "PDF Export"),
            "PDF successfully saved.\n\n" + path,
        )

    except Exception as exc:
        print("PDF export error:", exc)
        _show_message(
            t.get("error", "Error"),
            "PDF export failed.",
        )
