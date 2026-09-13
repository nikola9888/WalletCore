from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup


STEPS = [
    "izaberite kategoriju",
    "unesite zeljenu cifru",
    "unesite zeljeni opis",
]


def install_onboarding(HomeScreen):
    original_init = HomeScreen.__init__

    def new_init(self, **kwargs):
        original_init(self, **kwargs)
        Clock.schedule_once(lambda dt: _start_onboarding(self), 0.5)

    HomeScreen.__init__ = new_init


def _start_onboarding(screen):
    app = App.get_running_app()

    try:
        if app.store.get("onboarding").get("completed", False):
            return
    except Exception:
        pass

    _show_step(screen, 0)


def _show_step(screen, index):
    if index >= len(STEPS):
        App.get_running_app().store.put("onboarding", completed=True)
        return

    content = BoxLayout(
        orientation="vertical",
        padding=(dp(14), dp(8), dp(14), dp(8)),
    )

    label = Label(
        text=STEPS[index],
        font_size="17sp",
        bold=True,
        color=(1, 1, 1, 0.95),
        halign="center",
        valign="middle",
    )
    label.bind(size=lambda widget, value: setattr(widget, "text_size", widget.size))
    content.add_widget(label)

    popup = Popup(
        title="",
        title_size=0,
        separator_height=0,
        content=content,
        size_hint=(0.72, None),
        height=dp(82),
        auto_dismiss=False,
        background_color=(0.02, 0.10, 0.17, 0.72),
    )

    state = {"closed": False, "event": None}

    def close_popup(*args):
        if not state["closed"]:
            popup.dismiss()

    def on_touch(window, touch):
        close_popup()
        return True

    def on_open(*args):
        Window.bind(on_touch_down=on_touch)
        state["event"] = Clock.schedule_once(close_popup, 2.0)

    def on_dismiss(*args):
        if state["closed"]:
            return

        state["closed"] = True
        Window.unbind(on_touch_down=on_touch)

        if state["event"] is not None:
            state["event"].cancel()

        if index + 1 < len(STEPS):
            Clock.schedule_once(lambda dt: _show_step(screen, index + 1), 0.05)
        else:
            App.get_running_app().store.put("onboarding", completed=True)

    popup.bind(on_open=on_open)
    popup.bind(on_dismiss=on_dismiss)
    popup.open()
