# config.py – Lazy geladen beim Zugriff

from core.settings_manager import load_settings

def get_api_key():
    settings = load_settings()
    return settings.get("api_key", "")

def get_default_model():
    settings = load_settings()
    return settings.get("last_model", "openai/gpt-4o")
