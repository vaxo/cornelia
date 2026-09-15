import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ASSETS = os.path.join(ROOT, "assets")
IMAGES = os.path.join(ASSETS, "images")
AUDIO = os.path.join(ASSETS, "audio")
FONTS = os.path.join(ASSETS, "fonts")
DATA = os.path.join(ROOT, "data")

SAVE_FILE = os.path.join(DATA, "save_data.json")
LEVELS_FILE = os.path.join(DATA, "levels.json")
CARS_FILE = os.path.join(DATA, "cars.json")

MUSIC_DIR = os.path.join(AUDIO, "music")
SFX_DIR = os.path.join(AUDIO, "sfx")

def sfx(name): return os.path.join(SFX_DIR, name)
def music(name): return os.path.join(MUSIC_DIR, name)
def image(subdir, name): return os.path.join(IMAGES, subdir, name)
def font(name): return os.path.join(FONTS, name)
