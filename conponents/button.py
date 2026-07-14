from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.behaviors import ButtonBehavior
from kivy.animation import Animation

from theme import PRIMARY, TEXT, RADIUS


class IconButton(ButtonBehavior, BoxLayout):

    def __init__(self, text="", icon=None, **kwargs):

        super().__init__(**kwargs)

        self.disabled = False

        self.orientation = "horizontal"
        self.spacing = 10
        self.padding = (20, 0)


        # POZADINA DUGMETA
        with self.canvas.before:

            Color(*PRIMARY)

            self.bg = RoundedRectangle(
                radius=[RADIUS]
            )


        self.bind(
            pos=self.update_bg,
            size=self.update_bg
        )


        # IKONICA
        if icon:

            self.icon = Image(
                source=icon,
                size_hint=(None ,None),
                size=(58,58),
                fit_mode="contain"
            )

            self.add_widget(self.icon)



        # TEKST
        self.label = Label(
            text=text,
            color=TEXT,
            font_size="12sp",
            bold=True,
            halign="center",
            valign="middle"
        )


        self.label.bind(
            size=lambda x,y:
            setattr(
                x,
                "text_size",
                x.size
            )
        )


        self.add_widget(self.label)

    def on_touch_down(self, touch):
 
        if self.collide_point(*touch.pos):
            
            return super().on_touch_down(touch)

        return False

    def on_touch_up(self, touch):

        if self.collide_point(*touch.pos):
          
            return super().on_touch_up(touch)

        return False

    def update_bg(self,*args):

        self.bg.pos = self.pos
        self.bg.size = self.size



    @property
    def text(self):

        return self.label.text



    @text.setter
    def text(self,value):

        self.label.text = value



class ModernButton(IconButton):

    def on_press(self):
        Animation(
            opacity=0.6,
            duration=0.08
        ).start(self)

    def on_release(self):
        Animation(
            opacity=1,
            duration=0.08
        ).start(self)