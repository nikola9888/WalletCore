import json
import os
import ssl
import threading
import urllib.error
import urllib.request

import certifi

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.storage.jsonstore import JsonStore

from components.my_ai_config import AI_API_URL
from kivy.app import App


class MyAIChat:
    def _get_wallet_context(self):
        """Build a compact, read-only snapshot from WalletCore's local database."""
        from collections import defaultdict
        from datetime import datetime
        from database import Database

        db = None
        try:
            db = Database()
            rows = db.get_all()
            app = App.get_running_app()
            income = 0.0
            expenses = 0.0
            by_category = defaultdict(float)
            by_month = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
            by_month_category = defaultdict(float)

            for row in rows:
                _transaction_id, amount, ttype, category, _note, time_value = row
                amount = float(amount or 0)
                category = str(category or "Ostalo")
                if ttype == "income":
                    income += amount
                elif ttype == "expense":
                    expenses += amount
                if ttype in ("income", "expense"):
                    by_category[(ttype, category)] += amount
                    month = str(time_value or "")[:7]
                    if len(month) == 7 and month[4] == "-":
                        by_month[month][ttype] += amount
                        by_month_category[(month, ttype, category)] += amount

            current_month = datetime.now().strftime("%Y-%m")
            months = {
                month: {
                    "income": round(values["income"], 2),
                    "expenses": round(values["expense"], 2)
                }
                for month, values in sorted(by_month.items())[-24:]
            }
            categories = [
                {"type": key[0], "category": key[1], "total": round(total, 2)}
                for key, total in sorted(by_category.items(), key=lambda item: item[1], reverse=True)[:30]
            ]
            current_categories = [
                {"type": key[1], "category": key[2], "total": round(total, 2)}
                for key, total in sorted(
                    (item for item in by_month_category.items() if item[0][0] == current_month),
                    key=lambda item: item[1],
                    reverse=True
                )[:30]
            ]
            recent = []
            for row in rows[:12]:
                transaction_id, amount, ttype, category, _note, time_value = row
                recent.append({
                    "id": transaction_id,
                    "amount": round(float(amount or 0), 2),
                    "type": ttype,
                    "category": str(category or "Ostalo"),
                    "date": str(time_value or "")
                })

            return {
                "currency": str(getattr(app, "currency", "RSD")),
                "language": str(getattr(app, "language", "sr")),
                "transaction_count": len(rows),
                "total_income": round(income, 2),
                "total_expenses": round(expenses, 2),
                "balance": round(income - expenses, 2),
                "current_month": current_month,
                "monthly_totals": months,
                "category_totals_all_time": categories,
                "category_totals_current_month": current_categories,
                "recent_transactions": recent,
                "access": "read_only"
            }
        except Exception as exc:
            return {
                "available": False,
                "error": "WalletCore podaci trenutno nisu dostupni: {}".format(type(exc).__name__)
            }
        finally:
            if db is not None:
                try:
                    db.close()
                except Exception:
                    pass

    """My AI chat popup using a private server-side API proxy."""

    def __init__(self):
        self.messages = []
        self.history_store = None

    def _load_history(self):
        """Load saved chat messages from the app's private local storage."""
        try:
            app = App.get_running_app()
            history_path = os.path.join(app.user_data_dir, "my_ai_history.json")
            self.history_store = JsonStore(history_path)
            if self.history_store.exists("conversation"):
                saved = self.history_store.get("conversation").get("messages", [])
                if isinstance(saved, list):
                    self.messages = [
                        {"role": item["role"], "content": item["content"]}
                        for item in saved[-100:]
                        if isinstance(item, dict)
                        and item.get("role") in ("user", "assistant")
                        and isinstance(item.get("content"), str)
                    ]
        except Exception as exc:
            print("My AI history load error:", type(exc).__name__)
            self.messages = []

    def _save_history(self):
        """Persist the conversation locally; no history is sent just by saving."""
        try:
            if self.history_store is not None:
                self.history_store.put("conversation", messages=self.messages[-100:])
        except Exception as exc:
            print("My AI history save error:", type(exc).__name__)

    def open(self):
        self._load_history()
        root = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(10)
        )

        top = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(42),
            spacing=dp(8)
        )
        title = Label(
            text="My AI",
            bold=True,
            font_size="20sp",
            halign="left"
        )
        title.bind(size=lambda widget, size: setattr(widget, "text_size", size))

        new_chat = Button(
            text="Novi razgovor",
            size_hint_x=None,
            width=dp(112)
        )
        top.add_widget(title)
        top.add_widget(new_chat)
        root.add_widget(top)

        scroll = ScrollView(do_scroll_x=False)
        chat = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(4),
            size_hint_y=None
        )
        chat.bind(minimum_height=chat.setter("height"))
        scroll.add_widget(chat)
        root.add_widget(scroll)

        entry_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            spacing=dp(8)
        )
        entry = TextInput(
            hint_text="Napiši poruku...",
            multiline=False,
            size_hint_x=1,
            padding=[dp(10), dp(12), dp(10), dp(10)]
        )
        send = Button(
            text="Pošalji",
            size_hint_x=None,
            width=dp(88)
        )
        entry_row.add_widget(entry)
        entry_row.add_widget(send)
        root.add_widget(entry_row)

        popup = Popup(
            title="My AI",
            content=root,
            size_hint=(0.94, 0.86),
            auto_dismiss=True
        )

        request_state = {"generation": 0, "busy": False}

        def add_message(text, sender):
            bubble = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                padding=dp(10)
            )
            bubble.bind(minimum_height=bubble.setter("height"))

            bubble_color = (
                (0.08, 0.24, 0.40, 1)
                if sender == "Ti"
                else (0.10, 0.15, 0.23, 1)
            )
            with bubble.canvas.before:
                Color(*bubble_color)
                bubble.bg = RoundedRectangle(
                    pos=bubble.pos,
                    size=bubble.size,
                    radius=[dp(12)]
                )

            bubble.bind(
                pos=lambda widget, *_: setattr(widget.bg, "pos", widget.pos),
                size=lambda widget, *_: setattr(widget.bg, "size", widget.size)
            )

            label = Label(
                text="{}: {}".format(sender, text),
                size_hint_y=None,
                halign="left",
                valign="middle",
                color=(1, 1, 1, 1),
                font_size="15sp"
            )
            label.bind(
                width=lambda widget, width: setattr(
                    widget,
                    "text_size",
                    (max(width - dp(4), dp(20)), None)
                ),
                texture_size=lambda widget, size: setattr(
                    widget,
                    "height",
                    size[1] + dp(6)
                )
            )
            bubble.add_widget(label)
            chat.add_widget(bubble)
            Clock.schedule_once(lambda *_: setattr(scroll, "scroll_y", 0), 0.08)
            return bubble

        def set_busy(busy):
            request_state["busy"] = busy
            send.disabled = busy
            entry.disabled = busy
            send.text = "..." if busy else "Pošalji"

        def confirm_wallet_action(action):
            action_type = action.get("type")
            amount = action.get("amount")
            category = action.get("category")
            note = action.get("note", "")

            if (
                action_type not in ("income", "expense")
                or isinstance(amount, bool)
                or not isinstance(amount, (int, float))
                or amount <= 0
                or amount > 1000000000
                or not isinstance(category, str)
                or not category.strip()
                or len(category.strip()) > 60
                or not isinstance(note, str)
                or len(note) > 300
            ):
                add_message("Predlog nije ispravan. Ništa nije upisano.", "My AI")
                return

            currency = getattr(App.get_running_app(), "currency", "RSD")
            kind_label = "Prihod" if action_type == "income" else "Trošak"
            content = BoxLayout(
                orientation="vertical",
                spacing=dp(8),
                padding=dp(12)
            )
            content.add_widget(Label(
                text="{}: {:,.2f} {}".format(kind_label, float(amount), currency).replace(",", " "),
                size_hint_y=None,
                height=dp(36)
            ))
            content.add_widget(Label(
                text="Kategorija: {}".format(category.strip()),
                size_hint_y=None,
                height=dp(32)
            ))
            content.add_widget(Label(
                text="Napomena: {}".format(note.strip() or "—"),
                size_hint_y=None,
                height=dp(42)
            ))
            content.add_widget(Label(
                text="Ništa se ne upisuje bez tvoje potvrde.",
                size_hint_y=None,
                height=dp(38)
            ))
            actions = BoxLayout(
                orientation="horizontal",
                spacing=dp(8),
                size_hint_y=None,
                height=dp(44)
            )
            confirm = Button(text="Potvrdi unos")
            cancel = Button(text="Otkaži")
            actions.add_widget(confirm)
            actions.add_widget(cancel)
            content.add_widget(actions)
            dialog = Popup(
                title="Potvrdi transakciju",
                content=content,
                size_hint=(0.9, None),
                height=dp(270),
                auto_dismiss=False
            )

            def cancel_proposal(*_):
                dialog.dismiss()
                add_message("Unos je otkazan. Transakcija nije upisana.", "My AI")

            def save_proposal(*_):
                confirm.disabled = True
                cancel.disabled = True
                db = None
                try:
                    from database import Database
                    db = Database()
                    db.add_ai_transaction(
                        amount,
                        action_type,
                        category,
                        note
                    )
                    result = "{} od {:,.2f} {} je upisan. Kategorija: {}.".format(
                        kind_label,
                        float(amount),
                        currency,
                        category.strip()
                    ).replace(",", " ")
                except Exception as exc:
                    result = "Upis nije uspeo ({}). Proveri istoriju transakcija.".format(
                        type(exc).__name__
                    )
                finally:
                    if db is not None:
                        try:
                            db.close()
                        except Exception:
                            pass
                dialog.dismiss()
                add_message(result, "My AI")

            confirm.bind(on_release=save_proposal)
            cancel.bind(on_release=cancel_proposal)
            dialog.open()

        def send_message(*_):
            user_text = entry.text.strip()
            if not user_text or request_state["busy"]:
                return

            if not AI_API_URL.strip():
                add_message(
                    "AI servis još nije podešen. Potrebno je postaviti backend "
                    "i upisati njegov URL u components/my_ai_config.py.",
                    "My AI"
                )
                return

            entry.text = ""
            add_message(user_text, "Ti")

            request_messages = list(self.messages[-40:])
            request_messages.append({"role": "user", "content": user_text})
            wallet_context = self._get_wallet_context()
            generation = request_state["generation"]
            set_busy(True)
            waiting_bubble = add_message("Pripremam odgovor...", "My AI")

            def do_request():
                answer = None
                error_text = None
                try:
                    payload = json.dumps(
                        {
                            "messages": request_messages,
                            "wallet_context": wallet_context
                        },
                        ensure_ascii=False
                    ).encode("utf-8")
                    request = urllib.request.Request(
                        AI_API_URL.strip(),
                        data=payload,
                        headers={
                            "Content-Type": "application/json",
                            "Accept": "application/json",
                            "User-Agent": "WalletCore-MyAI/1.0",
                        },
                        method="POST"
                    )
                    ssl_context = ssl.create_default_context(cafile=certifi.where())
                    with urllib.request.urlopen(
                        request,
                        timeout=45,
                        context=ssl_context
                    ) as response:
                        data = json.loads(response.read().decode("utf-8"))

                    answer = data.get("reply")
                    if not isinstance(answer, str) or not answer.strip():
                        error_text = data.get(
                            "error",
                            "AI servis nije vratio odgovor."
                        )
                    else:
                        answer = answer.strip()
                except urllib.error.HTTPError as exc:
                    try:
                        details = exc.read().decode("utf-8", errors="replace").strip()
                        try:
                            data = json.loads(details)
                        except Exception:
                            data = None

                        if isinstance(data, dict):
                            api_error = data.get("error")
                            if isinstance(api_error, dict):
                                api_error = api_error.get("message") or str(api_error)
                            if isinstance(api_error, str) and api_error.strip():
                                error_text = "HTTP {}: {}".format(
                                    exc.code,
                                    api_error.strip()[:300]
                                )
                            elif details:
                                error_text = "HTTP {}: {}".format(
                                    exc.code,
                                    details[:300]
                                )
                            else:
                                error_text = "AI servis je vratio HTTP grešku {}.".format(
                                    exc.code
                                )
                        elif details:
                            error_text = "HTTP {}: {}".format(
                                exc.code,
                                details[:300]
                            )
                        else:
                            error_text = "AI servis je vratio HTTP grešku {}.".format(
                                exc.code
                            )
                    except Exception as detail_exc:
                        error_text = "HTTP {} ({}).".format(
                            exc.code,
                            type(detail_exc).__name__
                        )
                except Exception as exc:
                    # Diagnostic text helps identify network/TLS/timeout issues.
                    error_text = "Greška povezivanja ({}): {}".format(
                        type(exc).__name__,
                        str(exc)[:180] or "bez dodatnih detalja"
                    )

                def finish_request(*_):
                    if generation != request_state["generation"]:
                        return
                    if waiting_bubble.parent is chat:
                        chat.remove_widget(waiting_bubble)
                    set_busy(False)

                    if answer:
                        self.messages.append({"role": "user", "content": user_text})
                        if answer.startswith("WALLET_ACTION:"):
                            try:
                                action = json.loads(answer[len("WALLET_ACTION:"):].strip())
                                if (
                                    action.get("type") not in ("income", "expense")
                                    or isinstance(action.get("amount"), bool)
                                    or not isinstance(action.get("amount"), (int, float))
                                    or action.get("amount") <= 0
                                    or not isinstance(action.get("category"), str)
                                    or not isinstance(action.get("note", ""), str)
                                ):
                                    raise ValueError("invalid proposal")
                                summary = "Predlog pripremljen. Pregledaj podatke i potvrdi unos u posebnom prozoru."
                                self.messages.append({"role": "assistant", "content": summary})
                                self.messages = self.messages[-100:]
                                self._save_history()
                                add_message(summary, "My AI")
                                confirm_wallet_action(action)
                            except Exception:
                                answer = "Nisam uspeo da napravim ispravan predlog. Ništa nije upisano. Navedi tip transakcije, iznos i kategoriju."
                                self.messages.append({"role": "assistant", "content": answer})
                                self.messages = self.messages[-100:]
                                self._save_history()
                                add_message(answer, "My AI")
                        else:
                            self.messages.append({"role": "assistant", "content": answer})
                            self.messages = self.messages[-100:]
                            self._save_history()
                            add_message(answer, "My AI")
                    else:
                        add_message(error_text or "Došlo je do greške.", "My AI")

                Clock.schedule_once(finish_request, 0)

            threading.Thread(target=do_request, daemon=True).start()

        def reset_chat(*_):
            request_state["generation"] += 1
            request_state["busy"] = False
            self.messages = []
            self._save_history()
            chat.clear_widgets()
            set_busy(False)
            add_message("Novi razgovor. Ja sam My AI.", "My AI")

        send.bind(on_release=send_message)
        entry.bind(on_text_validate=send_message)
        new_chat.bind(on_release=reset_chat)

        if self.messages:
            for saved_message in self.messages:
                sender = "Ti" if saved_message["role"] == "user" else "My AI"
                add_message(saved_message["content"], sender)
        else:
            add_message(
                "Zdravo! Ja sam My AI. Pošalji poruku da započnemo razgovor.",
                "My AI"
            )
        popup.open()
