# Think-it-through — Redraw Bibble to match the reference + flap its arms while flying

**Status:** design agreed · not yet built · 2026-08-20
**Scope:** In: (1) rewrite the `bibble` character's art so it reads like the reference image — teal/cyan fur, magenta spiky mohawk, purple chest/limb accent, big lashed blue eyes, out-stretched arms; (2) animate its arms flapping up/down every frame during flight. Out: photoreal fidelity, external PNG assets, changing any other character. Related: [[custom-character]].

## Intention
The `bibble` character today is a fluffy *fairy-winged pixie*, not the creature in the reference (a teal furry monster with a magenta mohawk and arms). We want the sprite to look like the reference, and — because it's a flappy-flyer — we want its arms/wings to visibly beat up and down while airborne so it reads as *actively flying* rather than a static picture sliding through the air.

## How it is now (verified in code)
- Bibble is **procedural draw-code**, not an asset. `_draw_bibble(surf, w, h, fur, accent, detail)` at `src/entities/player_car.py:250-304` draws: big **fairy wings** behind the body (`:257-273`), feet (`:274-276`), a fluffy fur puff (`:277-287`), blush cheeks (`:288-291`), big eyes (`:292-300`), a smile (`:301-304`). There is **no mohawk** and **no arms** — the current silhouette is wings + puff.
- Colours come from `CAR_PALETTE["bibble"]` at `config/constants.py:112-118`, a `[fur, accent, detail]` triple. Default colour `"ცისფერი"` = `(150,215,240)` light-blue — paler/bluer than the reference teal, and there is **no separate colour slot for a mohawk**.
- Canvas size is fixed: `CAR_SIZES["bibble"] = (120, 100)` (`player_car.py:20`).
- **The sprite is built ONCE and cached.** `_build_surface()` (`player_car.py:43`) renders into `self._surf`, called only from `__init__` (`:40`) and `change_appearance` (`:378`). It then runs a top-light/bottom-shadow shading pass (`_apply_shading`, `:64`).
- **`render()` never rebuilds** — it blits the one cached `self._surf`, applying only `tilt` rotation (`player_car.py:359-363`) and trail puffs (`_render_trail`, `:346`). So today nothing on the character *moves* frame-to-frame except whole-body tilt.
- `update(dt)` (`player_car.py:330`) does gravity + tilt + trail only — there is **no animation phase/clock**.
- The character-select **preview blits `self._preview._surf` directly** (`src/screens/car_selection_screen.py:108`) — so whatever single surface lives in `_surf` is what the menu shows.
- Gameplay calls `self.car.update(dt)` then `self.car.render(...)` each frame in both screens (`endless_screen.py:109,146`; `level_game_screen.py:143,210`).

## The real problem (one sentence)
Bibble is a single pre-rendered, cached surface, so matching the reference means rewriting `_draw_bibble`, and making the arms flap means the sprite must *change every frame* — which the build-once/blit-and-rotate architecture doesn't currently support.

## Alternatives considered

### For the ART
- **A. Rewrite `_draw_bibble` procedurally to match the reference.** Teal fur puff, a magenta spiky **mohawk** (triangle tufts up top), purple **chest/limb accent** stripe, big lashed blue eyes, two **arms** replacing the fairy wings. Reuses the existing pygame-shape approach, the shading pass, and the palette triple (add the mohawk as its own colour). Asset-free, cross-platform, tiny. Con: it's a *stylized approximation*, never a pixel-match to the AI render. **← chosen for art.**
- **B. Blit a PNG of the reference.** Most faithful, but there is **no image pipeline** — `assets/` holds only audio + fonts, `AssetManager` only does fonts/text (`asset_manager.py`), and animating arms would still need them as separate layers/sprite-sheet. Adds infra, clashes with the codebase's "everything drawn in code, no external art" ethos (see [[custom-character]]), and raises a fan-art/copyright wrinkle for a bundled asset. Rejected.
- **C. Procedural body + still-image face.** Hybrid; worst of both, no real gain. Rejected.

### For the ANIMATION (flapping arms)
- **1. Split body + per-frame arm draw.** Cache the body once, draw arms on top each frame at a phase offset. Cleanest in spirit, but arms-drawn-after must *also* rotate with `tilt` — the current single-surface rotation path (`:360`) would have to be reworked or arms rotated separately. Fiddly.
- **2. Pre-render a few whole-sprite frames (arm sprite-sheet in memory), cycle by phase.** `_build_surface` for bibble builds a **list** of ~6-8 surfaces, identical except arm height; `render()` picks `frames[idx]` by an animation phase. The classic flappy-wing approach. Keeps `render()`'s tilt-rotation path **unchanged** (still one full surface per frame → rotate as-is), runtime cost ≈ zero (just an index), memory trivial (8 small SRCALPHA surfaces). Generalizes to other flyers later. **← chosen for animation.**
- **3. Recompute the full surface every frame from a phase param.** Simplest code, but re-runs all the fur-circle drawing + shading pass 60×/sec for no visual gain over #2. Wasteful. Rejected.

## Decisions
1. **Art via Option A** — rewrite `_draw_bibble` to the reference silhouette (teal fur, magenta mohawk, purple accent, lashed eyes, two arms instead of fairy wings). Stays procedural and asset-free, consistent with the whole character system and [[custom-character]].
2. **Add a mohawk colour** to the bibble palette. Extend the triple to carry a 4th colour, or (lower blast radius) derive the magenta from `accent` so `CAR_PALETTE` structure and all its `[fur,accent,detail]` readers stay untouched. Prefer **derive-from-accent** for v1; make accent the purple/magenta so mohawk + chest-stripe + arms share it and read as one creature.
3. **Animation via Option A/#2** — bibble's `_build_surface` produces `self._frames` (a list) instead of a lone `self._surf`; non-bibble models keep the single surface. Add `self._anim_phase` advanced in `update(dt)`; `render()` selects the frame. Keep `self._surf` pointing at a neutral mid-flap frame so the **select-screen preview** (`car_selection_screen.py:108`) still works with no change there.
4. **Flap couples to motion.** Advance the flap phase faster while `vel_y < 0` (rising) so it beats harder when climbing — sells "effort → lift." Idle/falling = a slow gentle beat.
5. **Hitbox unchanged.** Keep `CAR_SIZES["bibble"]`, `self.w/h`, and the `pad=6` rect (`player_car.py:306-314`). Draw raised arms *within* the existing 120×100 canvas (nudge the body down a few px if the top-most arm frame clips); collision must not change with flap.

## Risks / new problems
- **Clipping at extremes** — a fully-raised arm frame may exceed the 120×100 canvas top. Mitigate by giving arms headroom in the layout (or a modest canvas bump); verify the top frame isn't cut.
- **Tilt + frames interaction** — each frame is a full surface so `pygame.transform.rotate` still applies uniformly; confirm rotation of the raised-arm frame still centers correctly via the existing `(w-rotated_w)//2` recenter (`:361-362`).
- **`change_appearance` / `reset`** must rebuild frames and reset `_anim_phase` (currently `reset` at `:367` doesn't touch the surface — fine, but phase should zero).
- **Preview staleness** — menu shows `_surf`; ensure it's set to a representative frame, not left empty/None, or the preview breaks.
- **Only bibble animates** — guard the frames path so the other six models keep the single-surface fast path untouched (zero blast radius on them).
- **Perf** — one extra dict/index per frame; negligible. No per-frame reshading.

## Decision and next step
Agreed: keep it **procedural and asset-free** — redraw `_draw_bibble` to the reference look, and animate by pre-rendering a small in-memory arm-flap frame list cycled by an `update(dt)`-driven phase, leaving every other character and the tilt/preview/hitbox paths untouched.

**Smallest safe first move:** in a scratch copy of `_draw_bibble`, get the *static* new look right first (teal fur + magenta mohawk + purple accent + arms), rendered as today's single surface, and eyeball it against the reference. Only once the still frame reads as "Bibble" do we split it into the flap-frame list and wire the phase. (Art first, motion second — motion on wrong art wastes both.)
