from config.paths import SAVE_FILE
from config.settings import Settings
from src.utils.json_utils import load_json, save_json


class SaveManager:
    def __init__(self):
        self.high_score = 0
        self.selected_car = "camry"
        self.selected_color = "წითელი"
        self.settings = Settings()
        self.unlocked_level = 1
        self.completed_levels = []
        self.load()

    def load(self):
        data = load_json(SAVE_FILE, {})
        self.high_score = data.get("high_score", 0)
        self.selected_car = data.get("selected_car", "camry")
        self.selected_color = data.get("selected_color", "წითელი")
        s = data.get("settings", {})
        self.settings.from_dict(s)
        lvl = data.get("levels", {})
        self.unlocked_level = lvl.get("unlocked_level", 1)
        self.completed_levels = lvl.get("completed_levels", [])

    def save(self):
        data = {
            "high_score": self.high_score,
            "selected_car": self.selected_car,
            "selected_color": self.selected_color,
            "settings": self.settings.to_dict(),
            "levels": {
                "unlocked_level": self.unlocked_level,
                "completed_levels": self.completed_levels,
            },
        }
        save_json(SAVE_FILE, data)

    def update_high_score(self, score):
        if score > self.high_score:
            self.high_score = score
            self.save()

    def save_selected_car(self, model, color):
        self.selected_car = model
        self.selected_color = color
        self.save()

    def save_settings(self):
        self.save()

    def unlock_level(self, level_num):
        if level_num > self.unlocked_level:
            self.unlocked_level = level_num
        if level_num not in self.completed_levels:
            self.completed_levels.append(level_num)
        self.save()

    def is_level_unlocked(self, level_num):
        return level_num <= self.unlocked_level
