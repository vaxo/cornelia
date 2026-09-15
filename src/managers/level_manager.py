from config.paths import LEVELS_FILE
from config.constants import NUM_LEVELS, LEVEL_DISTANCE
from src.utils.json_utils import load_json


class LevelManager:
    def __init__(self, save_manager):
        self.save = save_manager
        self._levels = load_json(LEVELS_FILE, [])
        self.current_level = 1
        self.distance_traveled = 0.0
        self.level_distance = LEVEL_DISTANCE

    def load_level(self, level_num):
        self.current_level = level_num
        self.distance_traveled = 0.0
        data = self.get_level_data(level_num)
        self.level_distance = data.get("distance", LEVEL_DISTANCE)

    def get_level_data(self, level_num):
        idx = level_num - 1
        if 0 <= idx < len(self._levels):
            return self._levels[idx]
        return {}

    def advance_distance(self, dx):
        self.distance_traveled += dx

    def is_finished(self):
        return self.distance_traveled >= self.level_distance

    def get_progress(self):
        return min(1.0, self.distance_traveled / self.level_distance)

    def unlock_next(self):
        next_lvl = self.current_level + 1
        self.save.unlock_level(self.current_level)
        if next_lvl <= NUM_LEVELS:
            if next_lvl > self.save.unlocked_level:
                self.save.unlocked_level = next_lvl
                self.save.save()

    def is_last_level(self):
        return self.current_level >= NUM_LEVELS
