import traceback
import os
from datetime import datetime
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from theme import BACKGROUND
from screens.home import HomeScreen
from screens.settings import SettingsScreen
from kivy.utils import get_color_from_hex
from kivy.storage.jsonstore import JsonStore
from screens.history import HistoryScreen
from screens.about import AboutScreen
from screens.profile import ProfileScreen

CURRENCIES = {
    "sr": "RSD",
    "en": "USD",
    "de": "EUR",
    "fr": "EUR",
    "it": "EUR",
    "es": "EUR",
    "ru": "RUB",
}

class WalletCore(App):

    language = "sr"

    store = JsonStore("wallet_settings.json")

    def load_language(self):

        if self.store.exists("settings"):

            lang = self.store.get("settings").get(
                "language",
                "sr"
            )

            if lang in ["sr", "en", "de", "it", "es", "fr", "ru"]:
                self.language = lang
            else:
                self.language = "sr"
        self.currency = CURRENCIES.get(self.language, "RSD")

    def save_language(self):

        self.store.put(
            "settings",
            language=self.language
        )


    def build(self):

        self.load_language()

        Window.clearcolor = BACKGROUND

        sm = ScreenManager(
        transition=FadeTransition(duration=0.2)
        )

        sm.add_widget(HomeScreen(name="home"))
    print("HOME OK")

        # sm.add_widget(SettingsScreen(name="settings"))

        sm.add_widget(
            HistoryScreen(name="history")
        )

        sm.add_widget(
            AboutScreen(name="about")
        )

        #     sm.add_widget(ProfileScreen(name="profile"))

        print("BUILD DONE")

        return sm