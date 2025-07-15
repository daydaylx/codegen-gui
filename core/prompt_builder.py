# prompt_builder.py – Kombiniert User- und System-Prompt in OpenRouter-Format

from typing import List, Dict

def sanitize(text: str) -> str:
    """
    Entfernt problematische Steuerzeichen und trimmt den Text.
    """
    return text.replace("\r", "").strip()

def build_prompt(user_prompt: str, system_prompt: str = "") -> List[Dict[str, str]]:
    """
    Baut das message-Array für die OpenRouter API.
    """
    user_clean = sanitize(user_prompt)
    system_clean = sanitize(system_prompt)

    messages = []
    if system_clean:
        messages.append({"role": "system", "content": system_clean})
    messages.append({"role": "user", "content": user_clean})
    return messages
