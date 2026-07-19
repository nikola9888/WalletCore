from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle

from components.card import ModernCard
from theme import TEXT, TEXT_SECONDARY, PRIMARY
from kivy.app import App
from translations import translations


class BalanceCard(ModernCard):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.padding = (28, 24)
        self.spacing = 14

        self.size_hint_y = None
        self.height = 220


        self.current_language = App.get_running_app().language
        t = translations[self.current_language]


        # NASLOV
        self.title = Label(
            text=translations[App.get_running_app().language]["current_balance"],
            color=TEXT_SECONDARY,
            font_size=22,
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


        # GLAVNI BALANS
        self.balance = Label(
            text="0.00 RSD",
            color=TEXT,
            bold=True,
            font_size=42,
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
            font_size=26
        )


        # TROŠAK
        self.expense = Label(
            text="0.00",
            color=(0.9, 0.3, 0.3, 1),
            font_size=26
        )


        # RED SA PRIHODOM I TROŠKOM
        stats_row = BoxLayout(
            orientation="horizontal",
            spacing=20,
            size_hint_y=None,
            height=25
        )

        stats_row.add_widget(self.income)
        stats_row.add_widget(self.expense)


        # PLAVA LINIJA
        self.line = BoxLayout(
            size_hint_y=None,
            height=6
        )


        with self.line.canvas.before:
            Color(*PRIMARY)

            self.line_bg = RoundedRectangle(
                radius=[20]
            )


        self.line.bind(
            pos=self.update_line,
            size=self.update_line
        )


        # DODAVANJE
        self.add_widget(self.title)
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
