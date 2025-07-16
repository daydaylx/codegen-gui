import json
import os
from datetime import datetime

_SESSION_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'sessions.json')

def _load_all_sessions() -> list:
    """Lädt alle Sitzungen aus der zentralen JSON-Datei."""
    if not os.path.exists(_SESSION_FILE):
        return []
    try:
        with open(_SESSION_FILE, 'r', encoding='utf-8') as f:
            sessions = json.load(f)
            # Stellen Sie sicher, dass es eine Liste ist, falls die Datei leer oder korrupt ist
            if not isinstance(sessions, list):
                print(f"Warnung: Sitzungsdatei {_SESSION_FILE} enthält kein gültiges Listenformat. Wird zurückgesetzt.")
                return []
            return sessions
    except json.JSONDecodeError:
        print(f"Fehler beim Decodieren der Sitzungsdatei: {_SESSION_FILE}. Leere Liste wird zurückgegeben.")
        return []
    except Exception as e:
        print(f"Fehler beim Laden der Sitzungen aus {_SESSION_FILE}: {e}. Leere Liste wird zurückgegeben.")
        return []

def _save_all_sessions(sessions: list):
    """Speichert die Liste aller Sitzungen in der zentralen JSON-Datei."""
    # Sicherstellen, dass das 'data'-Verzeichnis existiert
    os.makedirs(os.path.dirname(_SESSION_FILE), exist_ok=True)
    with open(_SESSION_FILE, 'w', encoding='utf-8') as f:
        json.dump(sessions, f, indent=4, ensure_ascii=False)

def save_session(user_prompt: str, system_prompt: str, model_id: str, generated_code: str):
    """Speichert eine neue Sitzung."""
    sessions = _load_all_sessions()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    session_data = {
        "timestamp": timestamp,
        "model_id": model_id,
        "user_prompt": user_prompt,
        "system_prompt": system_prompt,
        "generated_code": generated_code
    }
    sessions.append(session_data)
    _save_all_sessions(sessions)
    print(f"Sitzung gespeichert: {timestamp}")

def list_sessions() -> list[dict]:
    """Gibt eine Liste aller gespeicherten Sitzungsmetadaten zurück."""
    sessions = _load_all_sessions()
    # Rückgabe einer gekürzten Version für die Anzeige in der Liste,
    # die volle Sitzung wird bei Bedarf geladen.
    return [{"timestamp": s.get("timestamp"), "model_id": s.get("model_id"), "user_prompt_snippet": s.get("user_prompt", "")[:50] + "..." if len(s.get("user_prompt", "")) > 50 else s.get("user_prompt", "")} for s in sessions]

def load_session_by_timestamp(timestamp: str) -> dict | None:
    """Lädt eine spezifische Sitzung anhand ihres Zeitstempels."""
    sessions = _load_all_sessions()
    for session in sessions:
        if session.get("timestamp") == timestamp:
            return session
    return None

def delete_session_by_timestamp(timestamp: str):
    """Löscht eine spezifische Sitzung anhand ihres Zeitstempels."""
    sessions = _load_all_sessions()
    initial_len = len(sessions)
    sessions = [s for s in sessions if s.get("timestamp") != timestamp]
    if len(sessions) < initial_len:
        _save_all_sessions(sessions)
        print(f"Sitzung mit Zeitstempel {timestamp} gelöscht.")
        return True
    print(f"Sitzung mit Zeitstempel {timestamp} nicht gefunden.")
    return False

