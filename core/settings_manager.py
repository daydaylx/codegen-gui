import os
import json

# 🌍 Absoluter Pfad zur settings.json, egal von wo gestartet
SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", "settings.json")
DEFAULT_THEME = "dark" # Standard-Theme festlegen
DEFAULT_MODEL = "openai/gpt-4o" # Standardmodell festlegen (wenn nichts anderes gespeichert ist)


def _load_settings() -> dict:
    """Lädt alle Einstellungen aus der settings.json."""
    if not os.path.exists(SETTINGS_PATH):
        return {}

    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("⚠️ Fehler beim Parsen der settings.json – Datei ist möglicherweise beschädigt oder leer. Wird zurückgesetzt.")
        return {}
    except Exception as e:
        print(f"❌ Fehler beim Laden der Einstellungen: {e}. Leere Einstellungen werden verwendet.")
        return {}

def _save_settings(settings: dict):
    """Speichert alle Einstellungen in der settings.json."""
    # Sicherstellen, dass das 'config'-Verzeichnis existiert
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Fehler beim Speichern der Einstellungen: {e}")

# --- Spezifische Lade-/Speicherfunktionen ---

def load_api_key() -> str:
    settings = _load_settings()
    return settings.get("api_key", "")

def save_api_key(api_key: str):
    settings = _load_settings()
    settings["api_key"] = api_key
    _save_settings(settings)

def load_last_model() -> str:
    settings = _load_settings()
    return settings.get("last_model", DEFAULT_MODEL)

def save_last_model(model_id: str):
    settings = _load_settings()
    settings["last_model"] = model_id
    _save_settings(settings)

def load_theme() -> str:
    settings = _load_settings()
    return settings.get("theme", DEFAULT_THEME)

def save_theme(theme: str):
    settings = _load_settings()
    settings["theme"] = theme
    _save_settings(settings)

