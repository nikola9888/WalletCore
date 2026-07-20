from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

from theme import TEXT, TITLE


class AboutScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


        root = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=20
        )


        title = Label(
            text="WalletCore",
            color=TEXT,
            font_size=TITLE,
            bold=True,
            size_hint_y=None,
            height=80
        )


        info = Label(
            text=(
                "WalletCore\n\n"
                "Smart personal finance manager.\n\n"
                "Track income, expenses and budgets "
                "in one simple application.\n\n"
                "Version 1.0\n\n"
                "Developed by DEVELOPMENT4WORLD"
                "E-mail: development4world@gmail.com"
            ),
            font_size="26sp",
            color=TEXT,
            size_hint_y= None,
            height=600,
            halign="center",
            valign="middle"
        )

        info.bind(
            size=lambda x, y: setattr(x, "text_size", x.size)
        )

        back.bind(
            on_press=self.go_back
        )


        root.add_widget(title)
        root.add_widget(info)
        root.add_widget(back)


        self.add_widget(root)



    def go_back(self, instance):

        self.manager.current = "settings"
