def count_tokens(prompt: str, system: str = "") -> int:
    # Sehr einfache Token-Schätzung: ca. 1 Token pro 4 Zeichen
    return int((len(prompt) + len(system)) / 4)

def is_prompt_within_limit(prompt: str, system: str, model_id: str) -> bool:
    return count_tokens(prompt, system) < get_model_max_tokens(model_id)

def get_available_output_tokens(prompt: str, system: str, model_id: str) -> int:
    used = count_tokens(prompt, system)
    return get_model_max_tokens(model_id) - used

def get_model_max_tokens(model_id: str) -> int:
    MODEL_LIMITS = {
        "openai/gpt-3.5-turbo": 4096,
        "openai/gpt-4": 8192,
        "openrouter/auto": 4096,
    }

    # Fallback-Wert, wenn Modell nicht bekannt ist
    return MODEL_LIMITS.get(model_id, 4096)
