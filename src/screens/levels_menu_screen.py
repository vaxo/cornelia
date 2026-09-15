import pygame
from src.screens.base_screen import BaseScreen
from src.ui.button import Button
from src.ui.icons import draw_lock, draw_check
from config.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    UI_TEXT, UI_GOLD, UI_ACCENT, UI_TEXT_DIM, UI_LOCKED,
    UI_BUTTON, UI_BUTTON_HOVER, UI_BUTTON_BORDER,
    NUM_LEVELS, BTN_H, BTN_W,
)


class LevelsMenuScreen(BaseScreen):
    def __init__(self, game):
        super().__init__(game)
        self.btn_back = Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80, BTN_W, BTN_H, "უკან", self.assets)
        self._level_btns = []
        self._build_level_buttons()

    def _build_level_buttons(self):
        self._level_btns.clear()
        cols = 5
        rows = 2
        btn_w = 130
        btn_h = 70
        gap_x = 46
        gap_y = 52
        total_w = cols * btn_w + (cols - 1) * gap_x
        start_x = (SCREEN_WIDTH - total_w) // 2
        start_y = SCREEN_HEIGHT // 2 - 60
        for i in range(NUM_LEVELS):
            col = i % cols
            row = i // cols
            x = start_x + col * (btn_w + gap_x) + btn_w // 2
            y = start_y + row * (btn_h + gap_y) + btn_h // 2
            label = f"დონე {i + 1}"
            btn = Button(x, y, btn_w, btn_h, label, self.assets, font_size=28)
            self._level_btns.append((i + 1, btn))

    def on_enter(self, **kwargs):
        self._build_level_buttons()

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        self.btn_back.update(mouse_pos)
        for event in events:
            if self.btn_back.handle_event(event):
                self.audio.play_sfx("click")
                self.game.scene.change("main_menu")
        for lvl_num, btn in self._level_btns:
            btn.update(mouse_pos)
            if self.save.is_level_unlocked(lvl_num):
                for event in events:
                    if btn.handle_event(event):
                        self.audio.play_sfx("click")
                        self.game.scene.change("level_game", level=lvl_num)

    def update(self, dt):
        pass

    def render(self, surface):
        surface.fill((8, 12, 30))

        title = self.assets.render_text("დონეები", 72, UI_GOLD, bold=True)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 60))

        for lvl_num, btn in self._level_btns:
            unlocked = self.save.is_level_unlocked(lvl_num)
            completed = lvl_num in self.save.completed_levels

            # Draw custom background for locked
            rect = btn.rect
            if not unlocked:
                pygame.draw.rect(surface, UI_LOCKED, rect, border_radius=10)
                pygame.draw.rect(surface, (80, 80, 100), rect, 2, border_radius=10)
                # Level number (dim) above a drawn padlock
                num = self.assets.render_text(str(lvl_num), 24, (110, 110, 135), bold=True)
                surface.blit(num, (rect.centerx - num.get_width() // 2, rect.top + 10))
                draw_lock(surface, rect.centerx, rect.centery + 12, 24, (120, 120, 145))
            else:
                btn.render(surface)
                if completed:
                    draw_check(surface, rect.right - 18, rect.top + 14, 16, (80, 220, 120), 3)

        self.btn_back.render(surface)
