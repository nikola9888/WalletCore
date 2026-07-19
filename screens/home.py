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
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime

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

            # glavna pozadina
            Color(0.035, 0.055, 0.10, 1)

            self.rect = Rectangle(
                pos=self.pos,
                size=self.size
            )

            # blagi svetliji sloj gore
            Color(0.05, 0.18, 0.32, 0.35)
 
            self.glow = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[40]
            )

        self.bind(
            pos=self.update_background,
            size=self.update_background
        )

        # =====================
        # STATE
        # =====================
        self.income = 0
        self.expense = 0
        self.balance = 0
        self.transactions = []
        self.active_filter = "all"
        self.editing_transaction = None
        self.editing_type = None
        self.db = Database()
        self.current_language = App.get_running_app().language

         # =====================
        # ROOT
        # =====================
        root = BoxLayout(
            orientation="vertical",
            padding=10,
            spacing=10
        )
        
        with root.canvas.before:
            Color(*BACKGROUND)
            self.bg = RoundedRectangle(
                pos=root.pos,
                size=root.size
            )

        root.bind(
            pos=lambda x, y: setattr(self.bg, "pos", y),
            size=lambda x, y: setattr(self.bg, "size", y)
        )

        # BALANCE
        self.balance_card = BalanceCard()
        self.balance_card.size_hint_y = None
        self.balance_card.height = 180
        root.add_widget(self.balance_card)

        # CATEGORY
        self.category_grid = CategoryGrid()
        root.add_widget(self.category_grid)

        # HEADER
        header = Header()

        header.size_hint_y = None
        header.height = 75
        header.padding = (15, 15, 15, 5)

        root.add_widget(
            Widget(
                size_hint_y=None,
                height=18
            )
        )

        root.add_widget(header)
        self.welcome_label = Label(
            text=self.get_welcome(),
            color=(1,1,1,1),
            font_size="16sp",
            bold=True,
            size_hint_y=None,
            height=50
        )

        root.add_widget(self.welcome_label)
        
        # =====================
        # INPUT CARD
        # =====================
        input_card = BoxLayout(
            orientation="vertical",
            spacing=10,
            padding=15,
            size_hint=(1, None),
            height=380
        )

        self.amount_input = RoundedInput(
            hint_text=translations[self.current_language]["amount"],
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=120
        )
        self.amount_input.write_tab = False
        input_card.add_widget(self.amount_input)

        self.note_input = RoundedInput(
            hint_text=translations[self.current_language]["note"],
            multiline=False,
            size_hint_y=None,
            height=120
        )
        self.note_input.write_tab = False
        input_card.add_widget(self.note_input)

        # =====================
        # INCOME / EXPENSE
        # =====================
        row1 = BoxLayout(
            orientation="horizontal",
            spacing=10,
            size_hint=(0.9, None),
            height=65
        )

        self.income_btn = ModernButton(
            text=translations[self.current_language]["income"],
            icon="assets/icons/income.png"
        )
        self.income_btn.bind(on_press=lambda x: self.add_transaction("income"))

        self.expense_btn = ModernButton(
            text=translations[self.current_language]["expense"],
            icon="assets/icons/expense.png"
        )
        self.expense_btn.bind(
            on_press=lambda x: self.add_transaction("expense")
        )
        
        row1.add_widget(self.income_btn)
        row1.add_widget(self.expense_btn)

        input_card.add_widget(row1)

        root.add_widget(input_card)

        # =====================
        # STATS / CHART
        # =====================

        root.add_widget(
            Widget(size_hint_y=None, height=5)
        )
        
        row2 = BoxLayout(
            orientation="horizontal",
            spacing=8,
            size_hint=(1, None),
            height=65
        )
 
        self.stats_btn = ModernButton(
            text=translations[self.current_language]["stats"],
            icon="assets/icons/stats.png"
        )

        self.chart_btn = ModernButton(
            text=translations[self.current_language]["chart"],
            icon="assets/icons/chart.png"
        )

        self.export_btn = ModernButton(
            text=translations[self.current_language]["export"],
            icon="assets/icons/export.png"
        )

        self.filter_btn = ModernButton(
            text=translations[self.current_language]["filter"],
            icon="assets/icons/filter.png"
        )
        
        
        self.stats_btn.bind(on_press=lambda x: self.show_stats())
        self.chart_btn.bind(on_press=lambda x: self.show_chart())
        self.export_btn.bind(
            on_press=lambda x: self.export_pdf()
        )
        self.filter_btn.bind(on_press=lambda x: self.show_filter())

        row2.add_widget(self.stats_btn)
        row2.add_widget(self.chart_btn)
        row2.add_widget(self.export_btn)
        row2.add_widget(self.filter_btn)

        root.add_widget(row2)

        # TRANSACTION LIST
        scroll = ScrollView(
            size_hint=(0.9, 1.5),
            do_scroll_x=False
        )

        self.list_container = BoxLayout(
            orientation="vertical",
            spacing=10,
            size_hint_y=None
        )

        self.list_container.bind(
            minimum_height=self.list_container.setter("height")
        )

        scroll.add_widget(self.list_container)
        root.add_widget(scroll)
        
        # load data
        self.load_transactions()

        # FINAL
        self.add_widget(root)
      
    def update_background(self, *args):

        self.rect.pos = self.pos
        self.rect.size = self.size
 
        self.glow.pos = self.pos
        self.glow.size = self.size  
        
    def get_welcome(self):

        t = translations[App.get_running_app().language]

        if os.path.exists(PROFILE_FILE):
 
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                profile = json.load(f)

            name = profile.get("name", "")

            if name:
                return f"{t['welcome']}, {name}"

        return f"{t['welcome']}!"
        
    # =====================
    # ADD TRANSACTION
    # =====================
    def add_transaction(self, ttype):

        if not self.amount_input.text:
            return

        try:
            amount = float(self.amount_input.text)
        except:
            return

        category = self.category_grid.selected
        note = self.note_input.text
    
        # EDIT POSTOJEĆE TRANSAKCIJE
        if self.editing_transaction is not None:

            self.db.update_transaction(
                self.editing_transaction,
                amount,
                self.editing_type,
                category,
                note
            )

            self.editing_transaction = None
            self.editing_type = None

        else:
            self.db.add_transaction(
                amount,
                ttype,
                category,
                note
            )

        self.amount_input.text = ""
        self.note_input.text = ""

        self.load_transactions()
    # =====================
    # LOAD FROM DB
    # =====================
    def load_transactions(self):

        rows = self.db.get_all()

        self.list_container.clear_widgets()

        self.income = 0
        self.expense = 0
        self.transactions = []

        for transaction_id, amount, ttype, category, note, _time in rows:

            self.transactions.append({
                "amount": amount,
                "type": ttype,
                "category": category,
                "note": note
            })

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

    # =====================
    # UI UPDATE
    # =====================
    def update_ui(self):
        currency = App.get_running_app().currency

        self.balance_card.balance.text = f"{self.balance:,.2f} {currency}".replace(",", ".")
        self.balance_card.income.text = f" {self.income:,.2f} {currency}".replace(",", ".")
        self.balance_card.expense.text = f" {self.expense:,.2f} {currency}".replace(",", ".")
        
    # =====================
    # STATS
    # =====================
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
 
        text = "\n".join(
            [f"{k}: {v:.2f} {currency}" for k, v in stats.items()]
        )

        Popup(
            title="Stats",
            content=Label(
                text=text,
                font_size="16sp"
            ),
            size_hint=(0.8, 0.6)
        ).open()

    # =====================
    # CHART
    # =====================
    def show_chart(self):

        stats = self.get_stats()

        if not stats:
            return
  
        total = sum(stats.values()) or 1

        layout = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=12,
            size_hint_y=None
        )

        layout.bind(
            minimum_height=layout.setter("height")
        )

        title = Label(
            text=" Statistics",
            size_hint_y=None,
            height=60,
            font_size=42,
            bold=True
        )

        layout.add_widget(title)
 

        for cat, value in stats.items():

            percent = (value / total) * 100


            row = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=45,
                spacing=10
            )


            category_label = Label(
                text=cat,
                font_size=42,
                bold=True
            )


            percent_label = Label(
                text=f"{percent:.1f} %",
                font_size=42,
                bold=True
            )


            row.add_widget(category_label)
            row.add_widget(percent_label)

            layout.add_widget(row)


            bar = ProgressBar(
                max=100,
                value=percent,
                size_hint_y=None,
                height=30
            )

            layout.add_widget(bar)


        scroll = ScrollView()

        scroll.add_widget(layout)


        Popup(
            title="Statistics",
            content=scroll,
            size_hint=(0.9,0.9)
        ).open()
        
    def get_icon(self, category):
        icons = {
            "Food": "assets/icons/food.png",
            "Transport": "assets/icons/transport.png",
            "Shopping": "assets/icons/shopping.png",
            "Bills": "assets/icons/bills.png",
            "Health": "assets/icons/health.png",
            "Salary": "assets/icons/salary.png",
            "Other": "assets/icons/other.png"
        }

        return icons.get(category, "assets/icons/other.png")
        
    def delete_transaction(self, transaction_id):
        print("Deleting:", transaction_id)
        self.db.delete_transaction(transaction_id)
        self.load_transactions()
        
    def edit_transaction(self, transaction_id):

        transaction = self.db.get_transaction(transaction_id)

        if not transaction:
            return

        transaction_id, amount, ttype, category, note, time = transaction

        self.amount_input.text = str(amount)
        self.note_input.text = note if note else ""

        self.category_grid.selected = category

        self.editing_transaction = transaction_id
        self.editing_type = ttype
        
    def show_filter(self):

        layout = BoxLayout(
            orientation="vertical",
            spacing=10,
            padding=10
        )

        t = translations[App.get_running_app().language]

        filters = [
            (t["all"], "all"),
            (t["income"], "income"),
            (t["expense"], "expense"),
            (t["food"], "food"),
            (t["transport"], "transport"),
            (t["shopping"], "shopping"),
            (t["bills"], "bills"),
            (t["fun"], "fun"),
            (t["health"], "health"),
            (t["salary"], "salary"),
            (t["other"], "other")
         ]

        popup = Popup(
            title="Filter",
            content=layout,
            size_hint=(0.8, 0.8)
        )

        for text, key in filters:

            btn = ModernButton(
                text=text,
                size_hint_y=None,
                height=60
            )

            btn.bind(
                on_press=lambda x, k=key: (
                    self.apply_filter(k),
                    popup.dismiss()
                )
            )

            layout.add_widget(btn)

        popup.open()
        
    def apply_filter(self, filter_type):

        self.list_container.clear_widgets()

        rows = self.db.get_all()

        for transaction_id, amount, ttype, category, note, _time in rows:

            if filter_type == "income" and ttype != "income":
                continue

            if filter_type == "expense" and ttype != "expense":
                continue

            if filter_type not in ["all", "income", "expense"]:
                if category != filter_type:
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
        
    def update_language(self):
        t = translations[App.get_running_app().language]

        self.amount_input.hint_text = t["amount"]
        self.note_input.hint_text = t["note"]

        # osvežavanje postojećih dugmadi
        if hasattr(self, "settings_btn"):
            self.settings_btn.text =  t["settings"]

        if hasattr(self, "income_btn"):
            self.income_btn.text =  t["income"]

        if hasattr(self, "expense_btn"):
            self.expense_btn.text =  t["expense"]

        if hasattr(self, "stats_btn"):
            self.stats_btn.text =  t["stats"]

        if hasattr(self, "chart_btn"):
            self.chart_btn.text = t["chart"]
           
        if hasattr(self, "export_btn"):
            self.export_btn.text = t["export"]

        if hasattr(self, "filter_btn"):
            self.filter_btn.text = t["filter"]

        self.welcome_label.text = self.get_welcome()  
        self.category_grid.update_language() 
  
        self.balance_card.update_language()
           
        for card in self.list_container.children:
            if hasattr(card, "update_language"):
                card.update_language()
                            
                           
    def export_pdf(self):

        import os
        currency = App.get_running_app().currency
        os.makedirs("exports", exist_ok=True)

        filename = f"exports/WalletCore_Report_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.pdf"

        doc = SimpleDocTemplate(filename)
   
        styles = getSampleStyleSheet()

        story = []

        story.append(Paragraph("<b><font size=22>WalletCore</font></b>", styles["Title"]))
        story.append(Paragraph("Financial Report", styles["Heading2"]))
        story.append(Paragraph("<br/>", styles["Normal"]))

        story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}", styles["Normal"]))
        story.append(Paragraph(f"<b>Balance:</b> {self.balance:.2f} {currency}", styles["Normal"]))
        story.append(Paragraph(f"<b>Income:</b> {self.income:.2f} {currency}", styles["Normal"]))
        story.append(Paragraph(f"<b>Expenses:</b> {self.expense:.2f} {currency}", styles["Normal"]))
        story.append(Paragraph("<br/>", styles["Normal"]))

        data = [
            ["Date", "Type", "Category", "Amount"]
        ]

        rows = self.db.get_all()

        for _, amount, ttype, category, note, time in rows:

            data.append([
                str(time),
                ttype,
                category,
                f"{amount:.2f} {currency}"
            ])
 
        table = Table(data)

        table.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#3B82F6")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.white),

            ("GRID",(0,0),(-1,-1),1,colors.grey),

            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),

            ("BOTTOMPADDING",(0,0),(-1,0),10),
 
            ("BACKGROUND",(0,1),(-1,-1),colors.whitesmoke)
        ]))

        story.append(table)

        doc.build(story)

        t = translations[App.get_running_app().language]

        Popup(
            title=t["pdf_export"],
            content=Label(
                text=t["pdf_saved"],
                font_size="16sp"
            ),
            size_hint=(0.7, 0.3)
        ).open()
