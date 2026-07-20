from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from translations import translations
from theme import CATEGORY_BG, PRIMARY
from category_button import CategoryButton
class CategoryGrid(GridLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.current_language = App.get_running_app().language
        t = translations[self.current_language]

        self.cols = 2
        self.spacing = 10
        self.size_hint_y = None
        self.height = 420

        self.selected = "food"
        self.selected_text = " food"

        self.buttons = []

        categories = [
            ("food", t["food"]),
            ("transport", t["transport"]),
            ("shopping", t["shopping"]),
            ("bills", t["bills"]),
            ("fun", t["fun"]),
            ("health", t["health"]),
            ("salary", t["salary"]),
            ("other", t["other"])
]

        for key, text in categories:

            btn = CategoryButton(
                category=key,
                title=text,
                icon=f"assets/icons/{key}.png",
                size_hint_y=None,
                height=100
            )

            btn.category_key = key

            btn.bind(on_press=self.select_category)

            self.buttons.append(btn)

            self.add_widget(btn)

        # početno izabrana kategorija
        for btn in self.buttons:
            btn.unselect()

        self.buttons[0].select()

    def select_category(self, button):

        for btn in self.buttons:
            btn.unselect()

        button.select()

        self.selected = button.category_key
        self.selected_text = button.title
        
    def update_language(self):
        t = translations[App.get_running_app().language]

        texts = {
            "food": t["food"],
            "transport": t["transport"],
            "shopping": t["shopping"],
            "bills": t["bills"],
            "fun": t["fun"],
            "health": t["health"],
            "salary": t["salary"],
            "other": t["other"]
        }

        for btn in self.buttons:
            btn.label.text = texts[btn.category_key]
            btn.title = texts[btn.category_key]

        for btn in self.buttons:
            if btn.category_key == self.selected:
                self.selected_text = btn.title
                break
