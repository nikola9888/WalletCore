from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.app import App
from translations import translations
from theme import TEXT, TITLE, CARD, RADIUS


class IconButton(ButtonBehavior, Image):
    pass



class Header(BoxLayout):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.current_language = App.get_running_app().language

        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(75)

        self.padding = (
            dp(20),
            dp(8)
        )

        self.spacing = dp(15)


        # HEADER POZADINA
        with self.canvas.before:
            Color(*CARD)

            self.bg = RoundedRectangle(
                radius=[RADIUS]
            )

        self.bind(
            pos=self.update_bg,
            size=self.update_bg
        )


        # LEVA MENU IKONA
        self.menu_button = IconButton(
            source="assets/icons/menu.png",
            size_hint=(None, None),
            size=(dp(30), dp(30))
        )

        self.menu_button.bind(
            on_release=self.open_menu
        )


        # NASLOV
        self.title = Label(
            text=translations[self.current_language]["app_name"],
            color=TEXT,
            bold=True,
            font_size=TITLE,
            halign="left",
            valign="middle"
        )

        self.title.bind(
            size=lambda x, y: setattr(
                x,
                "text_size",
                x.size
            )
        )


        # HISTORY IKONA
        self.history = IconTextButton(
            icon="assets/icons/history.png",
            text=translations[self.current_language]["history"]
        )

        self.history.bind(
            on_release=self.open_history
        )


        # DODAVANJE U HEADER
        self.add_widget(self.menu_button)
        self.add_widget(self.title)

        self.add_widget(
            Widget(size_hint_x=1)
        )


        self.add_widget(self.history)

    def update_bg(self, *args):

        self.bg.pos = self.pos
        self.bg.size = self.size



    def open_settings(self, *args):

        app = App.get_running_app()

        if app.root:

            try:
                app.root.current = "settings"

            except Exception as e:
                print("Settings error:", e)

    def open_history(self, *args):
        App.get_running_app().root.current = "history"

    def open_menu(self, *args):

        print("MENU CLICKED")



    def update_language(self):

        t = translations[
            App.get_running_app().language
        ]

        self.title.text = t["app_name"]

        self.history.label.text = t["history"]
        
class IconTextButton(ButtonBehavior, BoxLayout):

    def __init__(self, icon, text, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "horizontal"
        self.spacing = dp( 8)
        self.size_hint = (None, None)
        self.size = (dp(70),dp(30))

        self.add_widget(
            Image(
                source=icon,
                size_hint=(None, None),
                size=(dp(30), dp(30))
            )
        )

        self.label = Label(
            text=text,
            color=TEXT,
            font_size=30,
            bold=True
        )

        self.add_widget(self.label)
