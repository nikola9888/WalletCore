import traceback
import os
from datetime import datetime
from kivy.app import App
from kivy.metrics import dp

LOG_FILE = "walletcore_debug.log"

def log(text):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(
            f"{datetime.now()} : {text}\n"
        )


log("MAIN START")


from kivy.app import App
log("KIVY OK")

from kivy.core.window import Window
log("WINDOW OK")

from kivy.storage.jsonstore import JsonStore
log("JSON OK")

from kivy.uix.screenmanager import ScreenManager, FadeTransition
log("SCREENMANAGER OK")

from theme import BACKGROUND
log("THEME OK")

from screens.home import HomeScreen
log("HOME OK")

from screens.settings import SettingsScreen
log("SETTINGS OK")

from screens.history import HistoryScreen
log("HISTORY OK")

from screens.about import AboutScreen
log("ABOUT OK")

from screens.profile import ProfileScreen
log("PROFILE IMPORT OK")


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


    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.store = JsonStore(
            "wallet_settings.json"
        )


    def load_language(self):

        if self.store.exists("settings"):

            lang = self.store.get("settings").get(
                "language",
                "sr"
            )

            if lang in CURRENCIES:
                self.language = lang
            else:
                self.language = "sr"

        self.currency = CURRENCIES.get(
            self.language,
            "RSD"
        )


    def save_language(self):

        self.store.put(
            "settings",
            language=self.language
        )


    def build(self):

        try:

            log("BUILD START")

            self.load_language()

            log("LANGUAGE LOADED")


            Window.clearcolor = BACKGROUND
            Window.softinput_mode = "below_target"


            sm = ScreenManager(
                transition=FadeTransition(
                    duration=0.2
                )
            )


            log("ADDING HOME")

            sm.add_widget(
                HomeScreen(name="home")
            )

            log("HOME OK")



            log("ADDING SETTINGS")

            sm.add_widget(
                SettingsScreen(name="settings")
            )

            log("SETTINGS OK")



            log("ADDING HISTORY")

            sm.add_widget(
                HistoryScreen(name="history")
            )

            log("HISTORY OK")



            log("ADDING ABOUT")

            sm.add_widget(
                AboutScreen(name="about")
            )

            log("ABOUT OK")



            log("CREATING PROFILE")

            profile = ProfileScreen(
                name="profile"
            )

            log("PROFILE CREATED")


            sm.add_widget(profile)

            log("PROFILE ADDED")


            log("BUILD FINISHED")


            return sm


        except Exception:

            log("BUILD ERROR")

            log(
                traceback.format_exc()
            )

            raise



if __name__ == "__main__":
    try:
        log("APP START")

        WalletCore().run()

        log("APP CLOSED")

    except Exception:
        log("===== CRASH =====")
        log(traceback.format_exc())
        raise
