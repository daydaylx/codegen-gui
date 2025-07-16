# Ergänzungen innerhalb von MainWindow.__init__(), im Sidebar-Bereich:

from PySide6.QtWidgets import QSpinBox

    # Expertenmodus
    self.expert_toggle = QCheckBox("🛠️ Expertenmodus")
    self.expert_toggle.setChecked(False)
    self.expert_toggle.stateChanged.connect(self.toggle_expert_mode)
    sidebar_layout.addWidget(self.expert_toggle)

    self.max_token_box = QSpinBox()
    self.max_token_box.setRange(128, 8192)
    self.max_token_box.setValue(2048)
    self.max_token_box.setSuffix(" max tokens")
    self.max_token_box.setVisible(False)
    sidebar_layout.addWidget(self.max_token_box)

def toggle_expert_mode(self):
    self.max_token_box.setVisible(self.expert_toggle.isChecked())
