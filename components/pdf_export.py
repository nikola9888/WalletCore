import os
from datetime import datetime

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.utils import platform

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def _safe_text(value):
    return "" if value is None else str(value)


def _register_fonts():
    regular = None
    bold = None

    candidates = [
        ("/system/fonts/Roboto-Regular.ttf", "/system/fonts/Roboto-Bold.ttf"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ("/Library/Fonts/Arial Unicode.ttf", "/Library/Fonts/Arial Unicode.ttf"),
    ]

    for regular_path, bold_path in candidates:
        if os.path.exists(regular_path):
            regular = regular_path
            if os.path.exists(bold_path):
                bold = bold_path
            break

    if regular:
        try:
            if "WalletCore-Regular" not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont("WalletCore-Regular", regular))
            if bold and "WalletCore-Bold" not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont("WalletCore-Bold", bold))
            elif "WalletCore-Bold" not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont("WalletCore-Bold", regular))
            return "WalletCore-Regular", "WalletCore-Bold"
        except Exception:
            pass

    return "Helvetica", "Helvetica-Bold"


def _show_message(title, message):
    Popup(
        title=title,
        content=Label(text=message, font_size="15sp"),
        size_hint=(0.82, 0.35),
    ).open()


def _open_pdf(path):
    if platform != "android":
        return

    try:
        from jnius import autoclass

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        FileProvider = autoclass("androidx.core.content.FileProvider")
        File = autoclass("java.io.File")
        Intent = autoclass("android.content.Intent")

        activity = PythonActivity.mActivity
        file = File(path)
        uri = FileProvider.getUriForFile(
            activity,
            "com.develop4world.walletcore.fileprovider",
            file,
        )

        intent = Intent(Intent.ACTION_VIEW)
        intent.setDataAndType(uri, "application/pdf")
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)

        activity.startActivity(intent)
    except Exception as exc:
        print("PDF open error:", exc)


def export_pdf_for_home(screen):
    app = App.get_running_app()
    t = __import__("translations").translations[app.language]

    try:
        font_regular, font_bold = _register_fonts()

        rows = screen.db.get_all()
        currency = app.currency

        total_income = sum(float(row[1]) for row in rows if row[2] == "income")
        total_expense = sum(float(row[1]) for row in rows if row[2] == "expense")
        balance = total_income - total_expense

        output_dir = app.user_data_dir
        os.makedirs(output_dir, exist_ok=True)
        filename = "WalletCore_Report.pdf"
        path = os.path.join(output_dir, filename)

        page_width, page_height = A4
        pdf = canvas.Canvas(path, pagesize=A4)
        pdf.setTitle("WalletCore Report")
        pdf.setAuthor("DEVELOP4WORLD")

        left = 42
        right = page_width - 42
        y = page_height - 48

        def draw_text(text, x, y_pos, size=10, bold=False):
            pdf.setFont(font_bold if bold else font_regular, size)
            pdf.drawString(x, y_pos, _safe_text(text))

        def new_page_if_needed(current_y, needed=40):
            if current_y < needed:
                pdf.showPage()
                return page_height - 48
            return current_y

        draw_text("WalletCore", left, y, 22, True)
        y -= 26
        draw_text(t.get("pdf_export", "PDF Export"), left, y, 13, True)
        y -= 18
        draw_text(datetime.now().strftime("%Y-%m-%d %H:%M"), left, y, 9)
        y -= 30

        draw_text(t.get("balance", "Balance"), left, y, 10, True)
        draw_text(f"{balance:,.2f} {currency}".replace(",", "."), left + 125, y, 10)
        y -= 18
        draw_text(t.get("income", "Income"), left, y, 10, True)
        draw_text(f"{total_income:,.2f} {currency}".replace(",", "."), left + 125, y, 10)
        y -= 18
        draw_text(t.get("expense", "Expense"), left, y, 10, True)
        draw_text(f"{total_expense:,.2f} {currency}".replace(",", "."), left + 125, y, 10)
        y -= 30

        pdf.setLineWidth(0.7)
        pdf.line(left, y, right, y)
        y -= 20

        headers = [
            "#",
            t.get("category", "Category"),
            t.get("amount", "Amount"),
            t.get("transaction", "Transaction"),
            t.get("note", "Note"),
            "Date",
        ]
        x_positions = [left, left + 28, left + 145, left + 245, left + 330, left + 435]

        for index, header in enumerate(headers):
            draw_text(header, x_positions[index], y, 8.5, True)
        y -= 15
        pdf.line(left, y, right, y)
        y -= 15

        for number, row in enumerate(rows, start=1):
            transaction_id, amount, ttype, category, note, time = row
            category_text = screen.translate_category(category).replace("\n", " ")
            type_text = t.get(ttype, ttype)
            amount_text = f"{float(amount):,.2f} {currency}".replace(",", ".")
            note_text = _safe_text(note).replace("\n", " ")
            date_text = _safe_text(time).replace(" ", "\n", 1).split("\n")[0]

            values = [
                number,
                category_text,
                amount_text,
                type_text,
                note_text,
                date_text,
            ]

            y = new_page_if_needed(y, 45)
            if y == page_height - 48 and number > 1:
                for index, header in enumerate(headers):
                    draw_text(header, x_positions[index], y, 8.5, True)
                y -= 15
                pdf.line(left, y, right, y)
                y -= 15

            for index, value in enumerate(values):
                text = _safe_text(value)
                max_chars = 20 if index in (1, 2, 3, 4) else 9
                if len(text) > max_chars:
                    text = text[: max_chars - 3] + "..."
                draw_text(text, x_positions[index], y, 7.5)

            y -= 16

        y = new_page_if_needed(y, 55)
        pdf.line(left, y, right, y)
        y -= 18
        draw_text(
            f"{t.get('transaction', 'Transaction')} count: {len(rows)}",
            left,
            y,
            9,
        )

        pdf.save()

        _show_message(
            t.get("pdf_export", "PDF Export"),
            t.get("pdf_saved", "PDF successfully saved!") + "\n" + filename,
        )
        _open_pdf(path)

    except Exception as exc:
        print("PDF export error:", exc)
        _show_message(
            t.get("error", "Error"),
            "PDF export failed.",
        )
