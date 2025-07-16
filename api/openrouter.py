import requests
import sseclient
from config import get_api_key

class OpenRouterAPIError(Exception):
    pass

def get_models():
    api_key = get_api_key()
    headers = {
        "Authorization": f"Bearer " + api_key,
        "HTTP-Referer": "https://localhost",
        "X-Title": "CodeGen GUI"
    }
    response = requests.get("https://openrouter.ai/api/v1/models", headers=headers)
    if response.status_code != 200:
        raise OpenRouterAPIError(f"Modelle konnten nicht geladen werden: {response.text}")
    return response.json()["data"]

def generate_code_streaming(user_prompt: str, model: str, system_prompt: str = "", max_tokens: int = 1024):
    api_key = get_api_key()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "text/event-stream",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://localhost",
        "X-Title": "CodeGen GUI"
    }

    body = {
        "model": model,
        "stream": True,
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=body,
        stream=True
    )

    if response.status_code != 200:
        raise OpenRouterAPIError(f"Fehler bei Anfrage: {response.status_code} - {response.text}")

    client = sseclient.SSEClient(response)
    for event in client.events():
        if event.data.strip() == "[DONE]":
            break
        try:
            data = event.data
            chunk = eval(data)  # OpenRouter sendet rohes JSON – eval = quick & dirty (kann ersetzt werden)
            content = chunk["choices"][0]["delta"].get("content", "")
            if content:
                yield content
        except Exception as e:
            continue  # Ignoriere fehlerhafte Chunks
