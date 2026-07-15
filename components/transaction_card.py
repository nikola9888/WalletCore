from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from functools import partial
from kivy.app import App
from translations import translations

class TransactionCard(BoxLayout):

    def __init__(
        self,
        transaction_id,
        amount,
        ttype,
        category,
        note="",
        on_delete=None,
        on_edit=None,
        **kwargs):

        super().__init__(**kwargs)
        
        self.current_language = App.get_running_app().language
        t = translations[self.current_language] 
        self.on_delete = on_delete
        self.on_edit = on_edit
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = 110
        self.padding = (20, 16)
        self.spacing = 10
        self.transaction_id = transaction_id
        
        accent = (0.2, 0.9, 0.5, 1) if ttype == "income" else (0.9, 0.3, 0.3, 1)
        sign = "+" if ttype == "income" else "-"

        icons = {
            "food": "🍔",
            "transport": "🚗",
            "shopping": "🛍️",
            "bills": "📄",
            "health": "💊",
            "salary": "💰",
            "fun": "🎮",
            "gift": "🎁",
            "other": "📦"
        }

        self.category = category
        self.icon = icons.get(category, "📌")

        with self.canvas.before:

            # senka
            Color(0, 0, 0, 0.25)
            self.shadow = RoundedRectangle(
                radius=[26]
            )

            # tamna glass kartica
            Color(0.10, 0.16, 0.23, 0.95)
            self.bg = RoundedRectangle(
                radius=[26]
            )

            # leva status linija
            Color(*accent)
            self.bar = RoundedRectangle(
                radius=[5]
            )

            # srebrna ivica
            Color(0.35, 0.38, 0.42, 1)
            self.outline = Line(
                rounded_rectangle=(0,0,0,0,26),
                width=1.5
            )
            
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        
        left = BoxLayout(orientation="vertical")

        self.title_label = Label(
            text=f"{self.icon}  {t.get(category, category)}",
            bold=True,
            halign="left",
            valign="middle",
            font_size="17sp",
            color=(1, 1, 1, 1)
        )

        self.title_label.bind(
            size=lambda i, v: setattr(i, "text_size", i.size)
        )
        subtitle = Label(
            text=note if note else " ",
            font_size="13sp",
            color=(0.75, 0.75, 0.75, 1),
            halign="left",
            valign="middle"
        )
        subtitle.bind(size=lambda i, v: setattr(i, "text_size", i.size))

        left.add_widget(self.title_label)
        left.add_widget(subtitle)

        self.amount = amount
        self.sign = sign

        currency = App.get_running_app().currency

        self.amount_label = Label(
            text=f"{sign}{amount:,.0f} {currency}".replace(",", "."),
            color=accent,
            font_size="13sp",
            bold=True,
            halign="right",
            valign="middle",
            size_hint_x=0.7
        )

        self.amount_label.bind(
            size=lambda i, v: setattr(i, "text_size", i.size)
        )

        self.add_widget(left)
        self.add_widget(self.amount_label)

    def update_canvas(self, *args):

        self.shadow.pos = (
            self.x,
            self.y - 5
        )
        self.shadow.size = self.size


        self.bg.pos = self.pos
        self.bg.size = self.size
 

        self.bar.pos = (
            self.x,
            self.y
        )
        self.bar.size = (
            7,
            self.height
        )


        self.outline.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            26
        )
        
    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):

            if touch.is_double_tap:
                self.show_menu()
                return True

        return super().on_touch_down(touch)
        
    def show_menu(self):

        t = translations[App.get_running_app().language]

        layout = BoxLayout(
            orientation="vertical",
            spacing=10,
            padding=10
        )

        edit = Button(
            text= t["edit"],
            background_normal="",
            background_color=(0.15, 0.35, 0.55, 1),
            color=(1,1,1,1),
            font_size=38
        )

        delete = Button(
            text= t["delete"],
            background_normal="",
            background_color=(0.15, 0.35, 0.55, 1),
            color=(1,1,1,1),
            font_size=38
        )

        cancel = Button(
            text= t["cancel"],
            background_normal="",
            background_color=(0.15, 0.35, 0.55, 1),
            color=(1,1,1,1),
            font_size=38
        )
        popup = Popup(
            title=t["transaction"],
            content=layout,
            size_hint=(0.80, 0.45),
            separator_color=(0.35,0.38,0.42,1)
        )

        edit.bind(
            on_release=lambda x: self.edit_transaction(popup)
        )

        delete.bind(
            on_release=partial(self.confirm_delete, popup)
        )

        cancel.bind(
            on_release=lambda x: popup.dismiss()
       )

        layout.add_widget(edit)
        layout.add_widget(delete)
        layout.add_widget(cancel)

        with layout.canvas.before:
            Color(0.08, 0.12, 0.18, 1)
            layout.bg = RoundedRectangle(
                radius=[35]
            )

        layout.bind(
            pos=lambda x,y: setattr(layout.bg,"pos",        layout.pos),
            size=lambda x,y: setattr(layout.bg,        "size",layout.size)
        )

        popup.open()
        
    def edit_transaction(self, popup):
        popup.dismiss()

        if self.on_edit:
            self.on_edit(
                self.transaction_id
            )
    def confirm_delete(self, menu_popup, instance):

        t = translations[App.get_running_app().language]

        menu_popup.dismiss()

        layout = BoxLayout(
            orientation="vertical",
            spacing=10,
            padding=10
        )

        layout.add_widget(
            Label(
                text=t["delete_question"]
            )
        )

        buttons = BoxLayout(
            size_hint_y=None,
            height=45,
            spacing=10
        )

        cancel = Button(text=t["cancel"])
        delete = Button(text=t["delete"])

        buttons.add_widget(cancel)
        buttons.add_widget(delete)
 
        layout.add_widget(buttons)

        popup = Popup(
            title=t["confirmation"],
            content=layout,
            size_hint=(0.8, 0.35)
        )
  
        cancel.bind(
            on_release=lambda x: popup.dismiss()
        )
 
        delete.bind(
            on_release=lambda x: self.delete_transaction(popup)
        )

        popup.open()
        
 
    def delete_transaction(self, popup):
        popup.dismiss()
        print("Delete pressed", self.transaction_id)

        if self.on_delete:
            self.on_delete(self.transaction_id)
            
            
    def update_language(self):

        t = translations[App.get_running_app().language]

        self.title_label.text = (
            f"{self.icon}  {t.get(self.category, self.category)}"
        )
        currency = App.get_running_app().currency

        self.amount_label.text = (
            f"{self.sign}{self.amount:,.0f} {currency}"
        ).replace(",", ".")