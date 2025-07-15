from PySide6.QtWidgets import QComboBox
from api.openrouter import get_models, OpenRouterAPIError

class ModelDropdown(QComboBox):
    def __init__(self):
        super().__init__()
        self.all_models = []
        self.current_filters = []
        self.refresh_models()

    def refresh_models(self):
        try:
            self.all_models = get_models()
            self.apply_filters()
        except OpenRouterAPIError as e:
            self.addItem(f"Fehler: {e}")

    def set_filters(self, filters: list):
        self.current_filters = filters
        self.apply_filters()

    def apply_filters(self):
        self.clear()
        for model in self.all_models:
            model_id = model["id"].lower()
            if not self.current_filters or any(self._model_matches_filter(model_id, f) for f in self.current_filters):
                self.addItem(model["id"])

    def _model_matches_filter(self, model_id: str, filter_type: str) -> bool:
        keywords = {
            "free": ["free", "ollama", "free", "openchat", "openhermes"],
            "code": ["code", "deepseek", "codellama", "starcoder", "wizardcoder"],
            "nsfw": ["nsfw", "uncensored", "raw", "capybara", "rawchat"]
        }
        return any(keyword in model_id for keyword in keywords.get(filter_type, []))

    def get_selected_model(self):
        return self.currentText()
