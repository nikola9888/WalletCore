import json
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

from components.my_ai_config import AI_API_URL


class MyAIChat:
    """My AI chat popup using a private server-side API proxy."""

    def __init__(self):
        self.messages = []

    def open(self):
        root = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(10)
        )

        top = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(42),
            spacing=dp(8)
        )
        title = Label(
            text="My AI",
            bold=True,
            font_size="20sp",
            halign="left"
        )
        title.bind(size=lambda widget, size: setattr(widget, "text_size", size))

        new_chat = Button(
            text="Novi razgovor",
            size_hint_x=None,
            width=dp(112)
        )
        top.add_widget(title)
        top.add_widget(new_chat)
        root.add_widget(top)

        scroll = ScrollView(do_scroll_x=False)
        chat = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(4),
            size_hint_y=None
        )
        chat.bind(minimum_height=chat.setter("height"))
        scroll.add_widget(chat)
        root.add_widget(scroll)

        entry_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            spacing=dp(8)
        )
        entry = TextInput(
            hint_text="Napiši poruku...",
            multiline=False,
            size_hint_x=1,
            padding=[dp(10), dp(12), dp(10), dp(10)]
        )
        send = Button(
            text="Pošalji",
            size_hint_x=None,
            width=dp(88)
        )
        entry_row.add_widget(entry)
        entry_row.add_widget(send)
        root.add_widget(entry_row)

        popup = Popup(
            title="My AI",
            content=root,
            size_hint=(0.94, 0.86),
            auto_dismiss=True
        )

        request_state = {"generation": 0, "busy": False}

        def add_message(text, sender):
            bubble = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                padding=dp(10)
            )
            bubble.bind(minimum_height=bubble.setter("height"))

            bubble_color = (
                (0.08, 0.24, 0.40, 1)
                if sender == "Ti"
                else (0.10, 0.15, 0.23, 1)
            )
            with bubble.canvas.before:
                Color(*bubble_color)
                bubble.bg = RoundedRectangle(
                    pos=bubble.pos,
                    size=bubble.size,
                    radius=[dp(12)]
                )

            bubble.bind(
                pos=lambda widget, *_: setattr(widget.bg, "pos", widget.pos),
                size=lambda widget, *_: setattr(widget.bg, "size", widget.size)
            )

            label = Label(
                text="{}: {}".format(sender, text),
                size_hint_y=None,
                halign="left",
                valign="middle",
                color=(1, 1, 1, 1),
                font_size="15sp"
            )
            label.bind(
                width=lambda widget, width: setattr(
                    widget,
                    "text_size",
                    (max(width - dp(4), dp(20)), None)
                ),
                texture_size=lambda widget, size: setattr(
                    widget,
                    "height",
                    size[1] + dp(6)
                )
            )
            bubble.add_widget(label)
            chat.add_widget(bubble)
            Clock.schedule_once(lambda *_: setattr(scroll, "scroll_y", 0), 0.08)
            return bubble

        def set_busy(busy):
            request_state["busy"] = busy
            send.disabled = busy
            entry.disabled = busy
            send.text = "..." if busy else "Pošalji"

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

            request_messages = list(self.messages)
            request_messages.append({"role": "user", "content": user_text})
            generation = request_state["generation"]
            set_busy(True)
            waiting_bubble = add_message("Pripremam odgovor...", "My AI")

            def do_request():
                answer = None
                error_text = None
                try:
                    payload = json.dumps(
                        {"messages": request_messages},
                        ensure_ascii=False
                    ).encode("utf-8")
                    request = urllib.request.Request(
                        AI_API_URL.strip(),
                        data=payload,
                        headers={"Content-Type": "application/json"},
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
                        details = exc.read().decode("utf-8")
                        data = json.loads(details)
                        error_text = data.get(
                            "error",
                            "AI servis je vratio HTTP grešku {}.".format(exc.code)
                        )
                    except Exception:
                        error_text = "AI servis je vratio HTTP grešku {}.".format(
                            exc.code
                        )
                except Exception as exc:
                    # Diagnostic text helps identify network/TLS/timeout issues.
                    error_text = "Greška povezivanja ({}): {}".format(
                        type(exc).__name__,
                        str(exc)[:180] or "bez dodatnih detalja"
                    )

                def finish_request(*_):
                    if generation != request_state["generation"]:
                        return
                    if waiting_bubble.parent is chat:
                        chat.remove_widget(waiting_bubble)
                    set_busy(False)

                    if answer:
                        self.messages.append({"role": "user", "content": user_text})
                        self.messages.append({"role": "assistant", "content": answer})
                        add_message(answer, "My AI")
                    else:
                        add_message(error_text or "Došlo je do greške.", "My AI")

                Clock.schedule_once(finish_request, 0)

            threading.Thread(target=do_request, daemon=True).start()

        def reset_chat(*_):
            request_state["generation"] += 1
            request_state["busy"] = False
            self.messages = []
            chat.clear_widgets()
            set_busy(False)
            add_message("Novi razgovor. Ja sam My AI.", "My AI")

        send.bind(on_release=send_message)
        entry.bind(on_text_validate=send_message)
        new_chat.bind(on_release=reset_chat)

        add_message(
            "Zdravo! Ja sam My AI. Pošalji poruku da započnemo razgovor.",
            "My AI"
        )
        popup.open()
