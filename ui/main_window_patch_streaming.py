from PySide6.QtWidgets import QMessageBox
from api.openrouter import generate_code_streaming, OpenRouterAPIError
from core.context_utils import is_prompt_within_limit
from core.settings_manager import save_settings
from PySide6.QtCore import QTimer

def on_generate(self):
    model = self.model_dropdown.get_selected_model()
    user_prompt = self.prompt_input.get_user_prompt()
    system_prompt = self.prompt_input.get_system_prompt()

    if not user_prompt.strip():
        QMessageBox.warning(self, "Fehlender Prompt", "Bitte gib einen Prompt ein.")
        return

    if not is_prompt_within_limit(user_prompt, system_prompt, model):
        QMessageBox.warning(self, "Tokenlimit überschritten", "Der Prompt ist zu lang.")
        return

    self.settings["api_key"] = self.api_input.text().strip()
    self.settings["last_model"] = model
    save_settings(self.settings)

    self.statusBar().showMessage("⏳ Streaming gestartet …")
    self.code_output.set_output("")

    def stream_response():
        try:
            for token in generate_code_streaming(user_prompt, model, system_prompt):
                self.code_output.append_output(token)
            self.statusBar().showMessage("✅ Antwort komplett empfangen.")
        except OpenRouterAPIError as e:
            QMessageBox.critical(self, "Fehler", str(e))
            self.statusBar().showMessage("❌ Anfrage fehlgeschlagen.")

    # Leicht verzögern, damit UI reagiert
    QTimer.singleShot(100, stream_response)
