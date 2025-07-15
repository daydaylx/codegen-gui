from PySide6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QLabel
from PySide6.QtCore import Signal

class ModelFilterWidget(QWidget):
    filter_changed = Signal(list)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        self.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QLabel("Modell-Filter"))

        self.free_checkbox = QCheckBox("🆓 Kostenlos")
        self.code_checkbox = QCheckBox("💻 Code")
        self.nsfw_checkbox = QCheckBox("🔞 NSFW")

        for cb in [self.free_checkbox, self.code_checkbox, self.nsfw_checkbox]:
            cb.stateChanged.connect(self.emit_filter)

        layout.addWidget(self.free_checkbox)
        layout.addWidget(self.code_checkbox)
        layout.addWidget(self.nsfw_checkbox)

        layout.addStretch()

    def emit_filter(self):
        filters = []
        if self.free_checkbox.isChecked():
            filters.append("free")
        if self.code_checkbox.isChecked():
            filters.append("code")
        if self.nsfw_checkbox.isChecked():
            filters.append("nsfw")

        self.filter_changed.emit(filters)
