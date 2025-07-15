from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtGui import QFont, QTextOption

class CodeOutput(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.setFont(QFont("Fira Code", 11))
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-family: 'Fira Code', monospace;
                font-size: 13px;
                border-radius: 8px;
                padding: 10px;
                border: 1px solid #444;
            }
        """)

    def set_output(self, text: str):
        self.setPlainText(text)

    def clear_output(self):
        self.setPlainText("")

    def get_output(self) -> str:
        return self.toPlainText()
