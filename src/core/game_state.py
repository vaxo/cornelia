"""Named identifiers for the game's screens/scenes.

These match the keys registered in Game._register_screens so code can refer to
scenes by a symbolic name instead of a raw string literal.
"""


class GameState:
    MAIN_MENU = "main_menu"
    ENDLESS = "endless"
    LEVELS_MENU = "levels_menu"
    LEVEL_GAME = "level_game"
    CAR_SELECTION = "car_selection"
    SETTINGS = "settings"
    PAUSE = "pause"
    GAME_OVER = "game_over"
    LEVEL_COMPLETE = "level_complete"
