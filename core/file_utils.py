# file_utils.py – Speichern, Kopieren etc.

from PySide6.QtWidgets import QFileDialog
from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import QApplication

def save_text_to_file(text: str):
    filename, _ = QFileDialog.getSaveFileName(None, "Speichern unter", "", "Textdateien (*.txt);;Python (*.py)")
    if filename:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)

def copy_to_clipboard(text: str):
    clipboard: QClipboard = QApplication.clipboard()
    clipboard.setText(text)
