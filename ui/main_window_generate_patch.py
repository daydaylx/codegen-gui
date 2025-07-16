def on_generate(self):
    model = self.model_dropdown.get_selected_model()
    user_prompt = self.prompt_input.get_user_prompt()
    system_prompt = self.prompt_input.get_system_prompt()

    if not user_prompt.strip():
        QMessageBox.warning(self, "Fehlender Prompt", "Bitte gib einen Prompt ein.")
        return

    # Tokenlimit prüfen
    if not is_prompt_within_limit(user_prompt, system_prompt, model):
        QMessageBox.warning(self, "Tokenlimit überschritten", "Der Prompt ist zu lang.")
        return

    # API-Key + Settings speichern
    self.settings["api_key"] = self.api_input.text().strip()
    self.settings["last_model"] = model
    save_settings(self.settings)

    self.statusBar().showMessage("⏳ Anfrage wird gesendet …")

    try:
        # Expertenmodus: Manuelle Max Token
        if self.expert_toggle.isChecked():
            max_tokens = self.max_token_box.value()
        else:
            from core.context_utils import get_model_max_tokens
            model_max = get_model_max_tokens(model)
            used_tokens = len(user_prompt) + len(system_prompt)
            max_tokens = max(100, model_max - used_tokens)

        # Anfrage stellen
        result = generate_code(
            user_prompt=user_prompt,
            model=model,
            system_prompt=system_prompt,
            max_tokens=max_tokens
        )

        self.code_output.set_output(result)
        self.statusBar().showMessage("✅ Antwort erhalten.")
    except Exception as e:
        QMessageBox.critical(self, "Fehler", str(e))
        self.statusBar().showMessage("❌ Anfrage fehlgeschlagen.")
