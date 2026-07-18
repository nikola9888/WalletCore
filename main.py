import traceback
import os
from datetime import datetime

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.storage.jsonstore import JsonStore

from theme import BACKGROUND
from screens.home import HomeScreen
from screens.settings import SettingsScreen
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

        print("[APP] Loading language...")

        if self.store.exists("settings"):

            lang = self.store.get("settings").get(
                "language",
                "sr"
            )

            if lang in ["sr", "en", "de", "fr", "it", "es", "ru"]:
                self.language = lang
            else:
                self.language = "sr"

        self.currency = CURRENCIES.get(self.language, "RSD")

        print(f"[APP] Language: {self.language}")
        print(f"[APP] Currency: {self.currency}")

    def save_language(self):

        self.store.put(
            "settings",
            language=self.language
        )

        print("[APP] Language saved")

    def build(self):

        print("===================================")
        print("[APP] BUILD START")
        print("===================================")

        self.load_language()

        Window.clearcolor = BACKGROUND
        print("[APP] Background loaded")

        sm = ScreenManager(
            transition=FadeTransition(duration=0.2)
        )
        print("[APP] ScreenManager created")

        try:
            print("[APP] Loading HomeScreen...")
            sm.add_widget(HomeScreen(name="home"))
            print("[APP] HomeScreen OK")
        except Exception:
            print("[ERROR] HomeScreen FAILED")
            raise

        try:
            print("[APP] Loading SettingsScreen...")
            sm.add_widget(SettingsScreen(name="settings"))
            print("[APP] SettingsScreen OK")
        except Exception:
            print("[ERROR] SettingsScreen FAILED")
            raise

        try:
            print("[APP] Loading HistoryScreen...")
            sm.add_widget(HistoryScreen(name="history"))
            print("[APP] HistoryScreen OK")
        except Exception:
            print("[ERROR] HistoryScreen FAILED")
            raise

        try:
            print("[APP] Loading AboutScreen...")
            sm.add_widget(AboutScreen(name="about"))
            print("[APP] AboutScreen OK")
        except Exception:
            print("[ERROR] AboutScreen FAILED")
            raise

        try:
            print("[APP] Loading ProfileScreen...")
            sm.add_widget(ProfileScreen(name="profile"))
            print("[APP] ProfileScreen OK")
        except Exception:
            print("[ERROR] ProfileScreen FAILED")
            raise

        print("===================================")
        print("[APP] BUILD FINISHED SUCCESSFULLY")
        print("===================================")

        return sm


if __name__ == "__main__":

    try:
        WalletCore().run()

    except Exception as e:

        error = traceback.format_exc()

        print("===================================")
        print("[APP] FATAL ERROR")
        print(error)
        print("===================================")

        # pokušaj da sačuva log u interni folder aplikacije
        try:
            app = App.get_running_app()

            if app:
                logfile = os.path.join(
                    app.user_data_dir,
                    "WalletCore_crash.txt"
                )

                with open(logfile, "w", encoding="utf-8") as f:
                    f.write(error)

                print("[APP] Crash log saved:", logfile)

        except Exception:
            # ako ni ovo ne uspe, pokušaj na SD karticu
            try:
                with open("/sdcard/WalletCore_crash.txt", "w", encoding="utf-8") as f:
                    f.write(error)

                print("[APP] Crash log saved to /sdcard")

            except Exception:
                print("[APP] Unable to save crash log.")

        raise