import os
import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QComboBox, QSpinBox,
    QLabel, QStatusBar, QMessageBox, QCheckBox, QSlider, QListWidgetItem, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

# Eigene Komponenten importieren
from ui.components.prompt_input import PromptInput
from ui.components.code_output import CodeOutput
from ui.components.model_dropdown import ModelDropdown
from ui.components.session_list import SessionList
from ui.components.model_info_box import ModelInfoBox # Neu hinzugefügt

# Core-Module importieren
from core import settings_manager
from core import context_utils
from core import session_manager # Neu hinzugefügt
from api import openrouter

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CodeGen GUI")
        self.setGeometry(100, 100, 1200, 800)

        self.stream_iterator = None # Initialisieren des Stream-Iterators

        # --- UI-Komponenten initialisieren ---
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Geben Sie hier Ihren OpenRouter API-Schlüssel ein...")
        self.api_key_input.textChanged.connect(self.save_api_key_on_change) # Sofort speichern

        self.model_dropdown = ModelDropdown()
        self.model_dropdown.model_selected.connect(self.set_max_tokens_for_current_model) # Verbindung für Token-Update
        self.model_dropdown.model_selected.connect(self.update_model_info_box) # Verbindung für ModelInfoBox

        self.prompt_input = PromptInput()
        # Die folgenden Zeilen wurden angepasst, um die neuen Namen in prompt_input.py zu verwenden
        self.prompt_input.user_prompt_input.textChanged.connect(self.update_token_progress)
        self.prompt_input.system_prompt_input.textChanged.connect(self.update_token_progress)


        self.code_output = CodeOutput()

        self.generate_button = QPushButton("Generieren")
        self.generate_button.clicked.connect(self.on_generate)

        self.theme_toggle_button = QPushButton("Theme wechseln")
        self.theme_toggle_button.clicked.connect(self.toggle_theme)

        self.expert_mode_toggle = QCheckBox("Expertenmodus")
        self.expert_mode_toggle.stateChanged.connect(self.toggle_expert_mode)

        self.max_token_label = QLabel("Max Tokens:")
        self.max_token_box = QSpinBox()
        self.max_token_box.setRange(1, 200000) # Großer Bereich, wird dynamisch angepasst
        self.max_token_box.setValue(4096)
        self.max_token_box.valueChanged.connect(self.update_token_progress)

        self.temperature_label = QLabel("Temperatur:")
        self.temperature_slider = QSlider(Qt.Horizontal)
        self.temperature_slider.setRange(0, 200) # Bereich von 0.00 bis 2.00
        self.temperature_slider.setValue(70) # Standardwert 0.70 * 100
        self.temperature_slider.setSingleStep(1)
        self.temperature_slider.setPageStep(10)
        self.temperature_value_label = QLabel("0.70") # Zeigt den aktuellen Wert an
        self.temperature_slider.valueChanged.connect(self.update_temperature_label)

        self.token_progress_bar = QLabel("Tokens: 0 / 4096 (0%)")
        self.token_progress_bar.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.token_progress_bar.setStyleSheet("QLabel { color: gray; }") # Standardfarbe

        self.session_list = SessionList()
        self.session_list.session_selected.connect(self.load_selected_session)

        self.save_session_button = QPushButton("Sitzung speichern")
        self.save_session_button.clicked.connect(self.save_current_session)

        self.model_info_box = ModelInfoBox() # Instanz der ModelInfoBox

        # --- Layouts erstellen ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Linke Sidebar (Einstellungen & Sessions)
        sidebar_layout = QVBoxLayout()
        sidebar_layout.addWidget(QLabel("API-Schlüssel:"))
        sidebar_layout.addWidget(self.api_key_input)
        sidebar_layout.addWidget(QLabel("Modell auswählen:"))
        sidebar_layout.addWidget(self.model_dropdown)
        sidebar_layout.addWidget(self.model_info_box) # Modell-Info-Box hier platzieren
        sidebar_layout.addWidget(self.expert_mode_toggle)

        # Expertenmodus-Einstellungen
        expert_settings_layout = QVBoxLayout()
        expert_settings_layout.addWidget(self.max_token_label)
        expert_settings_layout.addWidget(self.max_token_box)
        expert_settings_layout.addWidget(self.temperature_label)
        expert_settings_layout.addWidget(self.temperature_slider)
        expert_settings_layout.addWidget(self.temperature_value_label)
        sidebar_layout.addLayout(expert_settings_layout)

        sidebar_layout.addWidget(self.generate_button)
        sidebar_layout.addWidget(self.save_session_button)
        sidebar_layout.addWidget(self.theme_toggle_button)
        sidebar_layout.addStretch(1) # Füllt den restlichen Platz

        sidebar_layout.addWidget(QLabel("Gespeicherte Sitzungen:"))
        sidebar_layout.addWidget(self.session_list)


        main_layout.addLayout(sidebar_layout, 1) # Sidebar nimmt 1/3 der Breite

        # Hauptbereich (Prompts & Output)
        main_content_layout = QVBoxLayout()
        main_content_layout.addWidget(self.prompt_input)
        main_content_layout.addWidget(self.code_output)
        main_layout.addLayout(main_content_layout, 2) # Hauptbereich nimmt 2/3 der Breite

        # Statusleiste
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.addWidget(self.token_progress_bar, 1) # Token-Anzeige in der Statusleiste

        # --- Initialisierung & Laden von Einstellungen ---
        self.load_settings()
        self.session_list.load_sessions() # Laden der Sitzungen beim Start

        # Initialen Zustand des Expertenmodus setzen
        self.toggle_expert_mode(self.expert_mode_toggle.checkState())
        self.update_temperature_label(self.temperature_slider.value()) # Temperatur-Label initialisieren
        self.set_max_tokens_for_current_model() # Initial die Tokenanzahl setzen

        # Initial das Theme anwenden
        initial_theme = settings_manager.load_theme()
        self.apply_theme(initial_theme)
        self.theme_toggle_button.setText(f"{initial_theme.capitalize()} Mode")

    def load_settings(self):
        """Lädt API-Schlüssel und zuletzt gewähltes Modell aus den Einstellungen."""
        api_key = settings_manager.load_api_key()
        if api_key:
            self.api_key_input.setText(api_key)

        last_model_id = settings_manager.load_last_model()
        if last_model_id:
            self.model_dropdown.set_selected_model_by_id(last_model_id)
            self.update_model_info_box(last_model_id) # Aktualisieren der Modellinfo beim Laden

    def save_api_key_on_change(self):
        """Speichert den API-Schlüssel bei jeder Änderung im Eingabefeld."""
        api_key = self.api_key_input.text().strip()
        settings_manager.save_api_key(api_key)

    def on_generate(self):
        """Startet den Codegenerierungsprozess."""
        self.code_output.clear_output()
        # Anpassung an die neuen Namen der Prompt-Eingabefelder
        user_prompt = self.prompt_input.user_prompt_input.toPlainText()
        system_prompt = self.prompt_input.system_prompt_input.toPlainText()
        selected_model_id = self.model_dropdown.get_selected_model_id()
        api_key = self.api_key_input.text().strip()

        if not user_prompt:
            QMessageBox.warning(self, "Eingabefehler", "Der Benutzer-Prompt darf nicht leer sein.")
            return
        if not api_key:
            QMessageBox.warning(self, "API-Schlüssel", "Bitte geben Sie Ihren OpenRouter API-Schlüssel ein.")
            return
        if not selected_model_id:
            QMessageBox.warning(self, "Modellfehler", "Kein Modell ausgewählt.")
            return

        self.generate_button.setEnabled(False)
        self.generate_button.setText("Generiere...")
        self.status_bar.showMessage("Generiere Code...")

        # Hole die maximale Tokenanzahl basierend auf dem Expertenmodus
        max_tokens = self.max_token_box.value() if self.expert_mode_toggle.isChecked() else context_utils.get_model_max_tokens(selected_model_id)
        temperature_value = self.temperature_slider.value() / 100.0 if self.expert_mode_toggle.isChecked() else 0.7


        try:
            self.stream_iterator = openrouter.generate_code_streaming(
                model=selected_model_id,
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                api_key=api_key,
                max_tokens=max_tokens,
                temperature=temperature_value
            )
            self.process_stream()

        except openrouter.OpenRouterAPIError as e:
            QMessageBox.critical(self, "API-Fehler", f"Ein API-Fehler ist aufgetreten: {e}")
            self.reset_ui_after_generation()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Ein unerwarteter Fehler ist aufgetreten: {e}")
            self.reset_ui_after_generation()

    def process_stream(self):
        """Verarbeitet den Stream der API-Antwort."""
        try:
            chunk = next(self.stream_iterator)
            self.code_output.append_text(chunk)
            self.update_token_progress() # Token-Anzeige während des Streams aktualisieren
            QTimer.singleShot(10, self.process_stream) # Kurze Verzögerung, um UI-Ereignisse zu ermöglichen
        except StopIteration:
            # Stream beendet
            self.reset_ui_after_generation()
            self.status_bar.showMessage("Generierung abgeschlossen.")
            QMessageBox.information(self, "Erfolg", "Codegenerierung abgeschlossen!")
        except Exception as e:
            QMessageBox.critical(self, "Stream-Fehler", f"Ein Fehler beim Verarbeiten des Streams ist aufgetreten: {e}")
            self.reset_ui_after_generation()

    def reset_ui_after_generation(self):
        """Setzt die UI-Elemente nach Abschluss oder Fehler der Generierung zurück."""
        self.generate_button.setEnabled(True)
        self.generate_button.setText("Generieren")
        self.status_bar.showMessage("Bereit")
        self.stream_iterator = None # Iterator zurücksetzen

    def toggle_theme(self):
        """Schaltet das Theme zwischen 'dark' und 'light' um und wendet es dynamisch an."""
        current_theme = settings_manager.load_theme()
        new_theme = "light" if current_theme == "dark" else "dark"
        settings_manager.save_theme(new_theme)
        self.apply_theme(new_theme)

        # Aktualisieren Sie den Text des Buttons
        self.theme_toggle_button.setText(f"{new_theme.capitalize()} Mode")

    def apply_theme(self, theme: str):
        """Wendet das Stylesheet für das gegebene Theme auf die Anwendung an."""
        stylesheet_path = os.path.join(os.path.dirname(__file__), '..', 'themes', f'{theme}.qss')
        if os.path.exists(stylesheet_path):
            with open(stylesheet_path, 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())
        else:
            print(f"Warnung: Stylesheet für Theme '{theme}' nicht gefunden unter {stylesheet_path}. Standard-Theme wird verwendet.")
            # Fallback: Versuchen, ein leeres Stylesheet zu setzen, um Fehler zu vermeiden, falls die Datei fehlt
            self.setStyleSheet("")


    def toggle_expert_mode(self, state):
        """Schaltet den Expertenmodus um und zeigt/verbirgt zugehörige UI-Elemente."""
        is_expert_mode = bool(state)
        self.max_token_label.setVisible(is_expert_mode)
        self.max_token_box.setVisible(is_expert_mode)
        self.temperature_label.setVisible(is_expert_mode)
        self.temperature_slider.setVisible(is_expert_mode)
        self.temperature_value_label.setVisible(is_expert_mode)

        if not is_expert_mode:
            # Setzt max_token_box auf den Standardwert des Modells zurück, wenn der Expertenmodus deaktiviert wird
            self.set_max_tokens_for_current_model()
            self.update_temperature_label(70) # Setzt Temperatur auf 0.70 zurück (Wert 70 für 0.70)
            self.temperature_slider.setValue(70) # Setzt Slider auf 0.70 zurück

    def update_temperature_label(self, value):
        """Aktualisiert das Label für den Temperaturwert."""
        self.temperature_value_label.setText(f"{value / 100:.2f}")


    def set_max_tokens_for_current_model(self):
        """Setzt die max_token_box auf die Kontextlänge des aktuell ausgewählten Modells."""
        selected_model_id = self.model_dropdown.get_selected_model_id()
        model_context_length = context_utils.get_model_max_tokens(selected_model_id)

        # Nur setzen, wenn der Expertenmodus NICHT aktiv ist ODER wenn das Modell gewechselt wird
        # und der Expertenmodus nicht explizit eine manuelle Auswahl erlaubt.
        # Ein besseres Kriterium wäre hier, ob der Wert von max_token_box nicht manuell geändert wurde.
        # Vorerst lassen wir es so, damit der Wert bei Deaktivierung zurückgesetzt wird.
        if not self.expert_mode_toggle.isChecked():
            self.max_token_box.setValue(model_context_length)
        # Immer den Bereich der Spinbox anpassen
        self.max_token_box.setRange(1, model_context_length)
        self.update_token_progress() # Aktualisiert die Token-Anzeige


    def update_token_progress(self):
        """Aktualisiert die Token-Anzeige basierend auf Prompts und max_tokens."""
        # Anpassung an die neuen Namen der Prompt-Eingabefelder
        user_prompt = self.prompt_input.user_prompt_input.toPlainText()
        system_prompt = self.prompt_input.system_prompt_input.toPlainText()
        total_text = user_prompt + system_prompt

        # Eine sehr grobe Schätzung, da tiktoken nicht direkt hier ist.
        # Im Schnitt sind 4 Zeichen 1 Token für englische Texte.
        current_tokens = len(total_text) // 4
        # Wenn Sie tiktoken installieren, können Sie dies durch eine präzisere Zählung ersetzen:
        # try:
        #     import tiktoken
        #     encoding = tiktoken.encoding_for_model(self.model_dropdown.get_selected_model_id() or "gpt-3.5-turbo")
        #     current_tokens = len(encoding.encode(total_text))
        # except ImportError:
        #     current_tokens = len(total_text) // 4 # Fallback

        max_allowed_tokens = self.max_token_box.value()

        percentage = (current_tokens / max_allowed_tokens) * 100 if max_allowed_tokens > 0 else 0
        self.token_progress_bar.setText(f"Tokens: {current_tokens} / {max_allowed_tokens} ({percentage:.0f}%)")

        if percentage > 90:
            self.token_progress_bar.setStyleSheet("QLabel { color: orange; }")
        elif percentage >= 100:
            self.token_progress_bar.setStyleSheet("QLabel { color: red; }")
        else:
            self.token_progress_bar.setStyleSheet("QLabel { color: gray; }")

    def save_current_session(self):
        """Speichert die aktuelle Konversation und Generierung als Sitzung."""
        # Anpassung an die neuen Namen der Prompt-Eingabefelder
        user_prompt = self.prompt_input.user_prompt_input.toPlainText()
        system_prompt = self.prompt_input.system_prompt_input.toPlainText()
        model_id = self.model_dropdown.get_selected_model_id()
        generated_code = self.code_output.get_full_output()

        if not user_prompt and not system_prompt and not generated_code:
            QMessageBox.warning(self, "Sitzung speichern", "Es gibt nichts zu speichern. Prompts und/oder generierter Code sind leer.")
            return
        if not model_id:
            QMessageBox.warning(self, "Sitzung speichern", "Bitte wählen Sie ein Modell, bevor Sie die Sitzung speichern.")
            return

        session_manager.save_session(user_prompt, system_prompt, model_id, generated_code)
        QMessageBox.information(self, "Sitzung gespeichert", "Die aktuelle Sitzung wurde erfolgreich gespeichert.")
        self.session_list.load_sessions() # Sitzungsliste in der Sidebar aktualisieren


    def load_selected_session(self, timestamp: str):
        """Lädt eine ausgewählte Sitzung und füllt die UI-Elemente."""
        session_data = session_manager.load_session_by_timestamp(timestamp)
        if session_data:
            # Anpassung an die neuen Namen der Prompt-Eingabefelder
            self.prompt_input.user_prompt_input.setPlainText(session_data.get("user_prompt", ""))
            self.prompt_input.system_prompt_input.setPlainText(session_data.get("system_prompt", ""))
            # Versuchen, das Modell im Dropdown zu setzen. Wenn nicht gefunden, bleibt es beim aktuellen.
            model_to_load = session_data.get("model_id", "")
            if model_to_load:
                self.model_dropdown.set_selected_model_by_id(model_to_load)
            else:
                self.model_dropdown.set_selected_model_by_id("") # Kein Modell auswählen

            self.code_output.clear_output()
            self.code_output.append_text(session_data.get("generated_code", ""))
            self.status_bar.showMessage(f"Sitzung vom {timestamp} geladen.")
            self.update_token_progress()
        else:
            QMessageBox.warning(self, "Sitzung laden", "Die ausgewählte Sitzung konnte nicht geladen werden.")

    def update_model_info_box(self, model_id: str):
        """Aktualisiert die Modellinformationsbox basierend auf dem ausgewählten Modell."""
        model_data = None
        for data in self.model_dropdown.all_models: # Greift auf die vollständige Moddelliste aus dem Dropdown zu
            if data.get('id') == model_id:
                model_data = data
                break
        self.model_info_box.update_info(model_data)
