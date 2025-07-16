import requests
import json # Neu hinzugefügt

class OpenRouterAPIError(Exception):
    """Benutzerdefinierte Ausnahme für OpenRouter API-Fehler."""
    pass

def get_available_models(api_key: str) -> list[dict]:
    """Ruft die Liste der verfügbaren Modelle von der OpenRouter API ab."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://localhost",  # Ihre Anwendungs-URL
        "X-Title": "CodeGen GUI",  # Ihr Anwendungsname
    }
    try:
        response = requests.get("https://openrouter.ai/api/v1/models", headers=headers)
        response.raise_for_status()  # Löst HTTPError für Bad Responses (4xx oder 5xx) aus
        return response.json()['data']
    except requests.exceptions.RequestException as e:
        raise OpenRouterAPIError(f"Netzwerk- oder API-Fehler beim Abrufen der Modelle: {e}")

def generate_code_streaming(model: str, user_prompt: str, system_prompt: str, api_key: str, max_tokens: int, temperature: float = 0.7):
    """Generiert Code über die OpenRouter API mit Streaming."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://localhost",
        "X-Title": "CodeGen GUI",
    }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    data = {
        "model": model,
        "messages": messages,
        "stream": True,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            stream=True
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data: '):
                    json_data = decoded_line[len('data: '):].strip()
                    if json_data == '[DONE]':
                        break
                    try:
                        # SICHERHEITSFIX: json.loads() anstelle von eval() verwenden
                        event = json.loads(json_data)
                        if 'choices' in event and event['choices']:
                            delta = event['choices'][0]['delta']
                            if 'content' in delta:
                                yield delta['content']
                    except json.JSONDecodeError as e:
                        # Dies kann bei unvollständigen JSON-Zeilen passieren, was bei Streaming normal ist
                        # oder bei tatsächlichen Fehlern. Zum Debuggen kann ein print hier hilfreich sein.
                        # print(f"Fehler beim Decodieren von JSON-Stream-Chunk: {e} in Zeile: {json_data}")
                        continue # Überspringen Sie fehlerhafte JSON-Zeilen
    except requests.exceptions.RequestException as e:
        raise OpenRouterAPIError(f"Netzwerk- oder API-Fehler: {e}")

