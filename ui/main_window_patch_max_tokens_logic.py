
# Innerhalb von on_generate(self), VOR dem Aufruf von generate_code_streaming(...):

    if self.expert_toggle.isChecked():
        max_tokens = self.max_token_box.value()
    else:
        from core.context_utils import get_available_output_tokens
        max_tokens = get_available_output_tokens(user_prompt, system_prompt, model)
