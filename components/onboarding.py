from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle, Line


STEPS = [
    ("category_grid", "izaberite kategoriju"),
    ("amount_input", "unesite zeljenu cifru"),
    ("note_input", "unesite zeljeni opis"),
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

    target_name, message = STEPS[index]
    target = getattr(screen, target_name, None)

    if target is None:
        Clock.schedule_once(lambda dt: _show_step(screen, index + 1), 0.1)
        return

    highlight_color = (0.25, 0.85, 1, 0.38)
    highlight_state = {"rect": None, "line": None}

    def add_highlight(*args):
        remove_highlight()
        with target.canvas.after:
            Color(*highlight_color)
            highlight_state["rect"] = RoundedRectangle(
                pos=target.pos,
                size=target.size,
                radius=[dp(14)]
            )
            Color(0.45, 0.95, 1, 0.9)
            highlight_state["line"] = Line(
                rounded_rectangle=(
                    target.x,
                    target.y,
                    target.width,
                    target.height,
                    dp(14)
                ),
                width=1.6
            )

    def update_highlight(*args):
        if highlight_state["rect"] is not None:
            highlight_state["rect"].pos = target.pos
            highlight_state["rect"].size = target.size
        if highlight_state["line"] is not None:
            highlight_state["line"].rounded_rectangle = (
                target.x,
                target.y,
                target.width,
                target.height,
                dp(14)
            )

    def remove_highlight(*args):
        if highlight_state["rect"] is not None:
            try:
                target.canvas.after.remove(highlight_state["rect"])
            except Exception:
                pass
            highlight_state["rect"] = None
        if highlight_state["line"] is not None:
            try:
                target.canvas.after.remove(highlight_state["line"])
            except Exception:
                pass
            highlight_state["line"] = None

    add_highlight()
    target.bind(pos=update_highlight, size=update_highlight)

    content = BoxLayout(
        orientation="vertical",
        padding=(dp(14), dp(8), dp(14), dp(8)),
    )

    label = Label(
        text=message,
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
        background_color=(0.02, 0.10, 0.17, 0.30),
    )

    state = {"closed": False, "event": None}

    def position_popup(*args):
        try:
            x, y = target.to_window(target.x, target.y)
            popup.x = max(dp(8), min(x + (target.width - popup.width) / 2, Window.width - popup.width - dp(8)))

            if y + target.height + dp(12) + popup.height <= Window.height:
                popup.y = y + target.height + dp(12)
            else:
                popup.y = max(dp(8), y - popup.height - dp(12))
        except Exception:
            pass

    def close_popup(*args):
        if not state["closed"]:
            popup.dismiss()

    def on_touch(window, touch):
        close_popup()
        return True

    def on_open(*args):
        position_popup()
        Window.bind(on_touch_down=on_touch)
        state["event"] = Clock.schedule_once(close_popup, 2.0)

    def on_dismiss(*args):
        if state["closed"]:
            return

        state["closed"] = True
        Window.unbind(on_touch_down=on_touch)

        if state["event"] is not None:
            state["event"].cancel()

        target.unbind(pos=update_highlight, size=update_highlight)
        remove_highlight()

        if index + 1 < len(STEPS):
            Clock.schedule_once(lambda dt: _show_step(screen, index + 1), 0.05)
        else:
            App.get_running_app().store.put("onboarding", completed=True)

    popup.bind(on_open=on_open)
    popup.bind(on_dismiss=on_dismiss)
    popup.open()
