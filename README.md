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
weather, and selectable characters and colors.

## Weather

Rain, fog, storm and **snow**. A kind of weather holds for roughly a minute and
then *crossfades* into the next one over about four seconds — the rain thins out
as the snow starts drifting in, nothing ever pops. While it snows, the rooftops
gather snow and little christmas trees light up on them with a glowing border.
Soft cumulus drift across the night sky and thicken as the weather closes in.

## Difficulty follows the character

Characters are not resized to balance them — a big character stays big. What
changes is the pace of the world around it. Bulky characters (Bibble, the hen)
fill more of the gap, so the world runs slower for them and gates arrive further
apart in time; small quick ones (the chick) get a faster, twitchier world. The
layout is identical either way — only the time you get to read it changes — and
the points a gate is worth follow the same number, so the quick characters pay
out more. The character-select screen shows each one's pace and multiplier.

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

`assets/audio/sfx/dog_bark.wav` (the Dalmatian's voice) is the first 3 seconds
of a "Small Dog Barking" sound effect supplied by the project owner; check its
license before distributing a build.

`assets/audio/sfx/sun_yawn.wav` (the Sun's voice) is 0:06–0:07 of a meme
sound compilation supplied by the project owner; check its license before
distributing a build.
