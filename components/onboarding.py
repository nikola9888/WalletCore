from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.label import Label


STEPS = [
    ("category_grid", "Select a category"),
    ("amount_input", "Enter the amount"),
    ("note_input", "Enter a note"),
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

    label = Label(
        text=message,
        font_size="14sp",
        bold=True,
        color=(0.75, 0.95, 1, 1),
        halign="center",
        valign="middle",
        size_hint=(None, None),
        height=dp(24),
        opacity=1,
    )

    label.bind(size=lambda widget, value: setattr(widget, "text_size", widget.size))
    screen.add_widget(label)

    def position_label(*args):
        try:
            x, y = target.to_window(target.x, target.y)
            label_width = min(target.width, Window.width - dp(20))
            label.width = label_width
            label.x = max(
                dp(10),
                min(
                    x + (target.width - label.width) / 2,
                    Window.width - label.width - dp(10)
                )
            )

            if target_name == "category_grid":
                label.y = max(dp(4), y - dp(28))
            elif target_name == "amount_input":
                label.y = y + target.height + dp(2)
            else:
                label.y = max(dp(4), y - dp(28))
        except Exception:
            pass

    position_label()
    target.bind(pos=position_label, size=position_label)

    state = {"finished": False, "event": None}

    def finish_step(*args):
        if state["finished"]:
            return

        state["finished"] = True
        Window.unbind(on_touch_down=on_touch)

        if state["event"] is not None:
            state["event"].cancel()

        target.unbind(pos=position_label, size=position_label)
        screen.remove_widget(label)

        if index + 1 < len(STEPS):
            Clock.schedule_once(lambda dt: _show_step(screen, index + 1), 0.05)
        else:
            App.get_running_app().store.put("onboarding", completed=True)

    def on_touch(window, touch):
        finish_step()
        return False

    Window.bind(on_touch_down=on_touch)
    state["event"] = Clock.schedule_once(finish_step, 4.0)
