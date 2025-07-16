from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QMessageBox
from PySide6.QtGui import QFont, QClipboard, QTextDocument
from PySide6.QtCore import Qt # Importieren von Qt

from core.file_utils import save_text_to_file # Sicherstellen, dass save_text_to_file importiert ist
from core.highlighter import PygmentsHighlighter # Neu hinzugefügt

class CodeOutput(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        self.output_display.setFont(QFont("Fira Code", 10)) # Beispiel-Schriftart

        # Syntaxhervorhebung initialisieren
        self.highlighter = PygmentsHighlighter(self.output_display.document())

        self.layout.addWidget(self.output_display)

        # Buttons für Kopieren und Speichern
        button_layout = QHBoxLayout()
        self.copy_button = QPushButton("Kopieren")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        button_layout.addWidget(self.copy_button)

        self.save_button = QPushButton("Speichern als Datei")
        self.save_button.clicked.connect(self.save_code_to_file)
        button_layout.addWidget(self.save_button)
        button_layout.addStretch(1) # Sorgt dafür, dass Buttons links bleiben

        self.layout.addLayout(button_layout)

    def append_text(self, text: str):
        """Fügt Text zum Ausgabefeld hinzu."""
        self.output_display.insertPlainText(text)

    def clear_output(self):
        """Löscht den Inhalt des Ausgabefeldes."""
        self.output_display.clear()

    def get_full_output(self) -> str:
        """Gibt den gesamten Inhalt des Ausgabefeldes zurück."""
        return self.output_display.toPlainText()

    def copy_to_clipboard(self):
        """Kopiert den generierten Code in die Zwischenablage."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.output_display.toPlainText())
        QMessageBox.information(self, "Kopiert", "Code in die Zwischenablage kopiert!")

    def save_code_to_file(self):
        """Speichert den generierten Code in eine Datei."""
        code_content = self.output_display.toPlainText()
        if not code_content.strip():
            QMessageBox.warning(self, "Speichern", "Kein Code zum Speichern vorhanden.")
            return

        # save_text_to_file ist eine Funktion aus core.file_utils
        # Sie muss den Dateidialog selbst öffnen.
        success = save_text_to_file(code_content, "code.txt") # Standardname
        if success:
            QMessageBox.information(self, "Speichern", "Code erfolgreich gespeichert!")
        else:
            QMessageBox.warning(self, "Speichern", "Speichern fehlgeschlagen oder abgebrochen.")

