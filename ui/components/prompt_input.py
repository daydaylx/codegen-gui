from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QHBoxLayout, QPushButton, QFrame, QSizePolicy
)
from PySide6.QtCore import Signal, Qt # count_tokens Import entfernt

class PromptInput(QWidget):
    # prompt_changed Signal bleibt erhalten, da andere Teile der UI darauf reagieren könnten.
    # Für die Token-Anzeige im Hauptfenster sind die direkten Verbindungen zum textChanged-Signal in MainWindow ausreichend.
    prompt_changed = Signal()

    def __init__(self):
        super().__init__()
        self.user_prompt_input = QTextEdit() # Umbenannt von user_prompt, um Konflikte zu vermeiden und Klarheit zu schaffen
        self.user_prompt_input.setPlaceholderText("Was soll generiert werden?")
        self.user_prompt_input.setStyleSheet(self._style())
        self.user_prompt_input.textChanged.connect(self._on_text_changed) # Signal für Änderungen am Text

        self.system_prompt_input = QTextEdit() # Umbenannt von system_prompt
        self.system_prompt_input.setPlaceholderText("Systemprompt (optional)")
        self.system_prompt_input.setStyleSheet(self._style())
        self.system_prompt_input.setVisible(False)  # standardmäßig ausgeblendet
        self.system_prompt_input.textChanged.connect(self._on_text_changed) # Auch für System-Prompt Änderungen

        self.toggle_button = QPushButton("🧠 Systemprompt anzeigen")
        self.toggle_button.clicked.connect(self._toggle_system_prompt)

        # Token-Balken aus PromptInput entfernt, da er jetzt in MainWindow verwaltet wird
        # self.token_bar = QProgressBar()
        # ... (zugehöriger Code entfernt)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("📥 Eingabe-Prompt"))
        layout.addWidget(self.user_prompt_input)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.system_prompt_input)
        # layout.addWidget(self.token_bar) # Token-Balken entfernt
        self.setLayout(layout)

    def _toggle_system_prompt(self):
        visible = not self.system_prompt_input.isVisible() # Nutzt den umbenannten Namen
        self.system_prompt_input.setVisible(visible)
        self.toggle_button.setText("🔒 Systemprompt verbergen" if visible else "🧠 Systemprompt anzeigen")

    def _on_text_changed(self):
        # Die Token-Zählung und -Anzeige wird jetzt zentral in MainWindow.py verwaltet.
        # Dieses Signal dient dazu, MainWindow über Änderungen zu informieren.
        self.prompt_changed.emit()

    def get_user_prompt(self):
        return self.user_prompt_input.toPlainText()

    def get_system_prompt(self):
        return self.system_prompt_input.toPlainText()

    def _style(self):
        return """
        QTextEdit {
            background-color: #1e1e1e;
            color: #eee;
            font-family: 'Fira Code', monospace;
            font-size: 13px;
            border: 1px solid #444;
            border-radius: 6px;
            padding: 8px;
        }
        """
