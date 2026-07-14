from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.animation import Animation
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior

from theme import CATEGORY_BG, PRIMARY


class CategoryButton(ButtonBehavior, BoxLayout):

    def __init__(self, category, title, icon, **kwargs):
        super().__init__(**kwargs)

        self.category_key = category
        self.title = title

        self.orientation = "horizontal"
        self.spacing = 16
        self.padding = (20, 15)


        self.icon = Image(
            source=icon,
            size_hint=(None, None),
            size=(70, 70)
        )


        self.label = Label(
            text=title,
            color=(0.12,0.16,0.22,1),
            font_size=28,
            bold=True,
            halign="left",
            valign="middle"
        )

        self.label.bind(
            size=lambda i,v: setattr(i,"text_size",i.size)
        )


        self.add_widget(self.icon)
        self.add_widget(self.label)


        with self.canvas.before:

            # SENKA
            Color(0,0,0,0.25)

            self.shadow = RoundedRectangle(
                radius=[26]
            )


            # POZADINA KARTICE
            self.bg_color = Color(
                *CATEGORY_BG[category]
            )

            self.rect = RoundedRectangle(
                radius=[26]
            )


            # IVICA
            self.border_color = Color(
                0.20,0.22,0.25,1
            )

            self.border = Line(
                rounded_rectangle=(0,0,0,0,26),
                width=2.5
            )


        self.bind(
            pos=self.update_rect,
            size=self.update_rect
        )


    def update_rect(self,*args):

        self.shadow.pos = (
            self.x,
            self.y-4
        )
        self.shadow.size = self.size


        self.rect.pos = self.pos
        self.rect.size = self.size


        self.border.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            26
        )


    def select(self):

        self.border_color.rgba = PRIMARY

        Animation(
            size=(self.width+4,self.height+4),
            duration=0.12
        ).start(self)


    def unselect(self):

        self.border_color.rgba = (
            0.20,
            0.22,
            0.25,
            1
        )