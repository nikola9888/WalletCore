import traceback
import os
from datetime import datetime
from kivy.app import App
from kivy.core.window import WindowBase
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from theme import BACKGROUND
from screens.home import HomeScreen
from screens.settings import SettingsScreen
from kivy.utils import get_color_from_hex
from kivy.storage.jsonstore import JsonStore
from screens.history import HistoryScreen
from screens.about import AboutScreen
from screens.profile import ProfileScreen
from components.onboarding import install_onboarding

CURRENCIES = {
    "sr": "RSD",
    "en": "USD",
    "de": "EUR",
    "fr": "EUR",
    "it": "EUR",
    "es": "EUR",
    "ru": "RUB",
    "pt": "EUR",
    "tr": "TRY",
    "pl": "PLN",
    "nl": "EUR",
    "uk": "UAH",
    "ro": "RON",
    "bg": "BGN",
    "hr": "EUR",
    "bs": "BAM",
    "sl": "EUR",
    "mk": "MKD",
    "sq": "ALL",
    "cs": "CZK",
    "hu": "HUF",
    "el": "EUR",
    "sv": "SEK",
    "no": "NOK",
    "da": "DKK",
    "fi": "EUR",
    "id": "IDR",
    "vi": "VND",
    "hi": "INR",
    "zh": "CNY",
    "ja": "JPY",
    "ko": "KRW",
    "ar": "USD",
    "fr-CA": "CAD",
}

class WalletCore(App):

    language = "en"

    store = JsonStore("wallet_settings.json")

    def load_language(self):

        if self.store.exists("settings"):

            lang = self.store.get("settings").get(
                "language",
                "en"
            )

            if lang in ["sr", "en", "de", "it", "es", "fr", "ru", "pt", "tr", "pl", "nl", "uk", "ro", "bg", "hr", "bs", "sl", "mk", "sq", "cs", "hu", "el", "sv", "no", "da", "fi", "id", "vi", "hi", "zh", "ja", "ko", "ar", "fr-CA"]:
                self.language = lang
            else:
                self.language = "en"
        self.currency = CURRENCIES.get(self.language, "RSD")

    def save_language(self):

        self.store.put(
            "settings",
            language=self.language
        )

    def build(self):

        self.load_language()

        print("BUILD START")

        sm = ScreenManager(
            transition=FadeTransition(duration=0.2)
        )
        sm.add_widget(HomeScreen(name="home"))
        print("HOME OK")
 
        sm.add_widget(SettingsScreen(name="settings"))
        
        sm.add_widget(
            HistoryScreen(name="history")
        )
        
        sm.add_widget(
            AboutScreen(name="about")
        )
        print("SETTINGS OK")
        
        sm.add_widget(ProfileScreen(name="profile"))

        return sm


install_onboarding(HomeScreen)
        
if __name__ == "__main__":

    try:
        WalletCore().run()

    except BaseException as e:

        import traceback

        print("===== CRASH =====")
        traceback.print_exc()

        try:
            with open("/storage/emulated/0/walletcore_error.txt", "w", encoding="utf-8") as f:
                f.write(traceback.format_exc())
        except Exception as err:
            print("LOG WRITE ERROR:", err)

        raise
