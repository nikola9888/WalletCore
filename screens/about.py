from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from components.button import ModernButton
from theme import TEXT, TITLE
from translations import translations


class AboutScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.current_language = App.get_running_app().language

        root = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(12)
        )

        self.title = Label(
            text=translations[self.current_language]["about"],
            color=TEXT,
            font_size=TITLE,
            bold=True,
            size_hint_y=None,
            height=dp(64),
            halign="center",
            valign="middle"
        )

        self.scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(3),
            scroll_type=["bars", "content"]
        )

        self.info = Label(
            text=self.get_about_text(),
            color=TEXT,
            font_size=dp(17),
            size_hint_y=None,
            halign="center",
            valign="top",
            padding=(dp(12), dp(12)),
            line_height=1.2
        )
        self.info.bind(
            width=self._update_text_width,
            texture_size=self._update_text_height
        )

        self.scroll.add_widget(self.info)

        self.back = ModernButton(
            text=translations[self.current_language]["back"],
            size_hint_y=None,
            height=dp(56)
        )
        self.back.bind(on_press=self.go_back)

        root.add_widget(self.title)
        root.add_widget(self.scroll)
        root.add_widget(self.back)
        self.add_widget(root)

        self.bind(on_enter=self.update_language)

    def _update_text_width(self, instance, width):
        instance.text_size = (max(width - dp(24), dp(1)), None)

    def _update_text_height(self, instance, texture_size):
        instance.height = texture_size[1] + dp(24)

    def get_about_text(self):
        t = translations[self.current_language]

        description = t.get(
            "about_description",
            "WalletCore is your personal finance assistant."
        )

        return (
            "WalletCore\n\n"
            f"{description}\n\n"
            f"{t['version']} 1.2.0\n\n"
            f"{t['developed_by'].replace('DEVELOP4WORLD', 'DEVELOP4WORLD')}\n\n"
            "E-mail: development4world@gmail.com"
        )

    def update_language(self, *args):
        self.current_language = App.get_running_app().language
        t = translations[self.current_language]

        self.title.text = t["about"]
        self.info.text = self.get_about_text()
        self.back.text = t["back"]

    def go_back(self, instance):
        self.manager.current = "settings"
