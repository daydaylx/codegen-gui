import os
import json

# 🌍 Absoluter Pfad zur settings.json, egal von wo gestartet
SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", "settings.json")

def load_settings():
    if not os.path.exists(SETTINGS_PATH):
        return {}

    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("⚠️ Fehler beim Parsen der settings.json – Datei ist möglicherweise beschädigt.")
        return {}

def save_settings(settings: dict):
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"❌ Fehler beim Speichern: {e}")
