import json
import os

LEADERBOARD_FILE = os.path.join(os.path.dirname(__file__), "leaderboard.json")
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

DEFAULT_SETTINGS = {
    "sound": True,
    "car_color": [0, 100, 255],
    "difficulty": "normal",
}


def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, encoding="utf-8") as f:
            return json.load(f)
    return []


def save_leaderboard(entries):
    entries = sorted(entries, key=lambda e: e["score"], reverse=True)[:10]
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)


def add_score(username, score, distance):
    lb = load_leaderboard()
    lb.append({"username": username, "score": score, "distance": int(distance)})
    save_leaderboard(lb)


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, encoding="utf-8") as f:
            data = json.load(f)
        s = dict(DEFAULT_SETTINGS)
        s.update(data)
        return s
    return dict(DEFAULT_SETTINGS)


def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
