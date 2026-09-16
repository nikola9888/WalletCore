import json
import os
import csv
from components.header import Header
from components.balance_card import BalanceCard
from kivy.graphics import Color, RoundedRectangle
from components.category_grid import CategoryGrid
from database import Database
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from components.transaction_card import TransactionCard
from components.button import ModernButton
from components.rounded import RoundedInput
from kivy.graphics import Line
from kivy.uix.widget import Widget
from translations import translations
from kivy.app import App
from theme import BACKGROUND
from datetime import datetime
from kivy.metrics import dp
from kivy.clock import Clock

PROFILE_FILE = "data/profile.json"

class PieChart(Widget):
    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.bind(size=self.draw_chart, pos=self.draw_chart)

    def draw_chart(self, *args):
        self.canvas.clear()

        total = sum(self.data.values())
        if total == 0:
            return

        start_angle = 0

        colors = [
            (0.2, 0.7, 1, 1),
            (0.9, 0.3, 0.3, 1),
            (0.3, 0.9, 0.5, 1),
            (1, 0.8, 0.2, 1),
            (0.6, 0.4, 1, 1),
        ]

        i = 0

        with self.canvas:
            for label, value in self.data.items():
                angle = 360 * (value / total)

                Color(*colors[i % len(colors)])

                Line(
                    circle=(
                        self.center_x,
                        self.center_y,
                        min(self.width, self.height) / 2,
                        start_angle,
                        start_angle + angle
                    ),
                    width=30
                )

                start_angle += angle
                i += 1

class HomeScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        from kivy.graphics import Color, Rectangle

        with self.canvas.before:
            Color(0.035, 0.055, 0.10, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
            Color(0.05, 0.18, 0.32, 0.35)
            self.glow = RoundedRectangle(pos=self.pos, size=self.size, radius=[40])

        self.bind(pos=self.update_background, size=self.update_background)

        self.income = 0
        self.expense = 0
        self.balance = 0
        self.transactions = []
        self.active_filter = "all"
        self.editing_transaction = None
        self.editing_type = None
        self.db = Database()
        self.current_language = App.get_running_app().language

        root = BoxLayout(orientation="vertical", padding=10, spacing=10, size_hint=(1,1))

        with root.canvas.before:
            Color(*BACKGROUND)
            self.bg = RoundedRectangle(pos=root.pos, size=root.size)

        root.bind(pos=lambda x, y: setattr(self.bg, "pos", y), size=lambda x, y: setattr(self.bg, "size", y))

        self.balance_card = BalanceCard()
        self.balance_card.size_hint_y = None
        self.balance_card.height = dp(70)
        root.add_widget(self.balance_card)

        self.category_grid = CategoryGrid()
        root.add_widget(self.category_grid)

        self.header = Header()
        self.header.size_hint_y = None
        self.header.height = dp(30)
        self.header.padding = (15, 15, 15, 5)

        root.add_widget(Widget(size_hint_y=None, height=28))
        root.add_widget(self.header)
        root.add_widget(Widget(size_hint_y=None, height=dp(38)))

        input_card = BoxLayout(orientation="vertical", spacing=10, padding=15, size_hint=(1, None), height=dp(90))

        self.amount_input = RoundedInput(
            hint_text=translations[self.current_language]["amount"],
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=dp(40)
        )
        self.amount_input.write_tab = False

        amount_row = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=dp(40))

        self.amount_input = RoundedInput(
            hint_text=translations[self.current_language]["amount"],
            multiline=False,
            input_filter="float"
        )

        self.currency_btn = ModernButton(text=App.get_running_app().currency)
        self.currency_btn.size_hint_x = None
        self.currency_btn.width = dp(90)
        self.currency_btn.bind(on_press=lambda x: self.show_currency_picker())

        amount_row.add_widget(self.amount_input)
        amount_row.add_widget(self.currency_btn)
        input_card.add_widget(amount_row)

        self.note_input = RoundedInput(
            hint_text=translations[self.current_language]["note"],
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        self.note_input.write_tab = False
        input_card.add_widget(self.note_input)

        row1 = BoxLayout(orientation="horizontal", spacing=10, size_hint=(0.9, None), height=dp(28))
        self.income_btn = ModernButton(text=translations[self.current_language]["income"], icon="assets/icons/income.png")
        self.income_btn.bind(on_press=lambda x: self.add_transaction("income"))
        self.expense_btn = ModernButton(text=translations[self.current_language]["expense"], icon="assets/icons/expense.png")
        self.expense_btn.bind(on_press=lambda x: self.add_transaction("expense"))
        row1.add_widget(self.income_btn)
        row1.add_widget(self.expense_btn)
        input_card.add_widget(row1)
        root.add_widget(input_card)

        root.add_widget(Widget(size_hint_y=None, height=5))

        row2 = BoxLayout(orientation="horizontal", spacing=30, size_hint=(1, None), height=dp(25))
        self.stats_btn = ModernButton(text=translations[self.current_language]["stats"], icon="assets/icons/stats.png")
        self.chart_btn = ModernButton(text=translations[self.current_language]["chart"], icon="assets/icons/chart.png")
        self.export_btn = ModernButton(text=translations[self.current_language]["export"], icon="assets/icons/export.png")
        self.filter_btn = ModernButton(text=translations[self.current_language]["filter"], icon="assets/icons/filter.png")
        self.stats_btn.bind(on_press=lambda x: self.show_stats())
        self.chart_btn.bind(on_press=lambda x: self.show_chart())
        self.export_btn.bind(on_press=lambda x: self.export_pdf())
        self.filter_btn.bind(on_press=lambda x: self.show_filter())
        row2.add_widget(self.stats_btn)
        row2.add_widget(self.chart_btn)
        row2.add_widget(self.export_btn)
        row2.add_widget(self.filter_btn)
        root.add_widget(row2)
        root.add_widget(Widget(size_hint_y=None, height=dp(10)))

        self.scroll = ScrollView(size_hint=(1, 0.8), do_scroll_x=False)
        self.list_container = BoxLayout(orientation="vertical", spacing=10, size_hint_y=None)
        self.list_container.bind(minimum_height=self.list_container.setter("height"))
        self.scroll.add_widget(self.list_container)
        self.scroll.bar_width = dp(10)
        root.add_widget(self.scroll)

        self.load_transactions()
        self.add_widget(root)

    def update_background(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.glow.pos = self.pos
        self.glow.size = self.size

    def show_currency_picker(self):
        layout = BoxLayout(orientation="vertical", spacing=2, padding=3)
        popup = Popup(title="Select currency", content=layout, size_hint=(0.4, 0.6))
        currencies = ["RSD", "EUR", "USD", "CHF", "GBP", "BAM", "MKD", "JPY", "CNY"]
        for currency in currencies:
            btn = ModernButton(text=currency, size_hint_y=None, height=dp(45))
            btn.bind(on_press=lambda x, c=currency: (self.set_currency(c), popup.dismiss()))
            layout.add_widget(btn)
        popup.open()

    def set_currency(self, currency):
        App.get_running_app().currency = currency
        self.currency_btn.text = currency
        self.update_ui()

    def get_welcome(self):
        t = translations[App.get_running_app().language]
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                profile = json.load(f)
            name = profile.get("name", "")
            if name:
                return f"{t['welcome']}, {name}"
        return f"{t['welcome']}!"

    def add_transaction(self, ttype):
        if not self.amount_input.text:
            return
        try:
            amount = float(self.amount_input.text)
        except:
            return
        category = self.category_grid.selected
        note = self.note_input.text

        if self.editing_transaction is not None:
            self.db.update_transaction(self.editing_transaction, amount, self.editing_type, category, note)
            self.editing_transaction = None
            self.editing_type = None
        else:
            self.db.add_transaction(amount, ttype, category, note)

        self.amount_input.text = ""
        self.note_input.text = ""
        self.load_transactions()

    def load_transactions(self):
        saved_scroll_y = self.scroll.scroll_y if hasattr(self, "scroll") else 1

        rows = self.db.get_all()
        self.list_container.clear_widgets()

        self.income = 0
        self.expense = 0
        self.transactions = []

        for transaction_id, amount, ttype, category, note, _time in rows:
            self.transactions.append({"amount": amount, "type": ttype, "category": category, "note": note})

            if ttype == "income":
                self.income += amount
            else:
                self.expense += amount

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

        self.balance = self.income - self.expense
        self.update_ui()

        Clock.schedule_once(lambda dt: setattr(self.scroll, "scroll_y", saved_scroll_y), 0)

    def translate_category(self, category):
        t = translations[App.get_running_app().language]
        return t.get(category, category)

    def update_ui(self):
        currency = App.get_running_app().currency
        self.balance_card.balance.text = f"{self.balance:,.2f} {currency}".replace(",", ".")
        self.balance_card.income.text = f" {self.income:,.2f} {currency}".replace(",", ".")
        self.balance_card.expense.text = f" {self.expense:,.2f} {currency}".replace(",", ".")

    def get_stats(self):
        stats = {}
        for t in self.transactions:
            cat = t["category"]
            stats[cat] = stats.get(cat, 0) + t["amount"]
        return stats

    def show_stats(self):
        print("SHOW_STATS POZVAN")
        stats = self.get_stats()
        currency = App.get_running_app().currency
        text = "\n".join([f"{self.translate_category(k)}: {v:.2f} {currency}" for k, v in stats.items()])
        t = translations[App.get_running_app().language]
        Popup(title=t["stats"], content=Label(text=text, font_size="16sp"), size_hint=(0.8, 0.6)).open()

    def show_chart(self):
        stats = self.get_stats()
        if not stats:
            return
        total = sum(stats.values()) or 1
        layout = BoxLayout(orientation="vertical", padding=15, spacing=12, size_hint_y=None)
        layout.bind(minimum_height=layout.setter("height"))
        t = translations[App.get_running_app().language]
        title = Label(text=t["statistics"], size_hint_y=None, height=dp(60), font_size=42, bold=True)
        layout.add_widget(title)
        for cat, value in stats.items():
            percent = (value / total) * 100
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(45), spacing=10)
            category_label = Label(text=self.translate_category(cat), font_size=42, bold=True)
            percent_label = Label(text=f"{percent:.1f} %", font_size=42, bold=True)
            row.add_widget(category_label)
            row.add_widget(percent_label)
            layout.add_widget(row)
            bar = ProgressBar(max=100, value=percent, size_hint_y=None, height=dp(30))
            layout.add_widget(bar)
        Popup(title=t["chart"], content=layout, size_hint=(0.95, 0.85)).open()

    def show_filter(self):
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        popup = Popup(title="Filter", content=layout, size_hint=(0.8, 0.5))
        all_btn = ModernButton(text="All")
        income_btn = ModernButton(text="Income")
        expense_btn = ModernButton(text="Expense")
        layout.add_widget(all_btn)
        layout.add_widget(income_btn)
        layout.add_widget(expense_btn)
        all_btn.bind(on_press=lambda x: (setattr(self, "active_filter", "all"), popup.dismiss(), self.apply_filter()))
        income_btn.bind(on_press=lambda x: (setattr(self, "active_filter", "income"), popup.dismiss(), self.apply_filter()))
        expense_btn.bind(on_press=lambda x: (setattr(self, "active_filter", "expense"), popup.dismiss(), self.apply_filter()))
        popup.open()

    def apply_filter(self):
        for card in self.list_container.children:
            card_type = getattr(card, "ttype", None)
            if self.active_filter == "all":
                card.opacity = 1
                card.disabled = False
            elif self.active_filter == card_type:
                card.opacity = 1
                card.disabled = False
            else:
                card.opacity = 0
                card.disabled = True

    def delete_transaction(self, transaction_id):
        self.db.delete_transaction(transaction_id)
        self.load_transactions()

    def edit_transaction(self, transaction_id, amount, ttype, category, note):
        self.editing_transaction = transaction_id
        self.editing_type = ttype
        self.amount_input.text = str(amount)
        self.note_input.text = note or ""
        self.category_grid.selected = category

    def on_pre_enter(self, *args):
        self.load_transactions()

    def on_leave(self, *args):
        pass
