# Neue Signatur:
def generate_code_streaming(prompt, model, system_prompt="", max_tokens=None):
    if max_tokens is None:
        from core.context_utils import get_available_output_tokens
        max_tokens = get_available_output_tokens(prompt, system_prompt, model)

    ...
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "max_tokens": max_tokens
    }
