import shutil
import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from components.button import ModernButton
from kivy.uix.popup import Popup
from kivy.app import App
from translations import translations
import glob

class SettingsScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.current_language = App.get_running_app().language

        root = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=25
        )


        # TITLE
        self.title = Label(
            text= translations[self.current_language]["settings"],
            font_size="32sp",
            bold=True,
            size_hint_y=None,
            height=90
        )

        root.add_widget(self.title)


        # PROFILE
        self.profile_btn = ModernButton(
            text=translations[self.current_language]["profile"],
            icon="assets/icons/profile.png",
            size_hint_y=None,
            height=100
        )
        
        self.profile_btn.bind(
            on_press=self.open_profile
        )


        # LANGUAGE
        self.language_btn = ModernButton(
            text=translations[self.current_language]["language"],
            icon="assets/icons/language.png",
            size_hint_y=None,
            height=100
        )

        self.language_btn.bind(
            on_press=self.change_language
        )


        # BACKUP
        self.backup_btn = ModernButton(
            text=translations[self.current_language]["backup"],
            icon="assets/icons/backup.png",
            size_hint_y=None,
            height=100
        )
        
        self.backup_btn.bind(
            on_press=self.backup_database
        )
        
        #restore 
        self.restore_btn = ModernButton(
            text=translations[self.current_language]["restore"],
            icon="assets/icons/restore.png",
            size_hint_y=None,
            height=100
        )

        self.restore_btn.bind(
            on_press=self.restore_database
        )
     

        # CLEAR
        self.clear_btn = ModernButton(
            text=translations[self.current_language]["clear_transactions"],
            icon="assets/icons/clear.png",
            size_hint_y=None,
            height=100
        )
        
        self.clear_btn.bind(
            on_press=self.clear_transactions
        )


        # ABOUT
        self.about_btn = ModernButton(
            text=translations[self.current_language]["about"],
            icon="assets/icons/about.png",
            size_hint_y=None,
            height=100
        )

        self.about_btn.bind(
            on_press=self.open_about
        )


        # BACK
        self.back_btn = ModernButton(
            text=translations[self.current_language]["back"],
            icon="assets/icons/back.png",
            size_hint_y= None,
            height=100
         )

        self.back_btn.bind(
            on_press=self.go_home
        )


        # ADD BUTTONS
        root.add_widget(self.profile_btn)
        root.add_widget(self.language_btn)
        root.add_widget(self.backup_btn)
        root.add_widget(self.clear_btn)
        root.add_widget(self.restore_btn)
        root.add_widget(self.about_btn)
        root.add_widget(self.back_btn)


        self.add_widget(root)



    def go_home(self, instance):
        self.manager.current = "home"



    def open_about(self, instance):
        self.manager.current = "about"



    def change_language(self, instance):

        layout = BoxLayout(
            orientation="vertical",
            spacing=20,
            padding=10
        )


        popup = Popup(
            title="Choose language",
            content=layout,
            size_hint=(0.8,0.8)
        )


        languages = [
            ("Srpski", "sr"),
            ("English", "en"),
            ("Deutsch", "de"),
            ("Italiano", "it"),
            ("Español", "es"),
            ("Français", "fr"),
            ("Русский", "ru")
        ]


        for name, code in languages:

            btn = ModernButton(
                text=name,
                size_hint_y=None,
                height=70
            )

            btn.bind(
                on_press=lambda x, c=code:
                self.set_language(c, popup)
            )

            layout.add_widget(btn)


        cancel = ModernButton(
            text="Cancel",
            size_hint_y=None,
            height=70
        )

        cancel.bind(
            on_press=lambda x: popup.dismiss()
        )

        layout.add_widget(cancel)


        popup.open()



    def set_language(self, language, popup):

        app = App.get_running_app()

        from main import CURRENCIES

        app.language = language
        app.currency = CURRENCIES.get(language, "RSD")

        app.save_language()
 
        popup.dismiss()

        self.update_language()

        home = self.manager.get_screen("home")
        home.update_language()
        home.update_ui()

        self.manager.current = "home"

    def update_language(self):

        t = translations[App.get_running_app().language]

        self.title.text = t["settings"]

        self.profile_btn.text = t["profile"]
        self.language_btn.text = t["language"]
        self.backup_btn.text = t["backup"]
        self.restore_btn.text = t["restore"]
        self.clear_btn.text = t["clear_transactions"]
        self.about_btn.text = t["about"]
        self.back_btn.text = t["back"]
        
    def clear_transactions(self, instance):

        layout = BoxLayout(
            orientation="vertical",
            spacing=15,
            padding=15
        )
   
        layout.add_widget(
            Label(
                text="Are you sure you want to delete all transactions?",
                font_size="13sp"
            )
        )

        yes = ModernButton(
            text="Delete All",
            size_hint_y=None,
            height=70
        )

        no = ModernButton(
            text="Cancel",
            size_hint_y=None,
            height=70
        )

        layout.add_widget(yes)
        layout.add_widget(no)

        popup = Popup(
            title="Confirmation",
            content=layout,
            size_hint=(0.8, 0.4)
        )
 
        yes.bind(
            on_press=lambda x: self.confirm_delete(popup)
        )

        no.bind(
            on_press=lambda x: popup.dismiss()
        )

        popup.open()


    def confirm_delete(self, popup):

        popup.dismiss()

        home = self.manager.get_screen("home")

        home.db.delete_all_transactions()

        home.load_transactions()

        self.manager.current = "home"
        
    def open_profile(self, instance):
        self.manager.current = "profile"
        
    def backup_database(self, instance):
        try:
            import shutil
            import os
            from datetime import datetime

            os.makedirs("backup", exist_ok=True)

            source = "wallet.db"  # kasnije ćemo staviti pravi naziv

            print("Tražim bazu:", source)

            if not os.path.exists(source):
                print("Baza nije pronađena")
                Popup(
                    title="Backup",
                    content=Label(text="Database not found!"),
                    size_hint=(0.7, 0.3)
                ).open()
                return

            filename = datetime.now().strftime(
                "backup/WalletCore_Backup_%Y-%m-%d_%H-%M.db"
            )

            shutil.copy2(source, filename)

            Popup(
                title="Backup",
                content=Label(text="Backup OK"),
                size_hint=(0.7, 0.3)
            ).open()

        except Exception as e:
            Popup(
                title="Greška",
                content=Label(text=str(e)),
                size_hint=(0.8, 0.4)
            ).open()

    def restore_database(self, instance):

        import glob
        import shutil
        import os

        backups = sorted(
            glob.glob("backup/*.db"),
            reverse=True
        )

        if not backups:
            Popup(
                title="Restore",
                content=Label(text="No backup found."),
                size_hint=(0.7, 0.3)
            ).open()
            return

        latest = backups[0]

        shutil.copy2(latest, "wallet.db")

        home = self.manager.get_screen("home")
        home.load_transactions()

        Popup(
            title="Restore",
            content=Label(text="Database restored successfully!"),
            size_hint=(0.7, 0.3)
        ).open()
