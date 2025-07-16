from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtCore import Qt

class CodeOutput(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setFont(QFont("Courier", 10))
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")

    def set_output(self, text: str):
        self.setPlainText(text)
        self.moveCursor(QTextCursor.Start)

    def append_output(self, text: str):
        self.moveCursor(QTextCursor.End)
        self.insertPlainText(text)
        self.moveCursor(QTextCursor.End)
