
def on_generate(self):
    model = self.model_dropdown.get_selected_model()
    user_prompt = self.prompt_input.get_user_prompt()
    system_prompt = self.prompt_input.get_system_prompt()

    if not user_prompt.strip():
        QMessageBox.warning(self, "Fehlender Prompt", "Bitte gib einen Prompt ein.")
        return

    from core.context_utils import is_prompt_within_limit
    if not is_prompt_within_limit(user_prompt, system_prompt, model):
        QMessageBox.warning(self, "Tokenlimit überschritten", "Der Prompt ist zu lang.")
        return

    self.settings["api_key"] = self.api_input.text().strip()
    self.settings["last_model"] = model
    save_settings(self.settings)

    self.statusBar().showMessage("⏳ Anfrage wird gesendet …")

    # 🔧 Expertenmodus prüfen
    if self.expert_toggle.isChecked():
        max_tokens = self.max_token_box.value()
    else:
        from core.context_utils import get_available_output_tokens
        max_tokens = get_available_output_tokens(user_prompt, system_prompt, model)

    try:
        from api.openrouter import generate_code_streaming
        for chunk in generate_code_streaming(user_prompt, model, system_prompt, max_tokens):
            self.code_output.append_output(chunk)
        self.statusBar().showMessage("✅ Antwort erhalten.")
    except Exception as e:
        QMessageBox.critical(self, "Fehler", str(e))
        self.statusBar().showMessage("❌ Anfrage fehlgeschlagen.")
