import pygame
from src.screens.base_screen import BaseScreen
from src.ui.button import Button
from src.ui.icons import draw_star
from config.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BTN_W, BTN_H, BTN_SPACING,
    UI_TEXT, UI_GOLD, UI_ACCENT, UI_GREEN, UI_PANEL, UI_TEXT_DIM,
    NUM_LEVELS,
)


class LevelCompleteScreen(BaseScreen):
    def __init__(self, game):
        super().__init__(game)
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2 + 50
        self._score = 0
        self._best = 0
        self._level = 1
        self.btn_next    = Button(cx, cy,              BTN_W, BTN_H, "შემდეგი დონე", self.assets)
        self.btn_restart = Button(cx, cy + BTN_SPACING, BTN_W, BTN_H, "თავიდან",      self.assets)
        self.btn_menu    = Button(cx, cy + BTN_SPACING * 2, BTN_W, BTN_H, "მთავარი მენიუ", self.assets)

    def on_enter(self, score=0, best=0, level=1, **kwargs):
        self._score = score
        self._best = best
        self._level = level

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        btns = [self.btn_restart, self.btn_menu]
        is_last = self._level >= NUM_LEVELS
        if not is_last:
            btns = [self.btn_next] + btns
        for btn in btns:
            btn.update(mouse_pos)
        for event in events:
            if self.btn_next.handle_event(event) and not is_last:
                self.audio.play_sfx("click")
                self.game.scene.change("level_game", level=self._level + 1)
            if self.btn_restart.handle_event(event):
                self.audio.play_sfx("click")
                self.game.scene.change("level_game", level=self._level)
            if self.btn_menu.handle_event(event):
                self.audio.play_sfx("click")
                self.game.scene.change("main_menu")

    def render(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 15, 10, 200))
        surface.blit(overlay, (0, 0))

        pw, ph = 700, 540
        px = SCREEN_WIDTH // 2 - pw // 2
        py = SCREEN_HEIGHT // 2 - ph // 2 - 20
        pygame.draw.rect(surface, UI_PANEL, (px, py, pw, ph), border_radius=16)
        pygame.draw.rect(surface, UI_GREEN, (px, py, pw, ph), 2, border_radius=16)

        title = self.assets.render_text("დონე დასრულდა!", 58, UI_GREEN, bold=True)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, py + 28))

        lvl_txt = self.assets.render_text(f"დონე {self._level}", 46, UI_GOLD, bold=True)
        surface.blit(lvl_txt, (SCREEN_WIDTH // 2 - lvl_txt.get_width() // 2, py + 104))

        score_txt = self.assets.render_text(f"ქულა: {self._score}", 44, UI_TEXT, bold=True)
        surface.blit(score_txt, (SCREEN_WIDTH // 2 - score_txt.get_width() // 2, py + 160))

        new_best = self._score >= self._best and self._score > 0
        best_col = UI_GOLD if new_best else UI_TEXT_DIM
        best_label = "ახალი რეკორდი!" if new_best else f"საუკეთესო: {self._best}"
        best_txt = self.assets.render_text(best_label, 34, best_col)
        bx = SCREEN_WIDTH // 2 - best_txt.get_width() // 2
        surface.blit(best_txt, (bx, py + 214))
        if new_best:
            draw_star(surface, bx - 24, py + 231, 15, UI_GOLD)
            draw_star(surface, bx + best_txt.get_width() + 24, py + 231, 15, UI_GOLD)

        is_last = self._level >= NUM_LEVELS
        btns = [self.btn_restart, self.btn_menu]
        if not is_last:
            btns = [self.btn_next] + btns
        for btn in btns:
            btn.render(surface)
