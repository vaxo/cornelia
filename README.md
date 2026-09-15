# Cornelia

A 2D flappy-bird-style **car** game built with [pygame](https://www.pygame.org/).
You keep a car airborne through a scrolling night city, threading gaps between
obstacles. Georgian-language UI.

## Requirements

- Python 3.9+
- pygame 2.5+

## Running

```bash
pip install -r requirements.txt
python3 main.py
```

## Controls

| Key | Action |
| --- | --- |
| `Space` | Flap / lift the car |
| `1` | Use **shield** power-up |
| `2` | Use **slow-motion** power-up |
| `3` | Use **2× score** power-up |
| `Esc` | Pause |

## Game modes

- **Levels** — 10 hand-tuned levels with increasing speed, shrinking gaps and
  moving obstacles from level 4 onward. Progress unlocks as you clear them.
- **Endless** — run until you crash, chasing a high score.

Along the way there are power-ups (shield, slow-motion, score multiplier),
weather effects, day/night backgrounds, and selectable cars and colors.

## Project layout

```
main.py                 entry point
build_windows.py        PyInstaller build script (Windows / macOS)
config/                 constants, settings, asset paths
data/                   level and car definitions (JSON)
assets/                 images, fonts, audio
src/
  core/                 game loop, scene manager, display, event handling
  screens/              menu, level, endless, pause, game-over screens
  managers/             obstacles, collisions, score, audio, weather, saves, ...
  entities/             player car, obstacles, power-ups
  ui/                   buttons, labels, HUD, icons
  utils/                math, JSON and debug helpers
```

## Building a standalone executable

```bash
pip install pyinstaller
python3 build_windows.py
```

Produces a single bundled binary (`Cornelia.exe` on Windows, a unix binary /
`.app` on macOS) with `assets/` and `data/` embedded.

## Saves

Player progress lives in `data/save_data.json`. It is not tracked in git and is
recreated with defaults on first run.

## Audio credits

The tracks under `assets/audio/music/` are third-party music included for local
playback during development and are **not** covered by this repository's license.
