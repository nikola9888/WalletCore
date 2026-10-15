from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Line
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
        self.padding = (dp(20), dp(8))
        self.spacing = dp(15)

        # HEADER POZADINA
        with self.canvas.before:
            Color(*CARD)
            self.bg = RoundedRectangle(radius=[RADIUS])

        self.bind(pos=self.update_bg, size=self.update_bg)

        # MY AI DUGME - na mestu stare menu.png ikonice
        self.menu_button = Button(
            text="My AI",
            size_hint=(None, None),
            size=(dp(66), dp(34)),
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
            color=(0.04, 0.05, 0.07, 1),
            font_size="14sp",
            bold=True
        )

        # Srebrna povrsina je niza za 15%, dok donja ivica ostaje na mestu.
        with self.menu_button.canvas.before:
            Color(0.78, 0.80, 0.83, 1)
            self.menu_button_bg = RoundedRectangle(
                radius=[dp(9)],
                pos=self.menu_button.pos,
                size=(self.menu_button.width, self.menu_button.height * 0.85)
            )
            Color(0.03, 0.12, 0.25, 1)
            self.menu_button_border = Line(
                rounded_rectangle=(
                    self.menu_button.x,
                    self.menu_button.y,
                    self.menu_button.width,
                    self.menu_button.height * 0.85,
                    dp(9)
                ),
                width=dp(1.4)
            )

        self.menu_button.bind(
            pos=self.update_menu_button_style,
            size=self.update_menu_button_style
        )
        self.menu_button.bind(on_release=self.open_menu)

        # NASLOV
        self.title = Label(
            text=translations[self.current_language]["app_name"],
            color=TEXT,
            bold=True,
            font_size=TITLE,
            halign="left",
            valign="middle"
        )
        self.title.bind(size=lambda x, y: setattr(x, "text_size", x.size))

        # HISTORY IKONA
        self.history = IconTextButton(
            icon="assets/icons/history.png",
            text=translations[self.current_language]["history"]
        )
        self.history.bind(on_release=self.open_history)

        # DODAVANJE U HEADER
        self.add_widget(self.menu_button)
        self.add_widget(self.title)
        self.add_widget(Widget(size_hint_x=1))
        self.add_widget(self.history)

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def update_menu_button_style(self, button, *args):
        visible_height = button.height * 0.85
        button_y = button.y
        button_width = button.width
        button_x = button.x

        self.menu_button_bg.pos = (button_x, button_y)
        self.menu_button_bg.size = (button_width, visible_height)
        self.menu_button_border.rounded_rectangle = (
            button_x,
            button_y,
            button_width,
            visible_height,
            dp(9)
        )

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
        try:
            from components.my_ai_chat import MyAIChat
            MyAIChat().open()
        except Exception as e:
            print("My AI open error:", e)

    def update_language(self):
        t = translations[App.get_running_app().language]
        self.title.text = t["app_name"]
        self.history.label.text = t["history"]


class IconTextButton(ButtonBehavior, BoxLayout):

    def __init__(self, icon, text, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.spacing = dp(8)
        self.size_hint = (None, None)
        self.size = (dp(70), dp(30))

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
