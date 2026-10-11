from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock


class MyAIChat:
    """WalletCore My AI chat popup. API transport will be connected separately."""

    def __init__(self):
        self.messages = []

    def open(self):
        root = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        top = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(42), spacing=dp(8))
        title = Label(text="My AI", bold=True, font_size="20sp", halign="left")
        title.bind(size=lambda w, s: setattr(w, "text_size", s))
        new_chat = Button(text="New chat", size_hint_x=None, width=dp(95))
        top.add_widget(title)
        top.add_widget(new_chat)
        root.add_widget(top)

        scroll = ScrollView(do_scroll_x=False)
        chat = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(4), size_hint_y=None)
        chat.bind(minimum_height=chat.setter("height"))
        scroll.add_widget(chat)
        root.add_widget(scroll)

        def add_message(text, sender):
            bubble = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(10))
            bubble.bind(minimum_height=bubble.setter("height"))
            with bubble.canvas.before:
                Color(*( (0.08, 0.24, 0.40, 1) if sender == "You" else (0.10, 0.15, 0.23, 1) ))
                bubble.bg = RoundedRectangle(pos=bubble.pos, size=bubble.size, radius=[dp(12)])
            bubble.bind(pos=lambda w, *_: setattr(w.bg, "pos", w.pos),
                        size=lambda w, *_: setattr(w.bg, "size", w.size))
            label = Label(text=f"{sender}: {text}", size_hint_y=None, halign="left", valign="middle",
                          color=(1, 1, 1, 1), font_size="15sp")
            label.bind(width=lambda w, width: setattr(w, "text_size", (max(width - dp(4), dp(20)), None)),
                       texture_size=lambda w, size: setattr(w, "height", size[1] + dp(6)))
            bubble.add_widget(label)
            chat.add_widget(bubble)
            Clock.schedule_once(lambda *_: setattr(scroll, "scroll_y", 0), 0.05)

        add_message("Zdravo! Ja sam My AI. Chat interfejs je spreman; AI servis još nije povezan.", "My AI")

        entry_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48), spacing=dp(8))
        entry = TextInput(hint_text="Napiši poruku...", multiline=False, size_hint_x=1,
                          padding=[dp(10), dp(12), dp(10), dp(10)])
        send = Button(text="Pošalji", size_hint_x=None, width=dp(88))
        entry_row.add_widget(entry)
        entry_row.add_widget(send)
        root.add_widget(entry_row)

        popup = Popup(title="My AI", content=root, size_hint=(0.94, 0.86), auto_dismiss=True)

        def send_message(*_):
            text = entry.text.strip()
            if not text:
                return
            add_message(text, "You")
            entry.text = ""
            add_message("Poruka je prikazana. Za AI odgovor potrebno je povezati servis preko bezbednog API posrednika.", "My AI")

        def reset_chat(*_):
            chat.clear_widgets()
            add_message("Novi razgovor. Ja sam My AI.", "My AI")

        send.bind(on_release=send_message)
        entry.bind(on_text_validate=send_message)
        new_chat.bind(on_release=reset_chat)
        popup.open()
