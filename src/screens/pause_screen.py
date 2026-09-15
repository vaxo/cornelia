import pygame
from src.screens.base_screen import BaseScreen
from src.ui.button import Button
from config.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BTN_W, BTN_H, BTN_SPACING,
    UI_TEXT, UI_GOLD, UI_PANEL, UI_ACCENT,
)


class PauseScreen(BaseScreen):
    def __init__(self, game):
        super().__init__(game)
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2
        self._from_screen = "endless"
        self._level = 1
        self.buttons = [
            Button(cx, cy - BTN_SPACING,     BTN_W, BTN_H, "გაგრძელება",   self.assets),
            Button(cx, cy,                   BTN_W, BTN_H, "თავიდან",       self.assets),
            Button(cx, cy + BTN_SPACING,     BTN_W, BTN_H, "მთავარი მენიუ", self.assets),
            Button(cx, cy + BTN_SPACING * 2, BTN_W, BTN_H, "გასვლა",        self.assets),
        ]

    def on_enter(self, from_screen="endless", level=1, **kwargs):
        self._from_screen = from_screen
        self._level = level

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.update(mouse_pos)
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._resume()
            for btn in self.buttons:
                if btn.handle_event(event):
                    self.audio.play_sfx("click")
                    if btn.text == "გაგრძელება":
                        self._resume()
                    elif btn.text == "თავიდან":
                        if self._from_screen == "level_game":
                            self.game.scene.change("level_game", level=self._level)
                        else:
                            self.game.scene.change("endless")
                    elif btn.text == "მთავარი მენიუ":
                        self.game.scene.change("main_menu")
                    elif btn.text == "გასვლა":
                        self.game.running = False

    def _resume(self):
        self.game.scene.change(self._from_screen, resume=True, level=self._level)

    def render(self, surface):
        # Draw the frozen gameplay underneath so pause reads as an overlay on the
        # live game (its state isn't updated while paused, so this is a still frame).
        game_screen = self.game.scene.get(self._from_screen)
        if game_screen is not None:
            game_screen.render(surface)

        # Semi-transparent dim over the game
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 8, 25, 150))
        surface.blit(overlay, (0, 0))

        # Panel
        pw, ph = 500, 420
        px = SCREEN_WIDTH // 2 - pw // 2
        py = SCREEN_HEIGHT // 2 - ph // 2
        pygame.draw.rect(surface, UI_PANEL, (px, py, pw, ph), border_radius=16)
        pygame.draw.rect(surface, UI_ACCENT, (px, py, pw, ph), 2, border_radius=16)

        title = self.assets.render_text("პაუზა", 72, UI_GOLD, bold=True)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, py + 30))

        for btn in self.buttons:
            btn.render(surface)
