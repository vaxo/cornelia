import os
import glob
import pygame
from config.paths import FONTS

# Load the UI font by FILE PATH rather than by name. On macOS pygame's
# SysFont(name) resolution is unreliable — it silently returns broken/box fonts
# for many names (Tahoma, Segoe UI), and dedicated Georgian faces like SF
# Georgian lack Latin/digits. Loading a specific known-good file that covers
# BOTH Georgian AND Latin/digits avoids all of that.
#
# Priority: a font bundled in assets/fonts/ (fully portable — drop any .ttf
# there to override), then well-known per-OS system fonts.
FONT_CANDIDATES = [
    # macOS (both cover Georgian + Latin + digits)
    "/System/Library/Fonts/HelveticaNeue.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
    # Windows
    "C:/Windows/Fonts/sylfaen.ttf",
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/arialuni.ttf",
    "C:/Windows/Fonts/tahoma.ttf",
    # Linux
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansGeorgian-Regular.ttf",
    "/usr/share/fonts/noto/NotoSansGeorgian-Regular.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
]


def _bundled_fonts():
    files = []
    for ext in ("*.ttf", "*.otf", "*.ttc"):
        try:
            files += glob.glob(os.path.join(FONTS, ext))
        except Exception:
            pass
    return sorted(files)


_font_path = None
_font_resolved = False


def _resolve_font_path():
    """Absolute path of the first available UI font, or None for pygame default."""
    global _font_path, _font_resolved
    if not _font_resolved:
        for path in _bundled_fonts() + FONT_CANDIDATES:
            if path and os.path.exists(path):
                _font_path = path
                break
        _font_resolved = True
    return _font_path


class AssetManager:
    def __init__(self):
        self._font_cache = {}
        self._text_cache = {}

    def font(self, size, bold=False):
        key = (size, bold)
        if key not in self._font_cache:
            path = _resolve_font_path()
            if path:
                f = pygame.font.Font(path, size)
                f.set_bold(bold)
            else:
                # Last resort: pygame's built-in font (Latin only).
                f = pygame.font.SysFont(None, size, bold=bold)
            self._font_cache[key] = f
        return self._font_cache[key]

    def render_text(self, text, size, color, bold=False):
        key = (text, size, color, bold)
        if key not in self._text_cache:
            if len(self._text_cache) > 600:
                for k in list(self._text_cache)[:100]:
                    del self._text_cache[k]
            self._text_cache[key] = self.font(size, bold).render(text, True, color)
        return self._text_cache[key]
