from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line


STEPS = [
    ("category_grid", "SELECT A CATEGORY"),
    ("amount_input", "ENTER THE AMOUNT"),
    ("note_input", "ENTER A NOTE"),
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

    state = {
        "finished": False,
        "event": None,
        "label": None,
        "overlay": None,
        "highlight_rect": None,
        "highlight_line": None,
        "popup": None,
        "popup_line": None,
    }

    # Strong dark translucent overlay over the rest of the screen.
    with screen.canvas.after:
        Color(0, 0, 0, 0.72)
        state["overlay"] = Rectangle(pos=(0, 0), size=Window.size)

    def remove_highlight(*args):
        if state["highlight_rect"] is not None:
            try:
                target.canvas.after.remove(state["highlight_rect"])
            except Exception:
                pass
            state["highlight_rect"] = None

        if state["highlight_line"] is not None:
            try:
                target.canvas.after.remove(state["highlight_line"])
            except Exception:
                pass
            state["highlight_line"] = None

    def add_highlight(*args):
        remove_highlight()
        with target.canvas.after:
            # Bright cyan glow so the selected element remains clearly visible.
            Color(0.25, 0.9, 1, 0.55)
            state["highlight_rect"] = RoundedRectangle(
                pos=(target.x - dp(3), target.y - dp(3)),
                size=(target.width + dp(6), target.height + dp(6)),
                radius=[dp(16)],
            )
            Color(0.45, 0.95, 1, 1)
            state["highlight_line"] = Line(
                rounded_rectangle=(
                    target.x - dp(3),
                    target.y - dp(3),
                    target.width + dp(6),
                    target.height + dp(6),
                    dp(16),
                ),
                width=4.0,
            )

    def update_highlight(*args):
        if state["highlight_rect"] is not None:
            state["highlight_rect"].pos = (
                target.x - dp(3),
                target.y - dp(3),
            )
            state["highlight_rect"].size = (
                target.width + dp(6),
                target.height + dp(6),
            )

        if state["highlight_line"] is not None:
            state["highlight_line"].rounded_rectangle = (
                target.x - dp(3),
                target.y - dp(3),
                target.width + dp(6),
                target.height + dp(6),
                dp(16),
            )

    def update_overlay(*args):
        if state["overlay"] is not None:
            state["overlay"].pos = (0, 0)
            state["overlay"].size = Window.size

    add_highlight()
    target.bind(pos=update_highlight, size=update_highlight)
    Window.bind(size=update_overlay)

    # Smaller, bright white, highly rounded instruction popup.
    label = Label(
        text=message,
        font_size="17.9sp",
        bold=True,
        color=(0, 0, 0, 1),
        halign="center",
        valign="middle",
        size_hint=(None, None),
        size=(dp(280), dp(54)),
        text_size=(dp(260), dp(46)),
        padding=(dp(8), dp(4)),
    )
    state["label"] = label

    with label.canvas.before:
        Color(1, 1, 1, 0.88)
        state["popup"] = RoundedRectangle(
            pos=label.pos,
            size=label.size,
            radius=[dp(20)],
        )
        Color(1, 1, 1, 0.45)
        state["popup_line"] = Line(
            rounded_rectangle=(
                label.x,
                label.y,
                label.width,
                label.height,
                dp(20),
            ),
            width=1.0,
        )

    screen.add_widget(label)

    def update_popup(*args):
        if state["popup"] is not None:
            state["popup"].pos = label.pos
            state["popup"].size = label.size
        if state["popup_line"] is not None:
            state["popup_line"].rounded_rectangle = (
                label.x,
                label.y,
                label.width,
                label.height,
                dp(20),
            )

    label.bind(pos=update_popup, size=update_popup)

    def position_label(*args):
        try:
            x, y = target.to_window(target.x, target.y)
            label.x = max(
                dp(5),
                min(
                    x + (target.width - label.width) / 2,
                    Window.width - label.width - dp(5),
                ),
            )

            if target_name == "category_grid":
                label.y = max(dp(4), y - label.height - dp(6))
            else:
                above = y + target.height + dp(8)
                below = y - label.height - dp(8)
                if above + label.height <= Window.height - dp(4):
                    label.y = above
                else:
                    label.y = max(dp(4), below)
        except Exception:
            pass

    position_label()
    target.bind(pos=position_label, size=position_label)

    def finish_step(*args):
        if state["finished"]:
            return

        state["finished"] = True
        Window.unbind(on_touch_down=on_touch)
        Window.unbind(size=update_overlay)
        target.unbind(pos=update_highlight, size=update_highlight)
        target.unbind(pos=position_label, size=position_label)
        label.unbind(pos=update_popup, size=update_popup)

        if state["event"] is not None:
            state["event"].cancel()

        remove_highlight()

        if state["overlay"] is not None:
            try:
                screen.canvas.after.remove(state["overlay"])
            except Exception:
                pass
            state["overlay"] = None

        if state["label"] is not None:
            try:
                screen.remove_widget(state["label"])
            except Exception:
                pass
            state["label"] = None

        if index + 1 < len(STEPS):
            Clock.schedule_once(lambda dt: _show_step(screen, index + 1), 0.05)
        else:
            App.get_running_app().store.put("onboarding", completed=True)

    def on_touch(window, touch):
        finish_step()
        return False

    Window.bind(on_touch_down=on_touch)
    state["event"] = Clock.schedule_once(finish_step, 4.0)
