from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QSizePolicy
from PySide6.QtCore import Qt

class ModelInfoBox(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Modellinformationen", parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.title_label = QLabel("Kein Modell ausgewählt")
        self.provider_label = QLabel("Anbieter: N/A")
        self.description_label = QLabel("Beschreibung: N/A")
        self.context_length_label = QLabel("Kontextlänge: N/A")
        self.pricing_label = QLabel("Preise: N/A")
        self.features_label = QLabel("Merkmale: N/A")

        # Setzen von Textumbruch für längere Beschreibungen
        self.description_label.setWordWrap(True)
        # Beschreibungslabel sollte vertikal wachsen können
        self.description_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)


        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.provider_label)
        self.layout.addWidget(self.description_label)
        self.layout.addWidget(self.context_length_label)
        self.layout.addWidget(self.pricing_label)
        self.layout.addWidget(self.features_label)

        # Füllt den restlichen Platz in der Box
        self.layout.addStretch(1)

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding) # Passt die Höhe an den Inhalt an, erlaubt aber Expansion

        self.clear_info() # Initialen Zustand setzen

    def update_info(self, model_data: dict):
        """Aktualisiert die angezeigten Modellinformationen."""
        if not model_data:
            self.clear_info()
            return

        self.title_label.setText(f"<b>{model_data.get('id', 'N/A')}</b>")
        self.provider_label.setText(f"Anbieter: {model_data.get('creator', 'N/A')}")
        self.description_label.setText(f"Beschreibung: {model_data.get('description', 'N/A')}")
        self.context_length_label.setText(f"Kontextlänge: {model_data.get('context_length', 'N/A')} Token")

        # Preisinformationen formatieren und in float umwandeln
        pricing = model_data.get('pricing', {})
        try:
            # Konvertierung zu float hinzufügen, falls der Wert als String kommt
            prompt_cost = float(pricing.get('prompt', 0)) * 1_000_000 # Preis pro Million Token
            completion_cost = float(pricing.get('completion', 0)) * 1_000_000 # Preis pro Million Token
        except (ValueError, TypeError):
            prompt_cost = 0.0
            completion_cost = 0.0
            print(f"Warnung: Ungültiges Preisformat für Modell {model_data.get('id')}. Preise auf N/A gesetzt.")


        if prompt_cost > 0 or completion_cost > 0:
            self.pricing_label.setText(f"Preise (pro 1M Token): Input ${prompt_cost:.4f}, Output ${completion_cost:.4f}")
        else:
            self.pricing_label.setText("Preise: N/A (Kostenlos oder nicht angegeben)")

        # Merkmale (Tags) anzeigen
        tags = model_data.get('tags', [])
        if tags:
            self.features_label.setText(f"Merkmale: {', '.join(tags)}")
        else:
            self.features_label.setText("Merkmale: Keine angegeben")

    def clear_info(self):
        """Löscht alle angezeigten Modellinformationen."""
        self.title_label.setText("Kein Modell ausgewählt")
        self.provider_label.setText("Anbieter: N/A")
        self.description_label.setText("Beschreibung: N/A")
        self.context_length_label.setText("Kontextlänge: N/A")
        self.pricing_label.setText("Preise: N/A")
        self.features_label.setText("Merkmale: N/A")
