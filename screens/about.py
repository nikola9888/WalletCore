from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.app import App

from components.button import ModernButton
from theme import TEXT, TITLE
from translations import translations


class AboutScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.current_language = App.get_running_app().language

        root = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=20
        )


        # TITLE
        self.title = Label(
            text=translations[self.current_language]["about"],
            color=TEXT,
            font_size=TITLE,
            bold=True,
            size_hint_y=None,
            height=80
        )


        # INFO
        self.info = Label(
            text=self.get_about_text(),
            color=TEXT,
            font_size=28
        )


        # BACK
        self.back = ModernButton(
            text=translations[self.current_language]["back"],
            size_hint_y=None,
            height=100
        )

        self.back.bind(
            on_press=self.go_back
        )


        root.add_widget(self.title)
        root.add_widget(self.info)
        root.add_widget(self.back)

        self.add_widget(root)

        self.bind(on_enter=self.update_language)


    def get_about_text(self):

        t = translations[self.current_language]

        return (
            "WalletCore\n\n"
            f"{t['smart_finance_manager']}\n\n"
            f"{t['track_money']}\n\n"
            f"{t['version']} 1.0\n\n"
            f"{t['developed_by']}\n\n"
            "E-mail: development4world@gmail.com"
        )



    def update_language(self ,*args):

        self.current_language = App.get_running_app().language

        t = translations[self.current_language]

        self.title.text = t["about"]
        self.info.text = self.get_about_text()
        self.back.text = t["back"]



    def go_back(self, instance):

        self.manager.current = "settings"
