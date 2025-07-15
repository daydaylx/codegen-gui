from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QHBoxLayout, QPushButton, QFrame, QProgressBar, QSizePolicy
)
from PySide6.QtCore import Signal, Qt
from core.context_utils import count_tokens

class PromptInput(QWidget):
    prompt_changed = Signal()

    def __init__(self):
        super().__init__()
        self.user_prompt = QTextEdit()
        self.user_prompt.setPlaceholderText("Was soll generiert werden?")
        self.user_prompt.setStyleSheet(self._style())
        self.user_prompt.textChanged.connect(self._on_text_changed)

        self.system_prompt = QTextEdit()
        self.system_prompt.setPlaceholderText("Systemprompt (optional)")
        self.system_prompt.setStyleSheet(self._style())
        self.system_prompt.setVisible(False)  # standardmäßig ausgeblendet

        self.toggle_button = QPushButton("🧠 Systemprompt anzeigen")
        self.toggle_button.clicked.connect(self._toggle_system_prompt)

        self.token_bar = QProgressBar()
        self.token_bar.setRange(0, 8192)
        self.token_bar.setFormat("Tokens: %v")
        self.token_bar.setValue(0)
        self.token_bar.setTextVisible(True)
        self.token_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #333;
                border-radius: 4px;
                background: #222;
                color: #ccc;
            }
            QProgressBar::chunk {
                background-color: #05B8CC;
            }
        """)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("📥 Eingabe-Prompt"))
        layout.addWidget(self.user_prompt)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.system_prompt)
        layout.addWidget(self.token_bar)
        self.setLayout(layout)

    def _toggle_system_prompt(self):
        visible = not self.system_prompt.isVisible()
        self.system_prompt.setVisible(visible)
        self.toggle_button.setText("🔒 Systemprompt verbergen" if visible else "🧠 Systemprompt anzeigen")

    def _on_text_changed(self):
        tokens = count_tokens(self.get_user_prompt(), self.get_system_prompt())
        self.token_bar.setValue(tokens)
        self.prompt_changed.emit()

    def get_user_prompt(self):
        return self.user_prompt.toPlainText()

    def get_system_prompt(self):
        return self.system_prompt.toPlainText()

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
