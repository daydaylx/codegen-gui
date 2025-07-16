from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QPushButton, QTextEdit, QPlainTextEdit, QListWidget, QListWidgetItem,
    QLineEdit, QCheckBox, QFrame, QFileDialog, QMessageBox, QStatusBar, QSpinBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ui.components.model_dropdown import ModelDropdown
from ui.components.prompt_input import PromptInput
from ui.components.code_output import CodeOutput

from core.file_utils import save_text_to_file, copy_to_clipboard
from core.settings_manager import load_settings, save_settings
from core.context_utils import is_prompt_within_limit, get_available_output_tokens
from api.openrouter import generate_code_streaming

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("💻 CodeGen Pro")
        self.setMinimumSize(1200, 800)

        with open("style_dark.qss", "r") as f:
            self.setStyleSheet(f.read())

        self.settings = load_settings()

        # Layout: Sidebar + Content
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # === Sidebar ===
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(280)
        sidebar_layout = QVBoxLayout(self.sidebar)

        self.api_input = QLineEdit()
        self.api_input.setPlaceholderText("🔑 API-Key eingeben…")
        self.api_input.setText(self.settings.get("api_key", ""))
        sidebar_layout.addWidget(QLabel("API-Key"))
        sidebar_layout.addWidget(self.api_input)

        self.model_dropdown = ModelDropdown()
        sidebar_layout.addWidget(QLabel("Modell"))
        sidebar_layout.addWidget(self.model_dropdown)

        self.expert_toggle = QCheckBox("🛠️ Expertenmodus")
        sidebar_layout.addWidget(self.expert_toggle)

        self.max_token_box = QSpinBox()
        self.max_token_box.setRange(1, 32000)
        self.max_token_box.setValue(1024)
        sidebar_layout.addWidget(QLabel("Max Tokens (nur im Expertenmodus)"))
        sidebar_layout.addWidget(self.max_token_box)

        self.theme_toggle = QCheckBox("🌗 Dark Mode")
        self.theme_toggle.setChecked(self.settings.get("theme") == "dark")
        self.theme_toggle.stateChanged.connect(self.toggle_theme)
        sidebar_layout.addWidget(self.theme_toggle)

        sidebar_layout.addStretch()

        self.generate_button = QPushButton("▶️ Code generieren")
        self.generate_button.clicked.connect(self.on_generate)
        sidebar_layout.addWidget(self.generate_button)

        main_layout.addWidget(self.sidebar)

        # === Content Bereich ===
        content_frame = QFrame()
        content_frame.setObjectName("Content")
        content_layout = QVBoxLayout(content_frame)

        self.prompt_input = PromptInput()
        self.code_output = CodeOutput()

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.prompt_input)
        splitter.addWidget(self.code_output)
        splitter.setSizes([350, 450])

        content_layout.addWidget(splitter)
        main_layout.addWidget(content_frame)

        # === Statusbar ===
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        self.setCentralWidget(main_widget)

    def on_generate(self):
        model = self.model_dropdown.get_selected_model()
        user_prompt = self.prompt_input.get_user_prompt()
        system_prompt = self.prompt_input.get_system_prompt()

        if not user_prompt.strip():
            QMessageBox.warning(self, "Fehlender Prompt", "Bitte gib einen Prompt ein.")
            return

        if not is_prompt_within_limit(user_prompt, system_prompt, model):
            QMessageBox.warning(self, "Tokenlimit überschritten", "Der Prompt ist zu lang.")
            return

        if self.expert_toggle.isChecked():
            max_tokens = self.max_token_box.value()
        else:
            max_tokens = get_available_output_tokens(user_prompt, system_prompt, model)

        self.settings["api_key"] = self.api_input.text().strip()
        self.settings["last_model"] = model
        save_settings(self.settings)

        self.code_output.set_output("")
        self.statusBar().showMessage("⏳ Antwort wird gestreamt …")

        try:
            for chunk in generate_code_streaming(user_prompt, model, system_prompt, max_tokens):
                self.code_output.append_output(chunk)
            self.statusBar().showMessage("✅ Antwort vollständig.")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", str(e))
            self.statusBar().showMessage("❌ Anfrage fehlgeschlagen.")

    def toggle_theme(self):
        theme = "dark" if self.theme_toggle.isChecked() else "light"
        self.settings["theme"] = theme
        save_settings(self.settings)
        QMessageBox.information(self, "Theme gewechselt", "Bitte Anwendung neu starten für Theme-Wechsel.")
