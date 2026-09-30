# Think-it-through — Difficulty that scales with the character's size

**Status:** built · 2026-09-18
**Scope:** In: making the *played character's size* a deliberate difficulty dial (big = slower world, small = faster world), how it's applied, and how scoring stays honest. Out: per-character physics rewrites (gravity/lift), new levels, a difficulty menu setting. Related: [[custom-character]], [[bibble-redraw-and-flap]].

## Intention
Right now every character flies through an identical world — the only thing size changes is how much of the gap you fill. The idea is to turn size into an intentional, readable part of the game: the big heavy **Bibble** should play at a slower, heavier pace; the tiny **chick** should feel quick and twitchy. Size stops being a hidden handicap and becomes a *choice of difficulty and feel*.

> Naming note: in the code the big fluffy pixie is `bibble` / "ბიბლი" (`config/constants.py:118,150`) — the biggest character at 120×100. There's also a separate `hero` / "სუპერგმირი" (92×76, `constants.py:96,146`), which is mid-sized. The design below is driven by size, so it works either way, but "the big one" = **bibble**.

## How it is now (verified in code)
- **Size is per character, difficulty is not.** `CAR_SIZES` (`src/entities/player_car.py:14-24`) gives each model a sprite box: `bibble (120,100)`, `chicken (112,90)`, `hero (92,76)`, `chick (82,72)`, `camry (110,50)`, `sport (115,44)`. The hitbox is that box inset by `pad = 6` on every side (`player_car.py:600-607`) — so the *effective* heights are bibble 88, chicken 78, hero 64, chick 60, camry 38, sport 32.
- **Physics are global constants, identical for all models.** `GRAVITY = 0.42`, `LIFT_FORCE = -9.2`, `MAX_FALL_SPEED`, `MAX_RISE_SPEED` (`config/constants.py:156-159`) are applied in `PlayerCar.apply_gravity` with no model term (`player_car.py:614-618`). The only per-character tuning that exists today is cosmetic: `FLAP_RATE` (`player_car.py:34-38`) and trail colour (`player_car.py:52-59`).
- **So size already changes difficulty — silently, and only in one direction.** At the endless floor gap of 255 (`constants.py:170`) the clearance left over is `255 - hitbox_h`: camry **217px**, chick **195px**, hero **191px**, bibble **167px**. Bibble also spends longer inside a gate: crossing distance is `OBSTACLE_WIDTH + hitbox_w` = 82+108 for bibble vs 82+70 for the chick — ~25% more exposure at the same speed. Nothing anywhere compensates.
- **Difficulty is authored globally, per mode.** Endless ramps speed/gap/interval off *score* in `DifficultyManager.update_endless` (`src/managers/difficulty_manager.py:35-49`); levels read fixed `speed`/`gap`/`spawn_interval` rows from `data/levels.json` via `diff_mgr.reset(...)` (`src/screens/level_game_screen.py:80-89`). Neither knows which character you picked.
- **A "slow the whole world down" seam already exists.** The slow-mo helper multiplies world speed and passes the same factor as `time_scale` into the obstacle manager, which scales the *spawn timer* and the moving-obstacle bob with it (`src/screens/powerup_effects.py:42,95-96`; `src/managers/obstacle_manager.py:36-45`; `endless_screen.py:112,117`; `level_game_screen.py:147,152`). Because it scales speed **and** cadence together, the world geometry is untouched — it's a true tempo change, not a difficulty change. Crucially, `apply_gravity` ignores `time_scale`, so during slow-mo the car is *relatively* more agile — which is exactly why it feels like help.
- **Horizontal spacing is already speed-derived.** `spacing_interval(speed)` keeps consecutive gates `OBSTACLE_MIN_SPACING = 620px` apart whatever the speed (`difficulty_manager.py:11-20,33,49`), and vertical gap-to-gap jumps are capped to what's reachable in the frames available (`obstacle_manager.py:60-88`, `constants.py:193-195`).
- **Scoring and records are character-blind.** `on_pass` grants a flat `SCORE_PER_PASS` + combo bonus times a multiplier that today only reflects the 2× helper (`src/managers/score_manager.py:16-23`). There is exactly **one** global `high_score` in the save (`src/managers/save_manager.py:8,40-43`; current file holds `2970` with `selected_car: "bibble"`).
- **Levels finish by distance, not by gate count:** `level_mgr.advance_distance(speed)` per frame (`level_game_screen.py:159`), against `distance` from `data/levels.json`.

## The real problem (one sentence)
Size already makes big characters measurably harder (up to 50px less clearance and ~25% more time inside each gate) while the world treats every character identically — so the choice of character is a silent, uncompensated difficulty change instead of the deliberate, readable one we want.

## Alternatives considered
- **A. Per-character world tempo — reuse the slow-mo seam. ← chosen.** One scalar per model; multiply it into the same place `effect_speed_mult()` already feeds (world speed *and* the obstacle manager's `time_scale`). Big = tempo < 1 (slower, more reaction time), small = tempo > 1. Costs ~4 wiring lines plus a constants dict, changes zero geometry, reuses `spacing_interval`, the reachability cap, parallax, weather and the moving-obstacle bob for free, and is reversible by setting every tempo to 1.0.
- **B. Per-character physics ("weight"):** heavier gravity and a stronger-but-slower flap for big characters. Thematically lovely and the most "physical" answer, but it makes big characters **harder**, not slower-paced — the opposite of the ask — and it invalidates `REACHABLE_VSPEED = 4.2` (`constants.py:193`), which assumes one sustained climb rate for everyone. Gap placement would have to become per-character or big characters get genuinely impossible jumps. Big rewrite, big risk. Rejected for now; a mild version could layer on later.
- **C. Per-character gap scaling:** grow the obstacle gap by the character's height so clearance is constant. Simplest *fairness* fix, but it rewrites the authored geometry of all 10 levels per character, makes level screenshots/records incomparable, and still doesn't deliver a different *pace*. Rejected — though a size-aware **floor** on the gap is worth keeping as a safety net (see risks).
- **D. Derive the tempo automatically from `CAR_SIZES` instead of hand-authoring it.** Tempting (new characters self-tune, including the planned `custom` one from [[custom-character]]) — but sprite area doesn't match perceived bulk: `camry` is 5500px² and `chick` is 5904px², so an area formula would make the chick *slower than a car*. Derive-from-height is no better (it just cancels out the clearance difference and normalises everything back to equal). Rejected in favour of a hand-authored table, which is exactly the precedent `FLAP_RATE` already sets (`player_car.py:33-38`).
- **E. Do nothing / leave it implicit.** Defensible — the game is playable — but the current state is the worst of both: big characters are harder and nothing says so.

## Decisions
1. **Size becomes an explicit difficulty dial, not a balancing pass.** We deliberately *don't* normalise every character to equal difficulty. Big = slower world + bulkier hitbox = the forgiving choice; small = faster world + roomier gaps = the sharp choice. That's the user's intent and it gives each character a reason to exist.
2. **Implement it as a per-character world-tempo scalar** in `config/constants.py` next to `CAR_SIZES`/`FLAP_RATE`, hand-authored, seeded by size:
   `bibble 0.85 · chicken 0.90 · hero 0.93 · camry 1.00 (baseline) · retro 1.00 · plane 1.05 · rocket 1.08 · sport 1.08 · chick 1.15`
   ±15% is enough to feel and small enough not to break the authored levels. Default `1.0` for any unknown model, so the `custom` character of [[custom-character]] works without a change.
3. **Apply it at the existing slow-mo seam, to speed AND cadence.** Fold it into one `world_tempo()` helper = `CHARACTER_TEMPO[model] * effect_speed_mult()`, used where `effect_speed_mult()` is used today (`endless_screen.py:112,117`, `level_game_screen.py:147,152`). **Scaling speed alone is the trap:** speed without cadence keeps gate arrivals at the same ms interval while shrinking the pixel spacing, so a slow character would face *more, tighter* gates per level. Scaling both is a true tempo change — same geometry, same gate count, more thinking time.
4. **Leave `PlayerCar` physics, `FLAP_RATE` and the reachability constants alone.** Because gravity/lift are per-frame and unscaled, a slower world automatically makes a big character *relatively* more agile — the compensation we want falls out for free, with no retuning of `REACHABLE_VSPEED`.
5. **Points follow the tempo: score multiplier = the character's tempo.** `on_pass` already takes a multiplier (`score_manager.py:16-23`), so this is one argument: bibble earns 0.85× per gate, chick 1.15×, and it composes with the 2× helper. Playing the harder character is worth more — which is what keeps the single global high score honest.
6. **Surface it in the character selection screen** as a small "tempo / difficulty" badge under the name (`src/screens/car_selection_screen.py`), so the choice is visible before the run, not discovered after it.

## Risks / new problems
- **Compounding with slow-mo:** bibble + slow-mo = 0.85 × 0.55 ≈ 0.47 world speed, near-crawl. Probably fine (it's a consumable), but clamp the combined multiplier at a floor (~0.45) rather than letting future tunings stack unboundedly.
- **Levels get longer in wall-clock for slow characters** — completion is distance-based (`level_game_screen.py:159`), so at 0.85 tempo a level takes ~18% longer while presenting the same number of gates. That's the intended trade (more time per gate, longer exposure overall), but it's worth a playtest on level 10 before committing the table.
- **Reachability goes slightly conservative:** `_reachable_delta` computes frames from the *unscaled* `_spawn_interval` (`obstacle_manager.py:60-64`), so under tempo < 1 it under-counts the frames actually available and picks tamer vertical jumps. Safe direction, but it means big characters also get slightly less vertical variety. Pass the tempo in later if that reads as dull.
- **The single global `high_score` becomes mixed-provenance.** The existing 2970 was set under the old rules. The tempo-based score multiplier mostly fixes comparability, but the honest fix is an additive `high_scores: {model: n}` map in the save (`save_manager.py:27-38`), keeping `high_score` as the max for backward compatibility. Follow-up, not a blocker.
- **Safety net worth adding while we're here:** nothing currently guarantees the gap exceeds the character's hitbox — at `OBSTACLE_MIN_GAP = 255` bibble has 167px of clearance, which is fine, but a future bigger character (or a `custom` one) could get squeezed. A `max(gap, hitbox_h + MIN_CLEARANCE)` floor in `DifficultyManager` makes that impossible by construction.
- **Rollout:** entirely additive and flag-like — set every tempo to `1.0` and the game is byte-for-byte today's behaviour. `tests/` is empty, so verification is playtest-based; measure "gates survived" per character before and after.

## Decision and next step
**Agreed:** make the played character's size an explicit difficulty dial via a hand-authored per-character **world tempo** (bibble 0.85 → chick 1.15), applied through the *existing* slow-mo seam to both world speed and spawn cadence, with the character's physics untouched and the per-gate score multiplied by the same tempo so the harder characters pay out more.

**Built, 2026-09-18** — as designed, with the table living next to `CAR_SIZES` rather than in `config/constants.py` (it belongs with the other per-character feel knobs):

- `CHARACTER_TEMPO` + `character_tempo()` + `tempo_label()` in `src/entities/player_car.py:41-79`; `PlayerCar.tempo` set in `__init__` and `change_appearance`. Unknown models (the planned `custom` one) fall back to a size-derived value.
- `PowerupEffectsMixin.world_tempo()` (`src/screens/powerup_effects.py:97-102`) = character tempo × slow-mo, floored at `TEMPO_FLOOR = 0.45`. Applied to speed *and* spawn cadence at `endless_screen.py:114-121` and `level_game_screen.py:147-154`.
- Points follow the pace: `on_pass(self.effect_score_mult() * self.car.tempo)`.
- `ObstacleManager._reachable_delta` now divides by the live `time_scale` (`obstacle_manager.py:60-70`) — without that, a fast character was handed climbs it could not make.
- The character-select screen shows the pace and the score multiplier above the preview panel.

**Measured** (level 5, 10 s of play): geometry is untouched — gate spacing is 707 px for every character — while the pace moves as intended.

| character | tempo | gates / 10 s | time inside a gate | points / gate |
|---|---|---|---|---|
| bibble | 0.85 | 4 | 573 ms | 8 |
| camry | 1.00 | 5 | 462 ms | 10 |
| chick | 1.15 | 6 | 339 ms | 11 |

Still open: the per-character `high_scores` map and the size-aware gap floor (both listed under risks) were not built — neither blocks anything today.
