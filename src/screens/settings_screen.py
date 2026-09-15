import pygame
from src.screens.base_screen import BaseScreen
from src.ui.button import Button
from config.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BTN_W, BTN_H,
    UI_TEXT, UI_ACCENT, UI_GOLD, UI_GREEN, UI_RED,
    TITLE_FONT_SIZE, BTN_FONT_SIZE, SUBTITLE_FONT_SIZE,
)


class SettingsScreen(BaseScreen):
    def __init__(self, game):
        super().__init__(game)
        cx = SCREEN_WIDTH // 2

        self._y_sound = 205
        self._y_music = 310      # music volume row center
        y_nextsong = 400
        self._y_sfx = 500        # sfx volume row center
        y_full = 600
        y_day = 675
        y_back = 775

        self.btn_sound      = Button(cx, self._y_sound, BTN_W, BTN_H, "", self.assets)
        self.btn_music_down = Button(cx - 170, self._y_music, 72, BTN_H, "−", self.assets, font_size=48)
        self.btn_music_up   = Button(cx + 170, self._y_music, 72, BTN_H, "+", self.assets, font_size=48)
        self.btn_nextsong   = Button(cx, y_nextsong, BTN_W, BTN_H, "შემდეგი სიმღერა", self.assets, font_size=34)
        self.btn_sfx_down   = Button(cx - 170, self._y_sfx, 72, BTN_H, "−", self.assets, font_size=48)
        self.btn_sfx_up     = Button(cx + 170, self._y_sfx, 72, BTN_H, "+", self.assets, font_size=48)
        self.btn_fullscreen = Button(cx, y_full, BTN_W, BTN_H, "", self.assets)
        self.btn_daymode    = Button(cx, y_day, BTN_W, BTN_H, "", self.assets)
        self.btn_back       = Button(cx, y_back, BTN_W, BTN_H, "უკან", self.assets)

        self._all = [
            self.btn_sound, self.btn_music_down, self.btn_music_up, self.btn_nextsong,
            self.btn_sfx_down, self.btn_sfx_up,
            self.btn_fullscreen, self.btn_daymode, self.btn_back,
        ]

    def _sound_text(self):
        return "ხმა: ჩართული" if self.save.settings.sound_enabled else "ხმა: გამორთული"

    def _fullscreen_text(self):
        return "ეკრანი: სრული" if self.save.settings.fullscreen else "ეკრანი: ფანჯარა"

    def _daymode_text(self):
        return "რეჟიმი: დღე" if self.save.settings.day_mode else "რეჟიმი: ღამე"

    def _pct(self, v):
        return int(round(v * 100))

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        for btn in self._all:
            btn.update(mouse_pos)
        for event in events:
            if self.btn_sound.handle_event(event):
                self.audio.play_sfx("click")
                self.audio.set_sound_enabled(not self.save.settings.sound_enabled)
                self.save.save_settings()
            if self.btn_music_down.handle_event(event):
                self.audio.play_sfx("click")
                self.audio.set_music_volume(self.save.settings.music_volume - 0.1)
                self.save.save_settings()
            if self.btn_music_up.handle_event(event):
                self.audio.play_sfx("click")
                self.audio.set_music_volume(self.save.settings.music_volume + 0.1)
                self.save.save_settings()
            if self.btn_nextsong.handle_event(event):
                self.audio.play_sfx("click")
                self.audio.next_track()
            if self.btn_sfx_down.handle_event(event):
                self.audio.set_sfx_volume(self.save.settings.sfx_volume - 0.1)
                self.audio.play_sfx("click")   # play AFTER change so you hear the new level
                self.save.save_settings()
            if self.btn_sfx_up.handle_event(event):
                self.audio.set_sfx_volume(self.save.settings.sfx_volume + 0.1)
                self.audio.play_sfx("click")
                self.save.save_settings()
            if self.btn_fullscreen.handle_event(event):
                self.audio.play_sfx("click")
                self.game.toggle_fullscreen()
            if self.btn_daymode.handle_event(event):
                self.audio.play_sfx("click")
                self.save.settings.day_mode = not self.save.settings.day_mode
                self.save.save_settings()
            if self.btn_back.handle_event(event):
                self.audio.play_sfx("click")
                self.game.scene.change("main_menu")

    def update(self, dt):
        self.btn_sound.text = self._sound_text()
        self.btn_fullscreen.text = self._fullscreen_text()
        self.btn_daymode.text = self._daymode_text()

    def _render_vol_row(self, surface, cx, label, cy, value, down_btn, up_btn):
        lbl = self.assets.render_text(label, SUBTITLE_FONT_SIZE, UI_TEXT)
        surface.blit(lbl, (cx - lbl.get_width() // 2, cy - 60))
        down_btn.render(surface)
        up_btn.render(surface)
        pct = self.assets.render_text(f"{self._pct(value)}%", BTN_FONT_SIZE, UI_GOLD, bold=True)
        surface.blit(pct, (cx - pct.get_width() // 2, cy - pct.get_height() // 2))

    def render(self, surface):
        surface.fill((8, 12, 30))
        cx = SCREEN_WIDTH // 2

        title_surf = self.assets.render_text("პარამეტრები", 60, UI_GOLD, bold=True)
        surface.blit(title_surf, (cx - title_surf.get_width() // 2, 95))

        self.btn_sound.render(surface)
        self._render_vol_row(surface, cx, "მუსიკის ხმა", self._y_music,
                             self.save.settings.music_volume, self.btn_music_down, self.btn_music_up)
        self.btn_nextsong.render(surface)
        self._render_vol_row(surface, cx, "ეფექტების ხმა", self._y_sfx,
                             self.save.settings.sfx_volume, self.btn_sfx_down, self.btn_sfx_up)
        self.btn_fullscreen.render(surface)
        self.btn_daymode.render(surface)
        self.btn_back.render(surface)
