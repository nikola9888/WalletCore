from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle, Line

from theme import CARD, RADIUS


class ModernCard(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:

            # SENKA ISPOD KARTICE
            Color(0, 0, 0, 0.22)
            self.shadow = RoundedRectangle(
                radius=[RADIUS]
            )

            # GLAVNA KARTICA
            Color(*CARD)
            self.bg = RoundedRectangle(
                radius=[RADIUS]
            )

            # TANAK STAKLASTI OKVIR
            Color(1, 1, 1, 0.18)
            self.border = Line(
                rounded_rectangle=(0, 0, 0, 0, RADIUS),
                width=1.5
            )


        self.bind(
            pos=self.update_bg,
            size=self.update_bg
        )


    def update_bg(self, *args):

        # senka malo niže
        self.shadow.pos = (
            self.x,
            self.y - 5
        )

        self.shadow.size = self.size


        # kartica
        self.bg.pos = self.pos
        self.bg.size = self.size


        # okvir
        self.border.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            RADIUS
        )