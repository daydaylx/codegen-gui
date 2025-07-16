# core/context_utils.py
# Kontext-Tools für Tokenzählung und Promptvalidierung

try:
    import tiktoken
    def count_tokens(user_prompt: str, system_prompt: str = "", model: str = "gpt-3.5-turbo") -> int:
        combined = (system_prompt + "\n" + user_prompt).strip()
        enc = tiktoken.encoding_for_model(model)
        return len(enc.encode(combined))
except ImportError:
    def count_tokens(user_prompt: str, system_prompt: str = "", model: str = "gpt-3.5-turbo") -> int:
        # Fallback ohne tiktoken
        approx = len((system_prompt + user_prompt).split())
        return int(approx * 1.3)

def is_prompt_within_limit(user_prompt: str, system_prompt: str = "", model: str = "gpt-3.5-turbo", limit: int = 8192) -> bool:
    return count_tokens(user_prompt, system_prompt, model) <= limit

def get_available_output_tokens(user_prompt, system_prompt, model_id):
    from api.openrouter import get_model_metadata
    from core.tokenizer import count_tokens  # oder dein Tokenizer-Modul

    meta = get_model_metadata(model_id)
    context_limit = meta.get("context_length", 4096)

    input_tokens = count_tokens(user_prompt) + count_tokens(system_prompt or "")
    buffer = 64  # Sicherheitsabstand
    max_output_tokens = max(context_limit - input_tokens - buffer, 256)

    return max_output_tokens
