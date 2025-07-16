import json
import os

# Pfad zur Modellliste (Annahme: relativ zu diesem Skript)
_SCRIPT_DIR = os.path.dirname(__file__)
_MODEL_LISTING_PATH = os.path.join(_SCRIPT_DIR, '..', 'openrouter_models_complete_listing.json')

_MODELS_DATA = {}
if os.path.exists(_MODEL_LISTING_PATH):
    try:
        with open(_MODEL_LISTING_PATH, 'r', encoding='utf-8') as f:
            _MODELS_DATA = {model['id']: model for model in json.load(f)}
    except Exception as e:
        print(f"Fehler beim Laden der Modellliste aus {_MODEL_LISTING_PATH}: {e}")
else:
    print(f"Modellliste nicht gefunden: {_MODEL_LISTING_PATH}. Kontextlängen können ungenau sein.")


def get_model_max_tokens(model_id: str) -> int:
    """
    Gibt die maximale Tokenanzahl für ein gegebenes Modell zurück.
    Lädt die Kontextlänge aus der openrouter_models_complete_listing.json.
    """
    model_info = _MODELS_DATA.get(model_id)
    if model_info:
        return model_info.get('context_length', 4096) # Standardwert 4096, falls nicht gefunden
    return 4096 # Standardwert, wenn Modell nicht gefunden wird

# Die Funktion count_tokens ist aufgrund ihrer Ungenauigkeit entfernt, da keine präzise Tokenizer-Bibliothek (z.B. tiktoken) integriert ist.
# Für eine genauere Token-Zählung müsste eine entsprechende Bibliothek hinzugefügt werden.
