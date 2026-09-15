import pygame
import sys
from config.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, UI_TEXT_DIM
from src.core.display import Display
from src.core.scene_manager import SceneManager
from src.core.event_handler import EventHandler
from src.managers.asset_manager import AssetManager
from src.managers.audio_manager import AudioManager
from src.managers.save_manager import SaveManager

from src.screens.main_menu_screen import MainMenuScreen
from src.screens.endless_screen import EndlessScreen
from src.screens.levels_menu_screen import LevelsMenuScreen
from src.screens.level_game_screen import LevelGameScreen
from src.screens.car_selection_screen import CarSelectionScreen
from src.screens.settings_screen import SettingsScreen
from src.screens.pause_screen import PauseScreen
from src.screens.game_over_screen import GameOverScreen
from src.screens.level_complete_screen import LevelCompleteScreen


class Game:
    def __init__(self):
        pygame.init()
        # Audio may be unavailable (e.g. headless / no output device); don't
        # let that stop the game from running.
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        except pygame.error:
            pass
        pygame.display.set_caption("Cornelia")

        self.save = SaveManager()
        self.display = Display(SCREEN_WIDTH, SCREEN_HEIGHT, self.save.settings.fullscreen)
        # Scenes draw onto the logical 1920x1080 canvas; Display scales it to the
        # display's native resolution (SCALED) and maps mouse input for us.
        self.screen = self.display.canvas

        self.clock = pygame.time.Clock()
        self.running = True

        self.assets = AssetManager()
        self.audio = AudioManager(self.save.settings)

        self.scene = SceneManager(self)
        self._events = EventHandler(self)

        self._register_screens()
        self.scene.change("main_menu")
        self.audio.play_music()

    def toggle_fullscreen(self):
        s = self.save.settings
        s.fullscreen = not s.fullscreen
        self.save.save_settings()
        self.display.toggle_fullscreen()
        self.screen = self.display.canvas
        return s.fullscreen

    def _register_screens(self):
        screens = {
            "main_menu":      MainMenuScreen(self),
            "endless":        EndlessScreen(self),
            "levels_menu":    LevelsMenuScreen(self),
            "level_game":     LevelGameScreen(self),
            "car_selection":  CarSelectionScreen(self),
            "settings":       SettingsScreen(self),
            "pause":          PauseScreen(self),
            "game_over":      GameOverScreen(self),
            "level_complete": LevelCompleteScreen(self),
        }
        for key, screen in screens.items():
            self.scene.register(key, screen)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)
            dt = min(dt, 50)  # cap to avoid spiral of death
            events = self._events.collect()
            self.audio.update(dt)
            self.scene.handle_events(events)
            self.scene.update(dt)
            self.scene.render(self.screen)
            fps_surf = self.assets.render_text(f"FPS: {int(self.clock.get_fps())}", 22, (255, 255, 255))
            self.screen.blit(fps_surf, (8, 8))
            self.display.present()
        pygame.quit()
        sys.exit()
