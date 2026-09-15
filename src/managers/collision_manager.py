"""Collision detection between the player car, obstacles and world bounds."""
from config.constants import SCREEN_HEIGHT

# The visible ground strip is drawn 52px tall at the bottom of the screen
# (see BackgroundManager). Touching it means the car has hit the ground.
GROUND_Y = SCREEN_HEIGHT - 52


class CollisionManager:
    @staticmethod
    def check_obstacle(car, obstacle_manager):
        """Return True if the car's hitbox overlaps any obstacle pillar."""
        car_rect = car.rect
        rects = obstacle_manager.get_rects()
        return car_rect.collidelist(rects) != -1

    @staticmethod
    def check_bounds(car):
        """Return True if the car has hit the ceiling or the ground."""
        r = car.rect
        return r.top <= 0 or r.bottom >= GROUND_Y
