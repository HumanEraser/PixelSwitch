import os
import sys
import json
from datetime import datetime, date

SETTINGS_FILE = "settings.json"

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_default_folder():
    docs = os.path.join(os.path.expanduser("~"), "Documents", "PixelSwitch")
    os.makedirs(docs, exist_ok=True)
    return docs

def log_event(message):
    log_path = os.path.join(get_default_folder(), "log.txt")
    mode = "w" if os.path.exists(log_path) and date.fromtimestamp(os.path.getmtime(log_path)) < date.today() else "a"
    with open(log_path, mode, encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")

def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as f: 
            return json.load(f)
    except: 
        return {"theme": "System", "last_format": "JPG", "output_folder": get_default_folder()}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f: 
        json.dump(settings, f)