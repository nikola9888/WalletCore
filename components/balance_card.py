from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle

from components.card import ModernCard
from theme import TEXT, TEXT_SECONDARY, PRIMARY
from kivy.app import App
from translations import translations
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.metrics import dp

class IconButton(ButtonBehavior, Image):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # dozvoljava da se ikonica menja po veličini widgeta
        self.allow_stretch = True
        self.keep_ratio = True

        # sigurniji default za dugmad sa ikonom
        self.size_hint = (None, None)
    def update_text(self, text):
        self.label.text = text
class BalanceCard(ModernCard):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.spacing = dp(1)
        self.padding = (dp(10), dp(5))

        self.size_hint_y = None
        self.height = dp(220)


        self.current_language = App.get_running_app().language
        t = translations[self.current_language]


        # NASLOV
        self.title = Label(
            text=translations[App.get_running_app().language]["current_balance"],
            color=TEXT_SECONDARY,
            font_size=dp(16),
            halign="left",
            valign="middle",
            bold=True
        )

        self.title.bind(
            size=lambda x, y: setattr(
                x,
                "text_size",
                x.size
            )
        )

        header_row = FloatLayout(
            size_hint_y=None,
            height=dp(33)
        )

        self.title.size_hint = (1, 1)
        self.title.pos_hint = {
            "x": 0,
            "y": 0
        }

        header_row.add_widget(self.title)


        self.settings = IconButton(
            source="assets/icons/settings.png",
            size_hint=(None, None),
            size=(dp(28), dp(28)),
            allow_stretch=True,
            keep_ratio=True,
            pos_hint={
                "right": 0.98,
                "top": 0.45
            }
        )

        self.settings.bind(
            on_release=self.open_settings
        )

        header_row.add_widget(self.settings)
        # GLAVNI BALANS
        self.balance = Label(
            text="0.00 RSD",
            color=TEXT,
            bold=True,
            font_size=dp(14),
            halign="left",
            valign="middle"
        )

        self.balance.bind(
            size=lambda x, y: setattr(
                x,
                "text_size",
                x.size
            )
        )

        # PRIHOD
        self.income = Label(
            text="0.00",
            color=(0.2, 0.9, 0.5, 1),
            font_size=dp(12)
        )


        # TROŠAK
        self.expense = Label(
            text="0.00",
            color=(0.9, 0.3, 0.3, 1),
            font_size=dp(12)
        )


        # RED SA PRIHODOM I TROŠKOM
        stats_row = BoxLayout(
            orientation="horizontal",
            spacing=dp(20),
            size_hint_y=None,
            height=dp(15)
        )

        stats_row.add_widget(self.income)
        stats_row.add_widget(self.expense)


        # PLAVA LINIJA
        self.line = BoxLayout(
            size_hint_y=None,
            height=dp(3)
        )


        with self.line.canvas.before:
            Color(*PRIMARY)

            self.line_bg = RoundedRectangle(
                radius=[dp(20)]
            )


        self.line.bind(
            pos=self.update_line,
            size=self.update_line
        )


        # DODAVANJE
        self.add_widget(header_row)
        self.balance.size_hint_y = None
        self.balance.height = dp(15)
        self.add_widget(self.balance)
        self.add_widget(stats_row)
        self.add_widget(self.line)



    def update_line(self, *args):

        self.line_bg.pos = self.line.pos
        self.line_bg.size = self.line.size



    def update_language(self):
        from kivy.app import App
        from translations import translations

        t = translations[App.get_running_app().language]
        self.title.text = t["current_balance"]
        
    def open_settings(self, *args):

        App.get_running_app().root.current = "settings"
