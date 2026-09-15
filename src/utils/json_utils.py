"""Robust JSON load/save helpers.

Works cross-platform (Windows / macOS / Linux) and tolerates a missing,
empty, or corrupt file by falling back to the supplied default.
"""
import json
import os


def load_json(path, default=None):
    """Load JSON from *path*, returning *default* if it can't be read/parsed."""
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if not content:
            return default
        return json.loads(content)
    except (OSError, ValueError):
        return default


def save_json(path, data):
    """Write *data* as pretty UTF-8 JSON, creating parent dirs as needed."""
    try:
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except OSError:
        return False
