import os
import json
from datetime import datetime

SESSION_DIR = "sessions"

os.makedirs(SESSION_DIR, exist_ok=True)

def save_session(session_data: dict):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(SESSION_DIR, f"session_{timestamp}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)
    return filename

def load_latest_session():
    files = sorted(
        [f for f in os.listdir(SESSION_DIR) if f.startswith("session_")],
        reverse=True
    )
    if not files:
        return None
    path = os.path.join(SESSION_DIR, files[0])
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def list_sessions():
    return sorted([f for f in os.listdir(SESSION_DIR) if f.startswith("session_")])
