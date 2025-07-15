# openrouter.py – API mit Lazy-Key und optionaler Fehlerklasse

import httpx
from config import get_api_key
from core.prompt_builder import build_prompt

BASE_URL = "https://openrouter.ai/api/v1"

class OpenRouterAPIError(Exception):
    """Benutzerdefinierter Fehler für OpenRouter-Probleme."""
    pass

def get_headers():
    api_key = get_api_key()
    if not api_key:
        raise OpenRouterAPIError("❌ Kein API-Key gesetzt. Bitte in den Einstellungen eingeben.")

    return {
        "Authorization": f"Bearer " + api_key,
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "CodeGen GUI"
    }

def get_models():
    try:
        response = httpx.get(f"{BASE_URL}/models", headers=get_headers(), timeout=10)
        response.raise_for_status()
        return response.json()["data"]
    except httpx.HTTPError as e:
        raise OpenRouterAPIError(f"Fehler beim Laden der Modelle: {e}")

def generate_code(user_prompt, model, system_prompt="", max_tokens=2048, temperature=0.3, stop=None):
    payload = {
        "model": model,
        "messages": build_prompt(user_prompt, system_prompt),
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    if stop:
        payload["stop"] = stop

    try:
        response = httpx.post(f"{BASE_URL}/chat/completions", headers=get_headers(), json=payload, timeout=60)
        response.raise_for_status()
        choices = response.json().get("choices", [])
        if not choices:
            raise OpenRouterAPIError("Keine Antwort vom Modell erhalten.")
        return choices[0]["message"]["content"]
    except httpx.HTTPError as e:
        raise OpenRouterAPIError(f"Fehler bei Anfrage: {e}")
