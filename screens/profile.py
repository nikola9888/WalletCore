import os
import json
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.app import App
from kivy.uix.popup import Popup
from components.button import ModernButton
from components.rounded import RoundedInput
from kivy.uix.button import Button
from theme import TEXT, TITLE, CARD

PROFILE_FILE = "data/profile.json"

class ProfileScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )


        # =====================
        # TITLE
        # =====================

        title = Label(
            text="Profile",
            color=TEXT,
            font_size=32,
            bold=True,
            size_hint_y=None,
            height=70
        )

        root.add_widget(title)


        # =====================
        # PROFILE IMAGE
        # =====================

        self.avatar = Image(
            source="assets/icons/profile.png",
            size_hint=(None, None),
            size=(120,120)
        )

        avatar_box = BoxLayout(
            size_hint_y=None,
            height=130
        )

        avatar_box.add_widget(self.avatar)
        
        root.add_widget(avatar_box)



        # =====================
        # INPUTS
        # =====================

        self.name_input = RoundedInput(
            hint_text="Full Name",
            size_hint_y=None,
            height=100
        )

        self.email_input = RoundedInput(
            hint_text="Email",
            size_hint_y=None,
            height=100
        )


        self.country_input = RoundedInput(
            hint_text="Country",
            size_hint_y=None,
            height=100
        )


        self.currency_input = RoundedInput(
            hint_text="Currency",
            size_hint_y=None,
            height=100
        )


        root.add_widget(self.name_input)
        root.add_widget(self.email_input)
        root.add_widget(self.country_input)
        root.add_widget(self.currency_input)



        # =====================
        # SAVE BUTTON
        # =====================

        self.save_btn = ModernButton(
            text="💾 Save",
            size_hint_y=None,
            height=100
        )

        self.save_btn.bind(
            on_press=self.save_profile
        ) 


        # =====================
        # BACK BUTTON
        # =====================

        self.back_btn = ModernButton(
            text="⬅ Back",
            size_hint_y=None,
            height=100
        )

        self.back_btn.bind(
            on_press=self.go_back
        )


        root.add_widget(self.save_btn)
        root.add_widget(self.back_btn)


        self.add_widget(root)
        self.load_profile()



    # =====================
    # SAVE
    # =====================
    
    def save_profile(self, instance):

        profile = {
            "name": self.name_input.text,
            "email": self.email_input.text,
            "country": self.country_input.text,
            "currency": self.currency_input.text
        }

        os.makedirs("data", exist_ok=True)

        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=4, ensure_ascii=False)


        print("PROFILE SAVED")
        print(profile)
        self.show_saved()

    def show_saved(self):

        popup = Popup(
            title="Success",
            content=Label(
                text="Profile saved ✓",
                font_size="22sp"
            ),
            size_hint=(0.7,0.3)
        )

        popup.open()

    def load_profile(self):

        if os.path.exists(PROFILE_FILE):

            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                profile = json.load(f)


            self.name_input.text = profile.get("name", "")
            self.email_input.text = profile.get("email", "")
            self.country_input.text = profile.get("country", "")
            self.currency_input.text = profile.get("currency", "")


            print("PROFILE LOADED")

    # =====================
    # BACK
    # =====================

    def go_back(self, instance):

        self.manager.current = "settings"