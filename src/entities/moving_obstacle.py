import random
import math
from src.entities.obstacle import Obstacle
from config.constants import SCREEN_HEIGHT, OBSTACLE_MIN_Y_EDGE


class MovingObstacle(Obstacle):
    TYPES = ["vertical", "pendulum"]

    def __init__(self, x, gap_size, gap_y=None):
        super().__init__(x, gap_size, gap_y)
        self.movement_type = random.choice(self.TYPES)
        self.movement_speed = random.uniform(1.5, 3.0)
        half = gap_size // 2
        min_center = OBSTACLE_MIN_Y_EDGE + half + 20
        max_center = SCREEN_HEIGHT - OBSTACLE_MIN_Y_EDGE - half - 20
        self.movement_range = random.randint(40, 80)
        self.center_y = float(self.gap_y)
        self._time = random.uniform(0, math.pi * 2)

    def update(self, dt, speed, time_scale=1.0):
        self.x -= speed
        self._time += self.movement_speed * 0.04 * time_scale
        if self.movement_type == "vertical":
            offset = math.sin(self._time) * self.movement_range
        else:
            offset = math.sin(self._time) * self.movement_range * 0.8
        new_gap_y = int(self.center_y + offset)
        half = self.gap_size // 2
        low = OBSTACLE_MIN_Y_EDGE + half
        high = SCREEN_HEIGHT - OBSTACLE_MIN_Y_EDGE - half
        new_gap_y = max(low, min(high, new_gap_y))
        self.gap_y = new_gap_y
        self.top_h = new_gap_y - half
        self.bot_y = new_gap_y + half
        self.bot_h = SCREEN_HEIGHT - self.bot_y
