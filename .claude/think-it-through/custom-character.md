# Think-it-through — Custom character ("build your own")

**Status:** design agreed · not yet built · 2026-07-21
**Scope:** In: let a player create/save ONE custom playable character via a parametric builder that reuses the procedural drawing system. Out: a freehand pixel/sprite editor, importing image files, multiple custom slots (all considered and rejected for v1).

## Intention
Today a player can only *pick* from built-in characters (cars, hero, rocket, plane, bibble). We want them to **make their own** — pick a body, colors, and features — and play as it. It must stay true to the game's ethos: everything drawn in code, **no external art assets**, data lives in constants/JSON.

## How it is now (verified in code)
- A character = **code**, not data. `PlayerCar.__init__(model, color)` looks up a fixed size from `CAR_SIZES` (`src/entities/player_car.py:13`), a trail color from a dict (`player_car.py:34`), then `_build_surface()`.
- `_build_surface` picks `CAR_PALETTE[model]`, reads a `[body, accent, detail]` colour triple by colour-name, and dispatches to a bespoke `_draw_<model>()` via a hardcoded `drawers` map (`player_car.py:43`+). Each character is its own hand-written pygame draw method.
- The set of characters is three parallel hardcoded structures: `CAR_MODEL_NAMES` (`config/constants.py:120`), `CAR_MODEL_DISPLAY` names (`constants.py:121`), `CAR_PALETTE` colour triples (`constants.py`), plus `CAR_SIZES` + a `_draw_*` method.
- Selection UI cycles `self.models = CAR_MODEL_NAMES` and colours from `CAR_PALETTE[model].keys()` with prev/next buttons (`src/screens/car_selection_screen.py:17,44-49,61-80`); "select" calls `save.save_selected_car(model, color)` (`car_selection_screen.py:83`).
- Persistence stores **only two string keys**: `selected_car` (a model key) and `selected_color` (a colour-name key) (`src/managers/save_manager.py:19,45`). The save is a plain JSON dict via `save_json` — trivially extendable.
- Gameplay rebuilds the player from those two strings: `PlayerCar(model, color)` at `endless_screen.py:30` and `level_game_screen.py:54`; preview at `car_selection_screen.py:52`.

## The real problem (one sentence)
Every character is bespoke draw-code and the save only holds a colour *key*, so "custom character" can't mean "author new art at runtime" without either a whole sprite-editor or a **data-driven character** the existing draw system can render — and the save must hold real parameters, not a key.

## Alternatives considered
- **A. Parametric "Character Builder" (reuse the procedural system).** Add ONE `"custom"` model whose `_draw_custom(params)` **composes small part-drawers** (body shape + colours + feature toggles) read from a saved `custom` params dict. New "Customize" screen for the sliders/pickers. Reuses: PlayerCar dispatch, the colour-triple idea, Button/selection UI patterns, and the JSON save (just add a `custom` object). Asset-free, on-ethos, cheap, and genuinely "make your own." Bounded to the parameters we expose — not arbitrary art. **← chosen.**
- **B. Free-colour recolour only.** RGB sliders on an existing base; no new features. Even cheaper, but it's "custom colours," not a "custom character" — under-delivers given the user keeps adding whole new characters.
- **C. Freehand pixel/sprite editor.** A paint grid saved as pixel data. Maximum freedom, reuses ~nothing, large new UI, clashes with the polished procedural look, and hitbox-from-arbitrary-pixels is fiddly. Overkill for v1.
- **D. Import a PNG.** Reuses the sprite surface but: pygame has no native file dialog, scaling/hitbox from arbitrary images, art-style mismatch, and we just fought Downloads/TCC file-access issues. Poor fit.

## Decisions
1. **Build Option A — a parametric Character Builder.** One extra `"custom"` character + a dedicated Customize screen + a `custom` params dict in the save. It's the only option that delivers "make your own" while reusing all existing plumbing and staying asset-free.
2. **Compose from part-drawers.** `_draw_custom(params)` calls small helpers: `body shape` (e.g. puff / car / capsule / rocket), then `pattern` (none/stripe/spots), `eyes` (on/off), `wings` (none/small/big), `topper` (none/antenna/hat/hair-curl). Each part is a tiny function → testable, and future parts drop in without touching callers.
3. **Curated colour grid, not raw RGB (v1).** Body + accent chosen from a swatch grid (~12 hues). Simpler UI than sliders, still thousands of combos, and avoids ugly/invisible colour picks. RGB sliders can come later.
4. **Fixed canvas size (e.g. 112×92) for the custom model** regardless of params → predictable, fair hitbox (same `pad=6` inset path). Parts are drawn within that box.
5. **Save schema is additive + backward-compatible.** Add `"custom": { shape, body, accent, eyes, wings, topper, pattern }` to the save dict; default it in `SaveManager.load` when absent so old saves and `save_data.json` keep working. `selected_car == "custom"` selects it.
6. **`PlayerCar` gains an optional `custom=None` kwarg.** When `model == "custom"`, `_build_surface` uses the passed params (screens pass `self.save.custom`); everything else unchanged. Small, localized ripple at the 3 construction sites (`endless_screen.py:30`, `level_game_screen.py:54`, `car_selection_screen.py:52`).
7. **Entry point:** `"custom"` appears as the last entry in the character carousel; when it's the current pick, the two colour buttons are replaced by a **"რედაქტირება" (Edit)** button that opens the Customize screen. Keeps one obvious path in, no new top-level menu item.

## Risks / new problems
- **Save migration:** must default `custom` when missing (additive) — else old `save_data.json` breaks. Low risk if handled in `load`.
- **Selection-screen assumptions:** the prev/next **colour** cycle assumes every model has a `CAR_PALETTE` entry; `"custom"` has none. Must special-case: when model is custom, hide colour cycling and show Edit. Guard `on_enter` (`car_selection_screen.py:39`) which does `CAR_PALETTE[current_model()]`.
- **Hitbox fairness:** big wings/toppers can extend past the body inside the hitbox (already true for bibble). Fixed canvas + conservative part sizes keeps it fair.
- **Trail colour:** derive from the custom accent/body instead of the model→colour dict (`player_car.py:34`).
- **UI scope creep:** the Customize screen is the real cost. Keep v1 to swatch grid + a few toggle buttons with a live preview; resist sliders/animation until it's proven.

## Decision and next step
**Agreed:** ship a parametric Character Builder (Option A) — one `"custom"` model composed from part-drawers, edited in a new Customize screen, persisted as a `custom` params dict (additive save change), entered via an Edit button on the character carousel.

**Smallest safe first move:** implement the `custom` params **schema + sensible default** and `_draw_custom(params)` with its part-drawers, and render it standalone (offscreen PNG / pixel-check) across a few param combos to validate composition and the fixed-canvas hitbox — *before* building any UI or touching the save. Then wire the save default, then the Customize screen last.
