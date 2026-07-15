from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior

from kivy.graphics import Color, RoundedRectangle, Line
from kivy.animation import Animation


# =========================
# PREMIUM ROUNDED BUTTON
# =========================

class RoundedButton(ButtonBehavior, BoxLayout):

    def __init__(self, text="", icon=None, **kwargs):

        super().__init__(**kwargs)

        self.orientation = "horizontal"
        self.spacing = 10
        self.padding = (15, 5)

        self.size_hint_y = None
        self.height = 65


        with self.canvas.before:

            # shadow

            Color(
                0,
                0,
                0,
                0.35
            )

            self.shadow = RoundedRectangle(
                radius=[30]
            )


            # button

            Color(
                0.08,
                0.10,
                0.15,
                1
            )

            self.rect = RoundedRectangle(
                radius=[30]
            )


        with self.canvas.after:

            Color(
                0.25,
                0.55,
                1,
                1
            )

            self.border = Line(
                width=1.2
            )


        self.bind(
            pos=self.update_rect,
            size=self.update_rect
        )


        if icon:

            self.icon = Image(
                source=icon,
                size_hint=(None,None),
                size=(38,38),
                allow_stretch=True,
                keep_ratio=True
            )

            self.add_widget(self.icon)


        self.label = Label(
            text=text,
            color=(1,1,1,1),
            font_size="24sp",
            bold=True
        )

        self.add_widget(self.label)



    def update_rect(self,*args):

        self.rect.pos = self.pos
        self.rect.size = self.size

        self.shadow.pos = (
            self.x,
            self.y-3
        )

        self.shadow.size = self.size

        self.border.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            30
        )



    def on_press(self):

        Animation(
            opacity=0.75,
            duration=0.1
        ).start(self)



    def on_release(self):

        Animation(
            opacity=1,
            duration=0.15
        ).start(self)





# =========================
# PREMIUM ROUNDED INPUT
# =========================

class RoundedInput(BoxLayout):

    def __init__(
        self,
        bg=(0.10,0.12,0.17,1),
        radius=22,
        **kwargs
    ):

        hint = kwargs.pop(
            "hint_text",
            ""
        )

        input_filter = kwargs.pop(
            "input_filter",
            None
        )

        multiline = kwargs.pop(
            "multiline",
            False
        )


        super().__init__(**kwargs)


        self.orientation="vertical"


        with self.canvas.before:

            Color(*bg)

            self.rect = RoundedRectangle(
                radius=[radius]
            )


        with self.canvas.after:

            Color(
                0.25,
                0.55,
                1,
                0.8
            )

            self.border = Line(
                width=1
            )


        self.bind(
            pos=self.update_rect,
            size=self.update_rect
        )



        self.input = TextInput(

            hint_text=hint,

            input_filter=input_filter,

            multiline=multiline,


            background_normal="",

            background_active="",

            background_color=(
                0,
                0,
                0,
                0
            ),


            foreground_color=(
                1,
                1,
                1,
                1
            ),


            hint_text_color=(
                0.65,
                0.7,
                0.8,
                1
            ),


            font_size="20sp",

            padding=[
                40,
                20
            ]

        )


        self.add_widget(
            self.input
        )



    def update_rect(self,*args):

        self.rect.pos=self.pos
        self.rect.size=self.size


        self.border.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            22
        )



    @property
    def text(self):
        return self.input.text



    @text.setter
    def text(self,value):
        self.input.text=value



    @property
    def hint_text(self):
        return self.input.hint_text



    @hint_text.setter
    def hint_text(self,value):
        self.input.hint_text=value