import os
import json
from datetime import datetime

SESSIONS_FILE = os.path.join("data", "sessions.json")

def ensure_data_dir():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

def load_sessions():
    ensure_data_dir()
    with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_session_entry(prompt, response, model, system_prompt=""):
    ensure_data_dir()
    sessions = load_sessions()
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "model": model,
        "prompt": prompt,
        "system_prompt": system_prompt,
        "response": response
    }
    sessions.insert(0, entry)
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, indent=2, ensure_ascii=False)
