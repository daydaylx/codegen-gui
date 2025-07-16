import requests
import json
from core.settings_manager import load_settings

class OpenRouterAPIError(Exception):
    pass

BASE_URL = "https://openrouter.ai/api/v1"

def get_headers():
    settings = load_settings()
    api_key = settings.get("api_key", "")
    if not api_key:
        raise ValueError("❌ Kein API-Key gesetzt. Bitte in den Einstellungen eingeben.")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/daydaylx/codegen-gui",
        "X-Title": "CodeGen GUI"
    }

def get_models():
    response = requests.get(f"{BASE_URL}/models", headers=get_headers())
    if response.status_code != 200:
        raise OpenRouterAPIError(f"Fehler beim Laden der Modelle: {response.text}")
    return response.json()["data"]

def generate_code_streaming(user_prompt, model, system_prompt="", max_tokens=800):
    url = f"{BASE_URL}/chat/completions"
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "stream": True,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }

    with requests.post(url, headers=get_headers(), json=payload, stream=True) as r:
        if r.status_code != 200:
            raise OpenRouterAPIError(f"Fehler bei Anfrage: {r.status_code} – {r.text}")

        for line in r.iter_lines():
            if line and line.startswith(b'data: '):
                line_data = line[6:].decode("utf-8")
                if line_data.strip() == "[DONE]":
                    break
                try:
                    content = json.loads(line_data)["choices"][0]["delta"].get("content", "")
                    if content:
                        yield content
                except Exception:
                    continue
