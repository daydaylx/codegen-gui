from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QPlainTextEdit, QLineEdit, QCheckBox, QSpinBox, QStatusBar, QMessageBox,
    QSplitter, QFrame
)
from PySide6.QtCore import Qt
from ui.components.model_dropdown import ModelDropdown
from ui.components.prompt_input import PromptInput
from ui.components.code_output import CodeOutput
from core.settings_manager import load_settings, save_settings
from core.context_utils import get_available_output_tokens, is_prompt_within_limit
from api.openrouter import generate_code_streaming

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("💻 CodeGen Pro")
        self.setMinimumSize(1200, 800)

        # Theme laden
        try:
            with open("style_dark.qss", "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            pass

        self.settings = load_settings()
        self.sidebar_visible = True

        # === Zentrales Layout ===
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # Sidebar-Button links oben
        sidebar_button_layout = QVBoxLayout()
        self.sidebar_toggle = QPushButton("☰")
        self.sidebar_toggle.setFixedWidth(30)
        self.sidebar_toggle.clicked.connect(self.toggle_sidebar)
        sidebar_button_layout.addWidget(self.sidebar_toggle)
        sidebar_button_layout.addStretch()

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
        self.expert_toggle.setChecked(False)
        sidebar_layout.addWidget(self.expert_toggle)

        self.max_token_box = QSpinBox()
        self.max_token_box.setRange(100, 16000)
        self.max_token_box.setValue(800)
        sidebar_layout.addWidget(QLabel("Max Tokens"))
        sidebar_layout.addWidget(self.max_token_box)

        sidebar_layout.addStretch()

        self.generate_button = QPushButton("▶️ Code generieren")
        self.generate_button.clicked.connect(self.on_generate)
        sidebar_layout.addWidget(self.generate_button)

        # === Content ===
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

        # Layout-Zusammenbau
        main_layout.addLayout(sidebar_button_layout)
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(content_frame)

        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.setCentralWidget(main_widget)

    def toggle_sidebar(self):
        self.sidebar.setVisible(not self.sidebar.isVisible())

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

        self.statusBar().showMessage("⏳ Anfrage wird gestreamt …")

        self.code_output.set_output("")  # Reset
        try:
            for chunk in generate_code_streaming(user_prompt, model, system_prompt, max_tokens):
                self.code_output.append_output(chunk)
            self.statusBar().showMessage("✅ Antwort empfangen.")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", str(e))
            self.statusBar().showMessage("❌ Anfrage fehlgeschlagen.")
