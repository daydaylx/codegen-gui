from PySide6.QtWidgets import QComboBox, QMessageBox
from PySide6.QtCore import Signal, Qt
from api import openrouter
from core import settings_manager

class ModelDropdown(QComboBox):
    model_selected = Signal(str) # Sendet die ID des ausgewählten Modells

    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_models = []
        self.current_filter_tags = [] # Speichert die aktuell angewendeten Filter-Tags
        self.current_nsfw_filter = False # Speichert den NSFW-Filterzustand
        self.current_free_filter = False # Speichert den Free-Filterzustand

        self.currentIndexChanged.connect(self._on_selection_changed)
        self.setPlaceholderText("Modelle werden geladen...")
        self.load_models()

    def load_models(self):
        """Lädt Modelle von OpenRouter und füllt das Dropdown."""
        api_key = settings_manager.load_api_key()
        if not api_key:
            self.addItem("Bitte API-Schlüssel eingeben, um Modelle zu laden")
            self.setEnabled(False)
            return

        self.setEnabled(True)
        self.clear()
        self.addItem("Lade Modelle...")
        try:
            self.all_models = openrouter.get_available_models(api_key)
            self.all_models.sort(key=lambda m: m.get('id', '')) # Sortieren nach ID
            self.filter_and_populate_models() # Modelle nach dem Laden filtern und anzeigen
        except openrouter.OpenRouterAPIError as e:
            self.addItem(f"Fehler beim Laden: {e}")
            QMessageBox.critical(self, "API-Fehler", f"Fehler beim Laden der Modelle: {e}")
        except Exception as e:
            self.addItem(f"Unerwarteter Fehler: {e}")
            QMessageBox.critical(self, "Fehler", f"Unerwarteter Fehler beim Laden der Modelle: {e}")

    def filter_and_populate_models(self):
        """Filtert Modelle basierend auf den aktuellen Filtern und füllt das Dropdown."""
        self.clear()
        filtered_models = []

        for model in self.all_models:
            model_tags = model.get('tags', [])
            model_id = model.get('id', '')
            model_pricing = model.get('pricing', {})
            is_free = model_pricing.get('prompt', 1) == 0 and model_pricing.get('completion', 1) == 0
            is_nsfw = "nsfw" in model_tags or "NSFW" in model_id.upper()

            match = True

            # Anwenden der Filter
            if self.current_free_filter and not is_free:
                match = False
            if self.current_nsfw_filter and not is_nsfw:
                match = False
            # Filterung nach Tags (z.B. "code" filter)
            if self.current_filter_tags:
                tag_match = False
                for tag_filter in self.current_filter_tags:
                    if tag_filter.lower() in [t.lower() for t in model_tags]:
                        tag_match = True
                        break
                if not tag_match:
                    match = False

            if match:
                filtered_models.append(model)

        if not filtered_models:
            self.addItem("Keine Modelle gefunden, die den Filtern entsprechen.")
            self.setEnabled(False)
            return
        else:
            self.setEnabled(True)

        for model in filtered_models:
            model_id = model.get('id', 'Unbekanntes Modell')
            self.addItem(model_id, userData=model_id) # Speichert die Modell-ID als UserData

        # Auswahl des zuvor gespeicherten Modells oder des ersten Modells
        last_model_id = settings_manager.load_last_model()
        if last_model_id and self.findData(last_model_id, Qt.UserRole) != -1:
            self.set_selected_model_by_id(last_model_id)
        elif filtered_models:
            self.set_selected_model_by_id(filtered_models[0].get('id'))

    def set_filters(self, free: bool = None, nsfw: bool = None, tags: list[str] = None):
        """Setzt die Filter für die Modellanzeige."""
        if free is not None:
            self.current_free_filter = free
        if nsfw is not None:
            self.current_nsfw_filter = nsfw
        if tags is not None:
            self.current_filter_tags = tags
        self.filter_and_populate_models()

    def get_selected_model_id(self) -> str:
        """Gibt die ID des aktuell ausgewählten Modells zurück."""
        return self.currentData(Qt.UserRole)

    def set_selected_model_by_id(self, model_id: str):
        """Wählt ein Modell im Dropdown-Menü anhand seiner ID aus."""
        index = self.findData(model_id, Qt.UserRole)
        if index != -1:
            self.setCurrentIndex(index)
        else:
            # Falls das Modell nicht in der aktuellen gefilterten Liste ist,
            # wählen wir das erste verfügbare Modell oder nichts.
            if self.count() > 0:
                self.setCurrentIndex(0)
            else:
                self.setCurrentIndex(-1) # Nichts ausgewählt
            print(f"Modell-ID '{model_id}' nicht im Dropdown gefunden oder gefiltert.")
        settings_manager.save_last_model(self.get_selected_model_id()) # Speichern des ausgewählten Modells


    def _on_selection_changed(self, index: int):
        """Wird aufgerufen, wenn sich die Auswahl im Dropdown ändert."""
        if index >= 0:
            selected_model_id = self.itemData(index, Qt.UserRole)
            if selected_model_id:
                self.model_selected.emit(selected_model_id)
                settings_manager.save_last_model(selected_model_id) # Speichern der Auswahl
        else:
            self.model_selected.emit("") # Nichts ausgewählt

