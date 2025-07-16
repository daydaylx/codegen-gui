from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QMessageBox, QListWidgetItem
from PySide6.QtCore import Signal, Qt
from core import session_manager

class SessionList(QWidget):
    session_selected = Signal(str) # Signal, das den Zeitstempel der ausgewählten Sitzung sendet

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.session_list_widget = QListWidget()
        self.session_list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.layout.addWidget(self.session_list_widget)

        self.load_button = QPushButton("Sitzungen neu laden")
        self.load_button.clicked.connect(self.load_sessions)
        self.layout.addWidget(self.load_button)

        self.delete_button = QPushButton("Ausgewählte Sitzung löschen")
        self.delete_button.clicked.connect(self._delete_selected_session)
        self.layout.addWidget(self.delete_button)

        self.load_sessions() # Laden Sie die Sitzungen beim Start

    def load_sessions(self):
        """Lädt alle Sitzungen und zeigt sie in der Liste an."""
        self.session_list_widget.clear()
        sessions = session_manager.list_sessions()
        if not sessions:
            self.session_list_widget.addItem("Keine gespeicherten Sitzungen.")
            return

        # Sitzungen in umgekehrter Reihenfolge anzeigen (neueste zuerst)
        for session in reversed(sessions):
            timestamp = session.get("timestamp", "Unbekannt")
            model_id = session.get("model_id", "Unbekanntes Modell")
            snippet = session.get("user_prompt_snippet", "Kein Prompt-Ausschnitt")
            display_text = f"[{timestamp}] {model_id}: {snippet}"
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, timestamp) # Speichert den Zeitstempel im Item
            self.session_list_widget.addItem(item)

    def _on_item_double_clicked(self, item):
        """Wird aufgerufen, wenn ein Listenelement doppelt geklickt wird."""
        timestamp = item.data(Qt.UserRole)
        if timestamp and timestamp != "Keine gespeicherten Sitzungen.": # Vermeiden, wenn der Platzhalter geklickt wird
            self.session_selected.emit(timestamp) # Signal senden

    def _delete_selected_session(self):
        """Löscht die aktuell ausgewählte Sitzung."""
        selected_item = self.session_list_widget.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Löschen fehlgeschlagen", "Bitte wählen Sie eine Sitzung zum Löschen aus.")
            return

        timestamp_to_delete = selected_item.data(Qt.UserRole)
        if timestamp_to_delete and timestamp_to_delete != "Keine gespeicherten Sitzungen.":
            reply = QMessageBox.question(self, "Sitzung löschen",
                                        f"Möchten Sie die Sitzung vom {timestamp_to_delete} wirklich löschen?",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                if session_manager.delete_session_by_timestamp(timestamp_to_delete):
                    self.load_sessions() # Liste nach dem Löschen neu laden
                    QMessageBox.information(self, "Erfolg", "Sitzung erfolgreich gelöscht.")
                else:
                    QMessageBox.critical(self, "Fehler", "Sitzung konnte nicht gelöscht werden. Möglicherweise nicht gefunden.")
        else:
            QMessageBox.warning(self, "Löschen fehlgeschlagen", "Keine gültige Sitzung zum Löschen ausgewählt.")

