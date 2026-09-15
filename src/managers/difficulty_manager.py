from config.constants import (
    INITIAL_GAME_SPEED, MAX_GAME_SPEED, SPEED_RAMP_RATE,
    OBSTACLE_INITIAL_GAP, OBSTACLE_MIN_GAP,
    INITIAL_SPAWN_INTERVAL, MIN_SPAWN_INTERVAL,
    MOVING_SCORE_THRESHOLD,
)
from src.utils.math_utils import clamp


class DifficultyManager:
    def __init__(self):
        self.game_speed = INITIAL_GAME_SPEED
        self.gap = OBSTACLE_INITIAL_GAP
        self.spawn_interval = INITIAL_SPAWN_INTERVAL

    def reset(self, speed=None, gap=None, interval=None):
        self.game_speed = speed if speed is not None else INITIAL_GAME_SPEED
        self.gap = gap if gap is not None else OBSTACLE_INITIAL_GAP
        self.spawn_interval = interval if interval is not None else INITIAL_SPAWN_INTERVAL

    def update_endless(self, score):
        # Gradually ramp up speed
        ramp = score * SPEED_RAMP_RATE * 60
        self.game_speed = clamp(INITIAL_GAME_SPEED + ramp, INITIAL_GAME_SPEED, MAX_GAME_SPEED)
        # Shrink gap
        t = clamp((score - 0) / 200.0, 0, 1)
        self.gap = int(OBSTACLE_INITIAL_GAP - t * (OBSTACLE_INITIAL_GAP - OBSTACLE_MIN_GAP))
        # Increase spawn rate
        self.spawn_interval = clamp(
            INITIAL_SPAWN_INTERVAL - score * 5,
            MIN_SPAWN_INTERVAL,
            INITIAL_SPAWN_INTERVAL,
        )

    def get_speed(self):
        return self.game_speed

    def get_gap(self):
        return self.gap

    def get_spawn_interval(self):
        return self.spawn_interval

    def has_moving_obstacles_endless(self, score):
        return score >= MOVING_SCORE_THRESHOLD
