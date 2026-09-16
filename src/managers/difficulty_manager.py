from config.constants import (
    FPS, INITIAL_GAME_SPEED, MAX_GAME_SPEED, SPEED_RAMP_RATE,
    OBSTACLE_INITIAL_GAP, OBSTACLE_MIN_GAP,
    INITIAL_SPAWN_INTERVAL, MIN_SPAWN_INTERVAL,
    GAP_SHRINK_SCORE, SPAWN_INTERVAL_PER_SCORE, OBSTACLE_MIN_SPACING,
    MOVING_SCORE_THRESHOLD,
)
from src.utils.math_utils import clamp


def spacing_interval(speed):
    """Smallest spawn interval (ms) that still leaves OBSTACLE_MIN_SPACING px
    between consecutive obstacle pairs at *speed* px/frame.

    Obstacles move a fixed distance per frame, so a fixed spawn interval packs
    them closer and closer as the speed ramps up. Deriving the interval from the
    speed keeps the horizontal spacing constant however fast the run gets.
    """
    frames = OBSTACLE_MIN_SPACING / max(0.1, speed)
    return frames * (1000.0 / FPS)


class DifficultyManager:
    def __init__(self):
        self.game_speed = INITIAL_GAME_SPEED
        self.gap = OBSTACLE_INITIAL_GAP
        self.spawn_interval = INITIAL_SPAWN_INTERVAL

    def reset(self, speed=None, gap=None, interval=None):
        self.game_speed = speed if speed is not None else INITIAL_GAME_SPEED
        self.gap = gap if gap is not None else OBSTACLE_INITIAL_GAP
        interval = interval if interval is not None else INITIAL_SPAWN_INTERVAL
        self.spawn_interval = max(interval, spacing_interval(self.game_speed))

    def update_endless(self, score):
        # Gradually ramp up speed
        ramp = score * SPEED_RAMP_RATE * 60
        self.game_speed = clamp(INITIAL_GAME_SPEED + ramp, INITIAL_GAME_SPEED, MAX_GAME_SPEED)
        # Shrink gap (gently, and never below OBSTACLE_MIN_GAP)
        t = clamp(score / float(GAP_SHRINK_SCORE), 0, 1)
        self.gap = int(OBSTACLE_INITIAL_GAP - t * (OBSTACLE_INITIAL_GAP - OBSTACLE_MIN_GAP))
        # Increase spawn rate, but never past the horizontal spacing floor for
        # the speed we're now flying at.
        interval = clamp(
            INITIAL_SPAWN_INTERVAL - score * SPAWN_INTERVAL_PER_SCORE,
            MIN_SPAWN_INTERVAL,
            INITIAL_SPAWN_INTERVAL,
        )
        self.spawn_interval = max(interval, spacing_interval(self.game_speed))

    def get_speed(self):
        return self.game_speed

    def get_gap(self):
        return self.gap

    def get_spawn_interval(self):
        return self.spawn_interval

    def has_moving_obstacles_endless(self, score):
        return score >= MOVING_SCORE_THRESHOLD
