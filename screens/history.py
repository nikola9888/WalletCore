from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.app import App
from translations import translations
from database import Database
from components.transaction_card import TransactionCard
from theme import TEXT, TITLE


class HistoryScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.db = Database()
        self.filter_type = "all"
        
        self.current_language = App.get_running_app().language
        self.t = translations[self.current_language]

        root = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )


        # TITLE

        self.title = Label(
            text=f" {translations[App.get_running_app().language]['history']}",
            color=TEXT,
            font_size=TITLE,
            bold=True,
            size_hint_y=None,
            height=70
        )

        root.add_widget(self.title)


        # SEARCH

        self.search = TextInput(
            hint_text=translations[App.get_running_app().language]["search"],
            size_hint_y=None,
            height=60,
            multiline=False
        )

        self.search.bind(
            text=self.search_history
        )

        root.add_widget(self.search)



        # FILTER BUTTONS

        filter_row = BoxLayout(
            size_hint_y=None,
            height=60,
            spacing=10
        )


        self.all_btn = Button(
            text=translations[App.get_running_app().language]["all"]
        )

        self.income_btn = Button(
            text=translations[App.get_running_app().language]["income"]
        )

        self.expense_btn = Button(
            text=translations[App.get_running_app().language]["expense"]
        )


        self.all_btn.bind(
            on_press=lambda x:self.set_filter("all")
        )

        self.income_btn.bind(
            on_press=lambda x:self.set_filter("income")
        )

        self.expense_btn.bind(
            on_press=lambda x:self.set_filter("expense")
        )


        filter_row.add_widget(self.all_btn)
        filter_row.add_widget(self.income_btn)
        filter_row.add_widget(self.expense_btn)


        root.add_widget(filter_row)



        # LIST


        scroll = ScrollView()


        self.list_container = BoxLayout(
            orientation="vertical",
            spacing=10,
            size_hint_y=None
        )


        self.list_container.bind(
            minimum_height=
            self.list_container.setter("height")
        )


        scroll.add_widget(
            self.list_container
        )


        root.add_widget(scroll)


        # BACK

        self.back_btn = Button(
            text=self.t["back"],
            size_hint_y=None,
            height=60
        )

        self.back_btn.bind(
            on_press=self.go_home
        )


        root.add_widget(self.back_btn)


        self.add_widget(root)


        self.load_history()



    def load_history(self, search=""):

        self.list_container.clear_widgets()


        rows = self.db.get_all()


        for row in rows:

            transaction_id, amount, ttype, category, note, time = row


            # FILTER

            if self.filter_type != "all":

                if ttype != self.filter_type:
                    continue



            # SEARCH

            text = (
                str(category)
                + str(note)
                + str(amount)
            ).lower()


            if search.lower() not in text:
                continue



            card = TransactionCard(
                transaction_id=transaction_id,
                amount=amount,
                ttype=ttype,
                category=category,
                note=note,
                on_delete=self.delete_transaction,
                on_edit=self.edit_transaction
            )


            self.list_container.add_widget(card)




    def set_filter(self, value):

        self.filter_type = value

        self.load_history(
            self.search.text
        )



    def search_history(self, instance, value):

        self.load_history(value)




    def delete_transaction(self, transaction_id):

        self.db.delete_transaction(
            transaction_id
        )

        self.load_history(
            self.search.text
        )



    def edit_transaction(self, transaction_id):

        home = self.manager.get_screen(
            "home"
        )

        home.edit_transaction(
            transaction_id
        )

        self.manager.current = "home"



    def go_home(self, instance):

        self.manager.current="home"
        
    def update_language(self):

        self.t = translations[
            App.get_running_app().language
        ]

        self.title.text = self.t["history"]

        self.search.hint_text = self.t["search"]
        self.back_btn.text = self.t["back"]
        self.all_btn.text = self.t["all"]
        self.income_btn.text = self.t["income"]
        self.expense_btn.text = self.t["expense"]
