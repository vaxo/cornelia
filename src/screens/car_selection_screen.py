import pygame
from src.screens.base_screen import BaseScreen
from src.ui.button import Button
from src.ui.icons import draw_left_arrow, draw_right_arrow
from src.entities.player_car import PlayerCar, tempo_label
from config.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BTN_W, BTN_H,
    UI_TEXT, UI_GOLD, UI_ACCENT, UI_TEXT_DIM, UI_ACCENT2,
    CAR_PALETTE, CAR_MODEL_NAMES, CAR_MODEL_DISPLAY,
    SUBTITLE_FONT_SIZE, BTN_FONT_SIZE,
)


class CarSelectionScreen(BaseScreen):
    def __init__(self, game):
        super().__init__(game)
        self.models = CAR_MODEL_NAMES
        self.model_idx = 0
        self.color_idx = 0
        self._preview = None
        self._build_buttons()

    def _build_buttons(self):
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2 + 100
        self.btn_prev_car   = Button(cx - 220, cy - 80,  160, 54, "კარი",  self.assets)
        self.btn_next_car   = Button(cx + 220, cy - 80,  160, 54, "კარი",  self.assets)
        self.btn_prev_col   = Button(cx - 220, cy,       160, 54, "ფერი",  self.assets)
        self.btn_next_col   = Button(cx + 220, cy,       160, 54, "ფერი",  self.assets)
        self.btn_select     = Button(cx, cy + 80,         BTN_W, BTN_H, "არჩევა",   self.assets)
        self.btn_back       = Button(cx, cy + 80 + 70,    BTN_W, BTN_H, "უკან",     self.assets)

    def on_enter(self, **kwargs):
        # Match current save selection
        saved_model = self.save.selected_car
        saved_color = self.save.selected_color
        if saved_model in self.models:
            self.model_idx = self.models.index(saved_model)
        palette = list(CAR_PALETTE[self.current_model()].keys())
        if saved_color in palette:
            self.color_idx = palette.index(saved_color)
        self._rebuild_preview()

    def current_model(self):
        return self.models[self.model_idx]

    def current_color(self):
        palette = list(CAR_PALETTE[self.current_model()].keys())
        return palette[self.color_idx % len(palette)]

    def _rebuild_preview(self):
        self._preview = PlayerCar(self.current_model(), self.current_color())

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        all_btns = [self.btn_prev_car, self.btn_next_car, self.btn_prev_col,
                    self.btn_next_col, self.btn_select, self.btn_back]
        for btn in all_btns:
            btn.update(mouse_pos)
        for event in events:
            if self.btn_prev_car.handle_event(event):
                self.audio.play_sfx("click")
                self.model_idx = (self.model_idx - 1) % len(self.models)
                self.color_idx = 0
                self._rebuild_preview()
            if self.btn_next_car.handle_event(event):
                self.audio.play_sfx("click")
                self.model_idx = (self.model_idx + 1) % len(self.models)
                self.color_idx = 0
                self._rebuild_preview()
            if self.btn_prev_col.handle_event(event):
                self.audio.play_sfx("click")
                palette = CAR_PALETTE[self.current_model()]
                self.color_idx = (self.color_idx - 1) % len(palette)
                self._rebuild_preview()
            if self.btn_next_col.handle_event(event):
                self.audio.play_sfx("click")
                palette = CAR_PALETTE[self.current_model()]
                self.color_idx = (self.color_idx + 1) % len(palette)
                self._rebuild_preview()
            if self.btn_select.handle_event(event):
                self.audio.play_sfx("click")
                self.save.save_selected_car(self.current_model(), self.current_color())
                self.game.scene.change("main_menu")
            if self.btn_back.handle_event(event):
                self.audio.play_sfx("click")
                self.game.scene.change("main_menu")

    def update(self, dt):
        # Keep the preview flapping so wing/arm animation is visible before you pick
        if self._preview:
            self._preview._update_anim(dt)

    def render(self, surface):
        surface.fill((8, 12, 30))

        title = self.assets.render_text("პერსონაჟის არჩევა", 64, UI_GOLD, bold=True)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 60))

        # Preview panel
        px, py = SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT // 2 - 160

        # Pace / difficulty for this character, above the panel - big bodies get
        # a slower world, small ones a faster one, and the points follow.
        if self._preview:
            tempo = self._preview.tempo
            pace = self.assets.render_text(
                f"{tempo_label(tempo)}   ·   ქულა x{tempo:.2f}", 28, UI_ACCENT2)
            surface.blit(pace, (SCREEN_WIDTH // 2 - pace.get_width() // 2, py - 52))
        panel = pygame.Rect(px, py, 440, 200)
        pygame.draw.rect(surface, (20, 28, 60), panel, border_radius=14)
        pygame.draw.rect(surface, UI_ACCENT, panel, 2, border_radius=14)

        if self._preview:
            pw = self._preview.w * 2
            ph = self._preview.h * 2
            preview_surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
            scale = pygame.transform.scale(self._preview._current_frame(), (pw, ph))
            preview_surf.blit(scale, (0, 0))
            surface.blit(preview_surf, (SCREEN_WIDTH // 2 - pw // 2, py + (200 - ph) // 2))

        # Model name
        model_name = CAR_MODEL_DISPLAY.get(self.current_model(), self.current_model())
        mn = self.assets.render_text(model_name, 42, UI_TEXT, bold=True)
        surface.blit(mn, (SCREEN_WIDTH // 2 - mn.get_width() // 2, py + 210))

        # Color name
        cn = self.assets.render_text(self.current_color(), SUBTITLE_FONT_SIZE, UI_TEXT_DIM)
        surface.blit(cn, (SCREEN_WIDTH // 2 - cn.get_width() // 2, py + 260))



        for btn in [self.btn_prev_car, self.btn_next_car, self.btn_prev_col,
                    self.btn_next_col, self.btn_select, self.btn_back]:
            btn.render(surface)

        # Direction arrows (drawn, so they never depend on font glyph coverage)
        for btn in (self.btn_prev_car, self.btn_prev_col):
            draw_left_arrow(surface, btn.rect.left + 22, btn.rect.centery, 18, UI_TEXT)
        for btn in (self.btn_next_car, self.btn_next_col):
            draw_right_arrow(surface, btn.rect.right - 22, btn.rect.centery, 18, UI_TEXT)
