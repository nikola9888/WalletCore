from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.widget import Widget

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
        self.height = 75

        self.padding = (20, 8)
        self.spacing = 15


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
            size=(70, 70)
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


        # DESNA SETTINGS IKONA
        self.settings = IconButton(
            source="assets/icons/settings.png",
            size_hint=(None, None),
            size=(80, 80),
            fit_mode="contain"
        )

        self.settings.bind(
            on_release=self.open_settings
        )
        self.settings.pos_hint = {"center_y": 9.90}


        # HISTORY IKONA
        self.history = IconTextButton(
            icon="assets/icons/history.png",
            text="History"
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
        self.add_widget(self.settings)

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
        
class IconTextButton(ButtonBehavior, BoxLayout):

    def __init__(self, icon, text, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "horizontal"
        self.spacing = 8
        self.size_hint = (None, None)
        self.size = (150, 60)

        self.add_widget(
            Image(
                source=icon,
                size_hint=(None, None),
                size=(75,75)
            )
        )

        self.label = Label(
            text=text,
            color=TEXT,
            font_size=30,
            bold=True
        )

        self.add_widget(self.label)
