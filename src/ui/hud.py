import pygame
from src.ui.icons import draw_finish_flag
from config.constants import (
    HUD_PAD, HUD_FONT_LG, HUD_FONT_MD, HUD_FONT_SM,
    UI_TEXT, UI_GOLD, UI_TEXT_DIM, UI_ACCENT2, UI_ACCENT,
    SCREEN_WIDTH,
)


class HUD:
    def __init__(self, asset_manager, mode="endless"):
        self.assets = asset_manager
        self.mode = mode

    def render(self, surface, score, best, combo, level=None, progress=None):
        pad = HUD_PAD

        # Score (top right)
        score_surf = self.assets.render_text(f"ქულა: {score}", HUD_FONT_LG, UI_TEXT, bold=True)
        surface.blit(score_surf, (SCREEN_WIDTH - score_surf.get_width() - pad, pad))

        # Best score (below score)
        best_surf = self.assets.render_text(f"საუკეთესო: {best}", HUD_FONT_SM, UI_TEXT_DIM)
        surface.blit(best_surf, (SCREEN_WIDTH - best_surf.get_width() - pad, pad + score_surf.get_height() + 4))

        # Combo (top left)
        if combo > 1:
            col = UI_GOLD
            combo_surf = self.assets.render_text(f"x{combo} კომბო!", HUD_FONT_MD, col, bold=True)
        else:
            combo_surf = self.assets.render_text("კომბო: 0", HUD_FONT_SM, UI_TEXT_DIM)
        surface.blit(combo_surf, (pad, pad))

        # Mode label
        mode_text = "უსასრულო" if self.mode == "endless" else f"დონე {level}"
        mode_surf = self.assets.render_text(mode_text, HUD_FONT_SM, UI_TEXT_DIM)
        surface.blit(mode_surf, (pad, pad + combo_surf.get_height() + 6))

        # Level progress bar (levels mode only)
        if self.mode == "level" and progress is not None:
            bar_w = 320
            bar_h = 14
            bar_x = (SCREEN_WIDTH - bar_w) // 2
            bar_y = pad
            pygame.draw.rect(surface, (30, 35, 65), (bar_x, bar_y, bar_w, bar_h), border_radius=7)
            fill = int(bar_w * progress)
            if fill > 0:
                pygame.draw.rect(surface, UI_ACCENT2, (bar_x, bar_y, fill, bar_h), border_radius=7)
            pygame.draw.rect(surface, UI_ACCENT, (bar_x, bar_y, bar_w, bar_h), 2, border_radius=7)
            # Finish flag icon (drawn)
            draw_finish_flag(surface, bar_x + bar_w + 8, bar_y - 4, 22)
