from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel, QListWidgetItem
from core.session_manager import load_sessions

class SessionList(QWidget):
    def __init__(self, on_session_selected):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("📚 Verlauf"))

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.list_widget)

        self.on_session_selected = on_session_selected
        self.load_items()

    def load_items(self):
        self.sessions = load_sessions()
        self.list_widget.clear()
        for session in self.sessions:
            display = f"{session['timestamp']} | {session['model']}"
            item = QListWidgetItem(display)
            self.list_widget.addItem(item)

    def on_item_clicked(self, item):
        index = self.list_widget.row(item)
        session = self.sessions[index]
        self.on_session_selected(session)
