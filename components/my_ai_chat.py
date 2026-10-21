import base64
import json
import os
import re
import ssl
import threading
import urllib.error
import urllib.request

import certifi

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.storage.jsonstore import JsonStore

from components.my_ai_config import AI_API_URL
from kivy.app import App
from kivy.core.window import Window
from translations import translations


class MyAIChat:
    def _get_wallet_context(self):
        """Build a compact, read-only snapshot from WalletCore's local database."""
        from collections import defaultdict
        from datetime import datetime
        from database import Database

        db = None
        try:
            db = Database()
            rows = db.get_all()
            app = App.get_running_app()
            income = 0.0
            expenses = 0.0
            by_category = defaultdict(float)
            by_month = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
            by_month_category = defaultdict(float)

            for row in rows:
                _transaction_id, amount, ttype, category, _note, time_value = row
                amount = float(amount or 0)
                category = str(category or "Ostalo")
                if ttype == "income":
                    income += amount
                elif ttype == "expense":
                    expenses += amount
                if ttype in ("income", "expense"):
                    by_category[(ttype, category)] += amount
                    month = str(time_value or "")[:7]
                    if len(month) == 7 and month[4] == "-":
                        by_month[month][ttype] += amount
                        by_month_category[(month, ttype, category)] += amount

            current_month = datetime.now().strftime("%Y-%m")
            months = {
                month: {
                    "income": round(values["income"], 2),
                    "expenses": round(values["expense"], 2)
                }
                for month, values in sorted(by_month.items())[-24:]
            }
            categories = [
                {"type": key[0], "category": key[1], "total": round(total, 2)}
                for key, total in sorted(by_category.items(), key=lambda item: item[1], reverse=True)[:30]
            ]
            current_categories = [
                {"type": key[1], "category": key[2], "total": round(total, 2)}
                for key, total in sorted(
                    (item for item in by_month_category.items() if item[0][0] == current_month),
                    key=lambda item: item[1],
                    reverse=True
                )[:30]
            ]
            recent = []
            for row in rows[:25]:
                transaction_id, amount, ttype, category, _note, time_value = row
                recent.append({
                    "id": transaction_id,
                    "amount": round(float(amount or 0), 2),
                    "type": ttype,
                    "category": str(category or "Ostalo"),
                    "note": str(_note or ""),
                    "date": str(time_value or "")
                })

            return {
                "currency": str(getattr(app, "currency", "RSD")),
                "language": str(getattr(app, "language", "sr")),
                "transaction_count": len(rows),
                "total_income": round(income, 2),
                "total_expenses": round(expenses, 2),
                "balance": round(income - expenses, 2),
                "current_month": current_month,
                "monthly_totals": months,
                "category_totals_all_time": categories,
                "category_totals_current_month": current_categories,
                "recent_transactions": recent,
                "access": "proposal_allowed_with_confirmation"
            }
        except Exception as exc:
            return {
                "available": False,
                "error": "WalletCore podaci trenutno nisu dostupni: {}".format(type(exc).__name__)
            }
        finally:
            if db is not None:
                try:
                    db.close()
                except Exception:
                    pass

    """My AI chat popup using a private server-side API proxy."""

    def __init__(self):
        self.messages = []
        self.history_store = None


    def _prepare_emoji_assets(self):
        """Create small bundled PNG icons for reliable inline display on Android."""
        app = App.get_running_app()
        icon_dir = os.path.join(app.user_data_dir, "my_ai_icons")
        os.makedirs(icon_dir, exist_ok=True)
        icons = {
            "💰": ("money.png", "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAABUUlEQVR4nO2YvQ3CMBBGL4guLRUdA7ACCzADA2QCKioqJsgAzMACrMAAdFS0qUOBDg7HcZzEPtvhnoSElJC8j/M/gCAISZPZ3ljfi9qnCCVbldZeM58iHCQfQAiNVWd51BVbB1ZZZrnR0XgxpLhKW5DWAFR+czn5cLLiut1/vutCaEehWOTV9+tahHEYDS2PmDwaATBlLPII+qhVSH4im3O/kHZKF7BWwLU8AGMFqPz6WAx6xu1QAsC7H+CQylIBF/Lqb7EzszYhnfxzl/98+j4j6CikE7YJQQkWwCTaJ0SQADaCtiGSn8gkwBAW58rJPQABK2AStJUHYA6AMymiE+2SV5/R2OH4Wk67XEoAfHdnbAEA3C3m6NaStQn5+FPY9wNjQugqOL15ANuXj83HGNBHPVoxViCWECYPbQCaMnSIroOt6R4tUmI+3BUEQRD+mxfxpoMoZu3mwAAAAABJRU5ErkJggg=="),
            "📈": ("chart.png", "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAABnElEQVR4nO2ZPVLDMBCFXxgqCg7gNg2XoKDlOHQwlJnQ5ThpKbgEDW0OQEEbCmZjRayklbRCa+NvJjN2xh6/t/sk/whYWPjfrKQHHj6Px5ZCOIbrVVJf8oAewn1iRqIGXPF3Lx+amkS8Pq5P2yETQQMkvodwHzLCmbjgTrAkHhh1cHFmDUyJXwasVZ8IdeGyi5oI79tx4N48pYtoKkKueG6fQ9yB3Mrkcv98AJAW7GOqAyWYMPBTfeDh6+3sf0mnuw9iEk+Qif1mEJ1vogM+UvFAZwN+9YE88UBHA5z4EpqMgdSUGxKfW32gQQdKbkZAmXigQ4Q0cu+iGqHQ3VQr7xxqHQjdjNz93dXt6UfUVB9Q6ABXXd8EgDPRtK/xTFXVgVg09puhuroSijowzixrttqucNrebUuulKZ6DPh5DlXdj4vWI7naLCSJS4v3CJVZ6C+yHqLaQIuq5lAUod6iXUy+D+RQOY22ZXKfVUoQG7CUe5esCFk0Mb8I0Td4d3HBAqE1gvl3ALDXhdgKzXzXyIhJr1K6WF0nXlio5BsNJp3XYjWl4wAAAABJRU5ErkJggg=="),
            "📅": ("calendar.png", "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAABN0lEQVR4nO2ZuRHCMBBFvxkiyDhSCGiAfqAWAiogJrb7oQECSDkiIBUJYjxmV8inJHtfBGN59T97WIwBQeg2UdEblVLqGySKnMXpFd3YF8SAa/o2i26rlSpz3RYqzjhJjH1hNFCVsDJoDZwRtoR8EJ+G0xN8D5AGfPv1NZSu4DNANoavGQB+mzn4DJAGHrt90zqsoHS1MwOAf1ng9BifxKM4BgDc1+vqFVmiNTyuL/K61VlIB/GR9vZAKFiVUJbl5vj9fNguGltHkTsD6c2o73Wt4wi+hLpnIFujXM1WvY6DPI2eLk8FALPJIFewOjl/HmTz6bBdp1EZozJGS9I9AzJGC8KNUZlCMoVK0k4DulHOxB9pF1OIa2Dgz0s+H6aRSTxg8ZZSm3AJJx6w6AHTzU3gen9B8J03WTWoUUoAbxMAAAAASUVORK5CYII="),
        }
        paths = {}
        for emoji, (filename, encoded) in icons.items():
            path = os.path.join(icon_dir, filename)
            if not os.path.exists(path):
                with open(path, "wb") as icon_file:
                    icon_file.write(base64.b64decode(encoded))
            paths[emoji] = path
        return paths

    def _download_reply_emoji_assets(self, text, paths):
        """Download/cache Twemoji PNGs for common emoji without relying on device fonts."""
        import urllib.request

        if not paths:
            return
        icon_dir = os.path.dirname(next(iter(paths.values())))
        emoji_pattern = re.compile(
            r"[\U0001F1E6-\U0001F1FF]{2}|"
            r"[\U0001F300-\U0001FAFF][\uFE0F\u200D\U0001F3FB-\U0001F3FF]*"
            r"(?:[\u200D][\U0001F300-\U0001FAFF][\uFE0F\u200D\U0001F3FB-\U0001F3FF]*)*|"
            r"[\u2600-\u27BF][\uFE0F]?"
        )
        # Avoid a long pause if a response contains a huge number of unusual symbols.
        detected = list(dict.fromkeys(emoji_pattern.findall(str(text))))[:24]
        for emoji in detected:
            if emoji in paths:
                continue
            codepoints = "-".join(
                format(ord(char), "x")
                for char in emoji
                if char != "\ufe0f"
            )
            if not codepoints:
                continue
            filename = "twemoji_" + codepoints.replace("-", "_") + ".png"
            path = os.path.join(icon_dir, filename)
            if not os.path.exists(path):
                url = (
                    "https://cdn.jsdelivr.net/gh/jdecked/twemoji@17.0.3/"
                    "assets/72x72/" + codepoints + ".png"
                )
                try:
                    request = urllib.request.Request(
                        url,
                        headers={"User-Agent": "WalletCore-MyAI/1.0"}
                    )
                    ssl_context = ssl.create_default_context(cafile=certifi.where())
                    with urllib.request.urlopen(
                        request,
                        timeout=2,
                        context=ssl_context
                    ) as response:
                        image_data = response.read(256 * 1024 + 1)
                    if not image_data or len(image_data) > 256 * 1024:
                        continue
                    with open(path, "wb") as image_file:
                        image_file.write(image_data)
                except Exception:
                    # Retry the stable upstream Twemoji package if the primary CDN fails.
                    try:
                        fallback_url = (
                            "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/"
                            "assets/72x72/" + codepoints + ".png"
                        )
                        request = urllib.request.Request(
                            fallback_url,
                            headers={"User-Agent": "WalletCore-MyAI/1.0"}
                        )
                        ssl_context = ssl.create_default_context(cafile=certifi.where())
                        with urllib.request.urlopen(
                            request,
                            timeout=2,
                            context=ssl_context
                        ) as response:
                            image_data = response.read(256 * 1024 + 1)
                        if not image_data or len(image_data) > 256 * 1024:
                            continue
                        with open(path, "wb") as image_file:
                            image_file.write(image_data)
                    except Exception:
                        continue
            if os.path.exists(path):
                paths[emoji] = path

    def _load_cached_reply_emoji_assets(self, text, paths):
        """Reconnect cached Twemoji files to their Unicode tokens when history is reopened."""
        if not paths:
            return
        icon_dir = os.path.dirname(next(iter(paths.values())))
        emoji_pattern = re.compile(
            r"[\U0001F1E6-\U0001F1FF]{2}|"
            r"[\U0001F300-\U0001FAFF][\uFE0F\u200D\U0001F3FB-\U0001F3FF]*"
            r"(?:[\u200D][\U0001F300-\U0001FAFF][\uFE0F\u200D\U0001F3FB-\U0001F3FF]*)*|"
            r"[\u2600-\u27BF][\uFE0F]?"
        )
        for emoji in dict.fromkeys(emoji_pattern.findall(str(text))):
            if emoji in paths:
                continue
            codepoints = "-".join(
                format(ord(char), "x") for char in emoji if char != "\ufe0f"
            )
            if not codepoints:
                continue
            path = os.path.join(
                icon_dir, "twemoji_" + codepoints.replace("-", "_") + ".png"
            )
            if os.path.isfile(path):
                paths[emoji] = path

    def _load_history(self):
        """Load saved chat messages from the app's private local storage."""
        try:
            app = App.get_running_app()
            history_path = os.path.join(app.user_data_dir, "my_ai_history.json")
            self.history_store = JsonStore(history_path)
            if self.history_store.exists("conversation"):
                saved = self.history_store.get("conversation").get("messages", [])
                if isinstance(saved, list):
                    self.messages = [
                        {"role": item["role"], "content": item["content"]}
                        for item in saved[-100:]
                        if isinstance(item, dict)
                        and item.get("role") in ("user", "assistant")
                        and isinstance(item.get("content"), str)
                    ]
        except Exception as exc:
            print("My AI history load error:", type(exc).__name__)
            self.messages = []

    def _save_history(self):
        """Persist the conversation locally; no history is sent just by saving."""
        try:
            if self.history_store is not None:
                self.history_store.put("conversation", messages=self.messages[-100:])
        except Exception as exc:
            print("My AI history save error:", type(exc).__name__)

    def open(self):
        self._load_history()
        emoji_paths = self._prepare_emoji_assets()
        # Saved assistant replies must reconnect to cached PNGs on every popup open.
        # This is local-only and never performs network requests on the UI thread.
        cached_reply_text = "\\n".join(
            item["content"]
            for item in self.messages
            if item.get("role") == "assistant"
        )
        self._load_cached_reply_emoji_assets(cached_reply_text, emoji_paths)
        previous_softinput_mode = Window.softinput_mode
        Window.softinput_mode = "below_target"

        root = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=[dp(12), dp(12), dp(12), dp(10)]
        )
        with root.canvas.before:
            Color(0.035, 0.055, 0.085, 1)
            root.background_shape = RoundedRectangle(
                pos=root.pos, size=root.size, radius=[dp(22)]
            )
        root.bind(
            pos=lambda widget, *_: setattr(widget.background_shape, "pos", widget.pos),
            size=lambda widget, *_: setattr(widget.background_shape, "size", widget.size)
        )

        top = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(58),
            spacing=dp(10),
            padding=[dp(4), dp(2), dp(2), dp(2)]
        )
        title_stack = BoxLayout(orientation="vertical", spacing=dp(1))
        title = Label(
            text="[b]My AI[/b]",
            markup=True,
            bold=True,
            font_size="25sp",
            color=(0.96, 0.98, 1, 1),
            halign="left",
            valign="middle",
            size_hint_y=0.65
        )
        title.bind(size=lambda widget, size: setattr(widget, "text_size", size))
        subtitle = Label(
            text=translations[App.get_running_app().language]["ai_subtitle"],
            font_size="13sp",
            color=(0.55, 0.72, 0.88, 1),
            halign="left",
            valign="middle",
            size_hint_y=0.35
        )
        subtitle.bind(size=lambda widget, size: setattr(widget, "text_size", size))
        title_stack.add_widget(title)
        title_stack.add_widget(subtitle)

        new_chat = Button(
            text=translations[App.get_running_app().language]["new_chat"],
            size_hint=(None, None),
            size=(dp(112), dp(36)),
            background_normal="",
            background_down="",
            background_color=(0.12, 0.22, 0.34, 1),
            color=(0.88, 0.94, 1, 1),
            font_size="12sp",
            bold=True
        )
        with new_chat.canvas.before:
            Color(0.12, 0.22, 0.34, 1)
            new_chat.bg_shape = RoundedRectangle(
                pos=new_chat.pos, size=new_chat.size, radius=[dp(12)]
            )
        new_chat.bind(
            pos=lambda widget, *_: setattr(widget.bg_shape, "pos", widget.pos),
            size=lambda widget, *_: setattr(widget.bg_shape, "size", widget.size)
        )
        top.add_widget(title_stack)
        top.add_widget(new_chat)
        root.add_widget(top)

        scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(3),
            scroll_type=["bars", "content"],
            bar_color=(0.20, 0.55, 0.88, 0.85),
            bar_inactive_color=(0.20, 0.55, 0.88, 0.25)
        )
        chat = BoxLayout(
            orientation="vertical",
            spacing=dp(14),
            padding=[dp(6), dp(12), dp(6), dp(12)],
            size_hint_y=None
        )
        chat.bind(minimum_height=chat.setter("height"))
        scroll.add_widget(chat)
        root.add_widget(scroll)

        entry_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(56),
            spacing=dp(9),
            padding=[dp(2), dp(2), dp(2), dp(2)]
        )
        entry_surface = BoxLayout(
            orientation="vertical",
            padding=[dp(2), dp(2), dp(2), dp(2)]
        )
        with entry_surface.canvas.before:
            Color(0.10, 0.14, 0.20, 1)
            entry_surface.bg_shape = RoundedRectangle(
                pos=entry_surface.pos, size=entry_surface.size, radius=[dp(16)]
            )
        entry_surface.bind(
            pos=lambda widget, *_: setattr(widget.bg_shape, "pos", widget.pos),
            size=lambda widget, *_: setattr(widget.bg_shape, "size", widget.size)
        )
        entry = TextInput(
            hint_text=translations[App.get_running_app().language]["write_message"],
            multiline=False,
            size_hint=(1, 1),
            padding=[dp(13), dp(15), dp(13), dp(10)],
            background_normal="",
            background_active="",
            background_color=(0, 0, 0, 0),
            foreground_color=(0.95, 0.97, 1, 1),
            hint_text_color=(0.52, 0.60, 0.70, 1),
            cursor_color=(0.25, 0.70, 1, 1),
            selection_color=(0.13, 0.39, 0.65, 0.8),
            font_size="18sp"
        )
        entry_surface.add_widget(entry)
        send = Button(
            text=translations[App.get_running_app().language]["send"],
            size_hint=(None, None),
            size=(dp(92), dp(48)),
            background_normal="",
            background_down="",
            background_color=(0.10, 0.42, 0.78, 1),
            color=(1, 1, 1, 1),
            font_size="16sp",
            bold=True
        )
        with send.canvas.before:
            Color(0.10, 0.42, 0.78, 1)
            send.bg_shape = RoundedRectangle(
                pos=send.pos, size=send.size, radius=[dp(15)]
            )
        send.bind(
            pos=lambda widget, *_: setattr(widget.bg_shape, "pos", widget.pos),
            size=lambda widget, *_: setattr(widget.bg_shape, "size", widget.size)
        )
        entry_row.add_widget(entry_surface)
        entry_row.add_widget(send)
        root.add_widget(entry_row)

        popup = Popup(
            title="",
            content=root,
            size_hint=(0.96, 0.90),
            separator_height=0,
            background="",
            background_color=(0.035, 0.055, 0.085, 1),
            auto_dismiss=True
        )
        popup.bind(on_dismiss=lambda *_: setattr(Window, "softinput_mode", previous_softinput_mode))

        def keep_input_visible(*_):
            if entry.focus:
                Window.softinput_mode = "below_target"
                Clock.schedule_once(lambda *_: setattr(scroll, "scroll_y", 0), 0.12)

        entry.bind(focus=lambda *_: keep_input_visible())

        request_state = {"generation": 0, "busy": False}

        def add_message(text, sender):
            is_user = sender == "Ti"
            row = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                spacing=dp(4),
                padding=[dp(2), dp(1), dp(2), dp(1)]
            )
            bubble = BoxLayout(
                orientation="vertical",
                size_hint=(None, None),
                width=dp(280),
                padding=[dp(14), dp(14), dp(14), dp(14)]
            )
            bubble.bind(minimum_height=bubble.setter("height"))
            bubble_color = (
                (0.08, 0.30, 0.53, 1)
                if is_user
                else (0.105, 0.14, 0.20, 1)
            )
            with bubble.canvas.before:
                Color(*bubble_color)
                bubble.bg = RoundedRectangle(
                    pos=bubble.pos,
                    size=bubble.size,
                    radius=[dp(15)]
                )
            bubble.bind(
                pos=lambda widget, *_: setattr(widget.bg, "pos", widget.pos),
                size=lambda widget, *_: setattr(widget.bg, "size", widget.size)
            )

            display_text = str(text)
            if not is_user:
                # Recover old broken [img=...] strings from saved conversations.
                display_text = re.sub(
                    r"(?:\[|&bl;)img=.*?\.png(?:\]|&br;)",
                    "",
                    display_text,
                    flags=re.IGNORECASE
                )
                display_text = display_text.replace("&bl;", "[").replace("&br;", "]")

            # Split the response into text and emoji pieces so images remain inline.
            # Keep Markdown formatting on text pieces and don't strip surrounding words.
            emoji_tokens = sorted(emoji_paths.keys(), key=len, reverse=True)
            pieces = []
            if not is_user and emoji_tokens:
                token_pattern = re.compile(
                    "|".join(re.escape(token) for token in emoji_tokens)
                )
                last = 0
                for match in token_pattern.finditer(display_text):
                    if match.start() > last:
                        pieces.append(("text", display_text[last:match.start()]))
                    pieces.append(("emoji", match.group(0)))
                    last = match.end()
                if last < len(display_text):
                    pieces.append(("text", display_text[last:]))
                if not pieces:
                    pieces = [("text", display_text)]
            else:
                pieces = [("text", display_text)]

            # Convert a safe subset of Markdown to Kivy markup in text fragments.
            for kind, value in pieces:
                if kind == "emoji" and value in emoji_paths:
                    icon = Image(
                        source=emoji_paths[value],
                        size_hint=(None, None),
                        size=(dp(23), dp(23)),
                        allow_stretch=True,
                        keep_ratio=True
                    )
                    bubble.add_widget(icon)
                    continue

                label_text = value
                label_markup = False
                if not is_user:
                    label_text = (
                        label_text
                        .replace("&", "&amp;")
                        .replace("[", "&bl;")
                        .replace("]", "&br;")
                    )
                    label_text = re.sub(
                        r"(?m)^\s{0,3}#{1,3}\s+(.+)$",
                        r"[b]\1[/b]",
                        label_text
                    )
                    label_text = re.sub(
                        r"\*\*(.+?)\*\*",
                        r"[b]\1[/b]",
                        label_text
                    )
                    label_text = re.sub(
                        r"(?<!\*)\*([^*\n]+)\*(?!\*)",
                        r"[i]\1[/i]",
                        label_text
                    )
                    label_text = re.sub(
                        r"(?m)^\s*[-*]\s+",
                        "• ",
                        label_text
                    )
                    label_markup = True

                label = Label(
                    text=label_text,
                    size_hint_y=None,
                    halign="left",
                    valign="middle",
                    color=(0.96, 0.98, 1, 1),
                    font_size="17sp",
                    markup=label_markup
                )
                label.bind(
                    width=lambda widget, width: setattr(
                        widget, "text_size", (max(width - dp(2), dp(20)), None)
                    ),
                    texture_size=lambda widget, size: setattr(
                        widget, "height", size[1] + dp(2)
                    )
                )
                bubble.add_widget(label)

            if is_user:
                row.add_widget(Widget(size_hint_x=1))
                row.add_widget(bubble)
            else:
                row.add_widget(bubble)
                row.add_widget(Widget(size_hint_x=1))
            row.bind(
                width=lambda widget, width: setattr(
                    bubble, "width", min(width * 0.88, dp(420))
                ),
                minimum_height=row.setter("height")
            )
            for child in bubble.children:
                if isinstance(child, Label):
                    bubble.bind(
                        width=lambda widget, *_args, target=child: setattr(
                            target, "width", widget.width - dp(24)
                        )
                    )
            chat.add_widget(row)
            Clock.schedule_once(lambda *_: setattr(scroll, "scroll_y", 0), 0.10)
            return row

        def set_busy(busy):
            request_state["busy"] = busy
            send.disabled = busy
            entry.disabled = busy
            send.text = "..." if busy else translations.get(App.get_running_app().language, {}).get("send", "Send")
            send.background_color = (
                (0.16, 0.25, 0.35, 1) if busy else (0.10, 0.42, 0.78, 1)
            )
            entry_surface.opacity = 0.72 if busy else 1.0

        def confirm_wallet_action(action, english_reply=False):
            def localized(sr, en):
                return en if english_reply else sr

            action_kind = action.get("action")
            if action_kind not in ("add", "update", "delete"):
                if action.get("type") in ("income", "expense"):
                    action_kind = "add"
                else:
                    add_message("Predlog nije prepoznat. Ništa nije promenjeno.", "My AI")
                    return

            action_type = action.get("type")
            amount = action.get("amount")
            category = action.get("category")
            note = action.get("note", "")
            transaction_id = action.get("transaction_id")

            if action_kind in ("add", "update"):
                if (
                    action_type not in ("income", "expense")
                    or isinstance(amount, bool)
                    or not isinstance(amount, (int, float))
                    or amount <= 0
                    or amount > 1000000000
                    or not isinstance(category, str)
                    or not category.strip()
                    or len(category.strip()) > 60
                    or not isinstance(note, str)
                    or len(note) > 300
                ):
                    add_message("Predlog nije ispravan. Ništa nije promenjeno.", "My AI")
                    return

            if action_kind in ("update", "delete"):
                if isinstance(transaction_id, bool) or not isinstance(transaction_id, int) or transaction_id <= 0:
                    add_message("Nisam pouzdano identifikovao transakciju. Navedi iznos, kategoriju ili datum. Ništa nije promenjeno.", "My AI")
                    return
                lookup_db = None
                try:
                    from database import Database
                    lookup_db = Database()
                    existing = lookup_db.get_transaction(transaction_id)
                except Exception:
                    existing = None
                finally:
                    if lookup_db is not None:
                        try:
                            lookup_db.close()
                        except Exception:
                            pass
                if not existing:
                    add_message("Ta transakcija više ne postoji ili nije pronađena. Ništa nije promenjeno.", "My AI")
                    return
            else:
                existing = None

            currency = getattr(App.get_running_app(), "currency", "RSD")
            content = BoxLayout(
                orientation="vertical",
                spacing=dp(7),
                padding=dp(12)
            )

            if action_kind == "add":
                title_text = localized(translations.get(App.get_running_app().language, {}).get("confirm_new_transaction", "Confirm new transaction"), "Confirm new transaction")
                kind_label = localized("Prihod", "Income") if action_type == "income" else localized("Trošak", "Expense")
                details = [
                    "{}: {:,.2f} {}".format(kind_label, float(amount), currency).replace(",", " "),
                    localized("Kategorija: {}", "Category: {}").format(category.strip()),
                    localized("Napomena: {}", "Note: {}").format(note.strip() or "—")
                ]
            elif action_kind == "update":
                title_text = localized(translations.get(App.get_running_app().language, {}).get("confirm_edit_transaction", "Edit transaction"), "Edit transaction")
                old_kind = "Prihod" if existing[2] == "income" else "Trošak"
                new_kind = "Prihod" if action_type == "income" else "Trošak"
                details = [
                    "Postojeće: #{} · {} · {:,.2f} {}".format(transaction_id, old_kind, float(existing[1] or 0), currency).replace(",", " "),
                    "Kategorija: {}".format(str(existing[3] or "Ostalo")),
                    "Nova vrednost: {} · {:,.2f} {}".format(new_kind, float(amount), currency).replace(",", " "),
                    "Nova kategorija: {}".format(category.strip()),
                    "Nova napomena: {}".format(note.strip() or "—")
                ]
            else:
                title_text = localized(translations.get(App.get_running_app().language, {}).get("confirm_delete_transaction", "Delete transaction"), "Delete transaction")
                old_kind = "Prihod" if existing[2] == "income" else "Trošak"
                details = [
                    "Transakcija #{}".format(transaction_id),
                    "{}: {:,.2f} {}".format(old_kind, float(existing[1] or 0), currency).replace(",", " "),
                    "Kategorija: {}".format(str(existing[3] or "Ostalo")),
                    "Napomena: {}".format(str(existing[4] or "—")),
                    "Datum: {}".format(str(existing[5] or "nepoznat"))
                ]

            for detail in details:
                content.add_widget(Label(
                    text=detail,
                    size_hint_y=None,
                    height=dp(34),
                    halign="left",
                    valign="middle"
                ))

            content.add_widget(Label(
                text=translations.get(App.get_running_app().language, {}).get("confirm_action_hint", "Review the details and confirm before saving."),
                size_hint_y=None,
                height=dp(38)
            ))
            actions = BoxLayout(
                orientation="horizontal",
                spacing=dp(8),
                size_hint_y=None,
                height=dp(44)
            )
            confirm_label = localized("Potvrdi brisanje", "Confirm deletion") if action_kind == "delete" else (localized("Sačuvaj izmenu", "Save changes") if action_kind == "update" else localized("Potvrdi unos", "Confirm entry"))
            confirm = Button(text=confirm_label)
            cancel = Button(text=translations.get(App.get_running_app().language, {}).get("cancel", "Cancel"))
            actions.add_widget(confirm)
            actions.add_widget(cancel)
            content.add_widget(actions)
            dialog = Popup(
                title=title_text,
                content=content,
                size_hint=(0.92, None),
                height=dp(min(410, 190 + 42 * len(details))),
                auto_dismiss=False
            )

            def cancel_proposal(*_):
                dialog.dismiss()
                add_message(localized("Radnja je otkazana. Podaci nisu promenjeni.", "Action cancelled. No data was changed."), "My AI")

            def save_proposal(*_):
                confirm.disabled = True
                cancel.disabled = True
                db = None
                try:
                    from database import Database
                    db = Database()
                    if action_kind == "add":
                        db.add_ai_transaction(amount, action_type, category, note)
                        result = localized("{} od {:,.2f} {} je upisan. Kategorija: {}.", "{} of {:,.2f} {} was saved. Category: {}.").format(
                            kind_label, float(amount), currency, category.strip()
                        ).replace(",", " ")
                    elif action_kind == "update":
                        current = db.get_transaction(transaction_id)
                        if not current:
                            raise ValueError("Transakcija više ne postoji")
                        db.update_transaction(transaction_id, float(amount), action_type, category.strip(), note.strip())
                        result = localized("Transakcija #{} je izmenjena i sačuvana.", "Transaction #{} was updated and saved.").format(transaction_id)
                    else:
                        current = db.get_transaction(transaction_id)
                        if not current:
                            raise ValueError("Transakcija više ne postoji")
                        db.delete_transaction(transaction_id)
                        result = localized("Transakcija #{} je obrisana.", "Transaction #{} was deleted.").format(transaction_id)

                    app = App.get_running_app()
                    if app is not None and app.root is not None:
                        try:
                            app.root.get_screen("home").load_transactions()
                        except Exception:
                            pass
                        try:
                            history = app.root.get_screen("history")
                            history.load_history(getattr(history, "search", None).text if getattr(history, "search", None) else "")
                        except Exception:
                            pass
                except Exception as exc:
                    result = localized("Radnja nije uspela ({}). Proveri istoriju transakcija.", "The action failed ({}). Check transaction history.").format(type(exc).__name__)
                finally:
                    if db is not None:
                        try:
                            db.close()
                        except Exception:
                            pass
                dialog.dismiss()
                add_message(result, "My AI")

            confirm.bind(on_release=save_proposal)
            cancel.bind(on_release=cancel_proposal)
            dialog.open()

        def send_message(*_):
            user_text = entry.text.strip()
            if not user_text or request_state["busy"]:
                return

            if not AI_API_URL.strip():
                add_message(
                    "AI servis još nije podešen. Potrebno je postaviti backend "
                    "i upisati njegov URL u components/my_ai_config.py.",
                    "My AI"
                )
                return

            entry.text = ""
            add_message(user_text, "Ti")

            request_messages = list(self.messages[-40:])
            request_messages.append({"role": "user", "content": user_text})
            wallet_context = self._get_wallet_context()
            latest_text = str(user_text or "")
            english_reply = bool(re.search(r"\b(english|answer|reply|speak|in english|income|expense|earned|spent|paid|bought|fuel|groceries|lunch|today|yesterday|please|thanks|hello|hi|how much|what is|show me|add|update|delete)\b", latest_text.lower()))

            def localized(sr, en):
                return en if english_reply else sr

            generation = request_state["generation"]
            set_busy(True)
            waiting_bubble = add_message("Pripremam odgovor...", "My AI")

            def do_request():
                answer = None
                error_text = None
                try:
                    payload = json.dumps(
                        {
                            "messages": request_messages,
                            "wallet_context": wallet_context,
                            "response_language": "English" if english_reply else "Serbian"
                        },
                        ensure_ascii=False
                    ).encode("utf-8")
                    request = urllib.request.Request(
                        AI_API_URL.strip(),
                        data=payload,
                        headers={
                            "Content-Type": "application/json",
                            "Accept": "application/json",
                            "User-Agent": "WalletCore-MyAI/1.0",
                        },
                        method="POST"
                    )
                    ssl_context = ssl.create_default_context(cafile=certifi.where())
                    with urllib.request.urlopen(
                        request,
                        timeout=45,
                        context=ssl_context
                    ) as response:
                        data = json.loads(response.read().decode("utf-8"))

                    answer = data.get("reply")
                    if not isinstance(answer, str) or not answer.strip():
                        error_text = data.get(
                            "error",
                            "AI servis nije vratio odgovor."
                        )
                    else:
                        answer = answer.strip()
                except urllib.error.HTTPError as exc:
                    try:
                        details = exc.read().decode("utf-8", errors="replace").strip()
                        try:
                            data = json.loads(details)
                        except Exception:
                            data = None

                        if isinstance(data, dict):
                            api_error = data.get("error")
                            if isinstance(api_error, dict):
                                api_error = api_error.get("message") or str(api_error)
                            if isinstance(api_error, str) and api_error.strip():
                                error_text = "HTTP {}: {}".format(
                                    exc.code,
                                    api_error.strip()[:300]
                                )
                            elif details:
                                error_text = "HTTP {}: {}".format(
                                    exc.code,
                                    details[:300]
                                )
                            else:
                                error_text = translations[App.get_running_app().language]["ai_service_http_error"].format(
                                    exc.code
                                )
                        elif details:
                            error_text = "HTTP {}: {}".format(
                                exc.code,
                                details[:300]
                            )
                        else:
                            error_text = "AI servis je vratio HTTP grešku {}.".format(
                                exc.code
                            )
                    except Exception as detail_exc:
                        error_text = "HTTP {} ({}).".format(
                            exc.code,
                            type(detail_exc).__name__
                        )
                except Exception as exc:
                    # Diagnostic text helps identify network/TLS/timeout issues.
                    error_text = translations[App.get_running_app().language]["ai_connection_error"].format(
                        type(exc).__name__,
                        str(exc)[:180] or "bez dodatnih detalja"
                    )

                if answer:
                    try:
                        self._download_reply_emoji_assets(answer, emoji_paths)
                    except Exception:
                        pass

                def finish_request(*_):
                    if generation != request_state["generation"]:
                        return
                    if waiting_bubble.parent is chat:
                        chat.remove_widget(waiting_bubble)
                    set_busy(False)

                    if answer:
                        self.messages.append({"role": "user", "content": user_text})
                        if answer.startswith("WALLET_ACTION:"):
                            try:
                                action = json.loads(answer[len("WALLET_ACTION:"):].strip())
                                if not isinstance(action, dict):
                                    raise ValueError("invalid proposal")
                                # Normalize common model output variations before strict validation.
                                action["action"] = str(action.get("action", "")).strip().lower()
                                action["type"] = str(action.get("type", "")).strip().lower()
                                raw_amount = action.get("amount")
                                if isinstance(raw_amount, str):
                                    cleaned_amount = raw_amount.strip().replace(" ", "").replace(",", ".")
                                    action["amount"] = float(cleaned_amount) if cleaned_amount else None
                                if action.get("category") is None or not str(action.get("category", "")).strip():
                                    action["category"] = "Ostalo"
                                else:
                                    action["category"] = str(action["category"]).strip()[:60]
                                if action.get("note") is None:
                                    action["note"] = ""
                                elif not isinstance(action.get("note"), str):
                                    action["note"] = str(action["note"])[:300]
                                action_kind = action.get("action")
                                if action_kind not in ("add", "update", "delete"):
                                    if action.get("type") in ("income", "expense"):
                                        action_kind = "add"
                                    else:
                                        raise ValueError("invalid action")
                                if action_kind == "add" and action.get("type") not in ("income", "expense"):
                                    raise ValueError("invalid add proposal")
                                if action_kind in ("update", "delete") and (
                                    isinstance(action.get("transaction_id"), bool)
                                    or not isinstance(action.get("transaction_id"), int)
                                    or action.get("transaction_id") <= 0
                                ):
                                    raise ValueError("invalid transaction id")
                                summary = localized("Predlog radnje je spreman. Proveri detalje i potvrdi u prozoru.", "The action proposal is ready. Review the details and confirm in the dialog.")
                                self.messages.append({"role": "assistant", "content": summary})
                                self.messages = self.messages[-100:]
                                self._save_history()
                                add_message(summary, "My AI")
                                confirm_wallet_action(action, english_reply)
                            except Exception as proposal_exc:
                                proposal_error = localized(
                                    "Predlog nije mogao da se obradi ({}: {}). Ništa nije upisano.",
                                    "The proposal could not be processed ({}: {}). Nothing was saved."
                                ).format(type(proposal_exc).__name__, str(proposal_exc).strip()[:120] or "no details")
                                self.messages.append({"role": "assistant", "content": proposal_error})
                                self.messages = self.messages[-100:]
                                self._save_history()
                                add_message(proposal_error, "My AI")
                        else:
                            self.messages.append({"role": "assistant", "content": answer})
                            self.messages = self.messages[-100:]
                            self._save_history()
                            add_message(answer, "My AI")
                    else:
                        add_message(error_text or "Došlo je do greške.", "My AI")

                def guarded_finish_request(*_):
                    try:
                        finish_request()
                    except BaseException as exc:
                        try:
                            import traceback
                            app = App.get_running_app()
                            log_path = os.path.join(
                                app.user_data_dir,
                                "my_ai_crash.txt"
                            )
                            with open(log_path, "a", encoding="utf-8") as log:
                                log.write(
                                    "\n--- My AI UI callback error ---\n"
                                    + traceback.format_exc()
                                    + "\n"
                                )
                        except Exception:
                            pass
                        try:
                            if waiting_bubble.parent is chat:
                                chat.remove_widget(waiting_bubble)
                            set_busy(False)
                            add_message(
                                "Greška pri prikazu odgovora ({}): {}. "
                                "Ponovo otvori My AI.".format(type(exc).__name__, str(exc).strip()[:180] or "bez dodatnih detalja"),
                                "My AI"
                            )
                        except Exception:
                            pass

                Clock.schedule_once(guarded_finish_request, 0)

            threading.Thread(target=do_request, daemon=True).start()

        def reset_chat(*_):
            request_state["generation"] += 1
            request_state["busy"] = False
            self.messages = []
            self._save_history()
            chat.clear_widgets()
            set_busy(False)
            add_message("Novi razgovor. Ja sam My AI.", "My AI")

        send.bind(on_release=send_message)
        entry.bind(on_text_validate=send_message)
        new_chat.bind(on_release=reset_chat)
        popup.bind(on_open=lambda *_: Clock.schedule_once(lambda __: setattr(scroll, "scroll_y", 0), 0.15))

        if self.messages:
            for saved_message in self.messages:
                sender = "Ti" if saved_message["role"] == "user" else "My AI"
                add_message(saved_message["content"], sender)
        else:
            add_message(
                "Zdravo! Ja sam My AI, tvoj finansijski asistent. Mogu da analiziram prihode i troškove ili da pripremim unos za tvoju potvrdu.",
                "My AI"
            )
        popup.open()
