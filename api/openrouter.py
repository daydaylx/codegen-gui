import requests
import json
from core.settings_manager import load_settings

OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"

class OpenRouterAPIError(Exception):
    pass

def get_models():
    API_KEY = load_settings().get("api_key", "")
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(OPENROUTER_MODELS_URL, headers=headers)

    if response.status_code != 200:
        raise OpenRouterAPIError(f"Modelle konnten nicht geladen werden: {response.status_code} {response.text}")

    return response.json()["data"]

def get_model_metadata(model_id):
    models = get_models()
    for model in models:
        if model["id"] == model_id:
            return model
    return {}

def generate_code_streaming(prompt, model, system_prompt="", max_tokens=None):
    API_KEY = load_settings().get("api_key", "")
    if not API_KEY:
        raise OpenRouterAPIError("❌ Kein API-Key gesetzt. Bitte in den Einstellungen eingeben.")

    from core.context_utils import get_available_output_tokens
    if max_tokens is None:
        max_tokens = get_available_output_tokens(prompt, system_prompt, model)

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    messages = [{"role": "system", "content": system_prompt}] if system_prompt else []
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "max_tokens": max_tokens
    }

    response = requests.post(OPENROUTER_CHAT_URL, headers=headers, json=payload, stream=True)

    if response.status_code != 200:
        raise OpenRouterAPIError(f"Fehler bei Anfrage: {response.status_code} {response.text}")

    for line in response.iter_lines():
        if line:
            try:
                if line.startswith(b"data: "):
                    line_data = json.loads(line[6:].decode("utf-8"))
                    content = line_data["choices"][0]["delta"].get("content", "")
                    yield content
            except Exception:
                continue
