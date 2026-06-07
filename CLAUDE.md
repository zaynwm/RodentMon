# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the game

```bash
python3 rodentmon.py
```

After any edit, verify syntax before running:

```bash
python3 -m py_compile rodentmon.py
```

There are no tests or linter configs. The compile check above is the only automated validation available.

## Architecture

The entire game lives in three files:

- **`rodentmon.py`** — all game logic, data, rendering (~3500 lines)
- **`music.py`** — chiptune engine; synthesises square/triangle wave tracks in memory at runtime
- **`sfx.py`** — 19 synthesised sound effects; self-contained, duplicates wave primitives from `music.py`

Both audio modules are optional — the game catches `ImportError` and runs silently without them.

### Data tables (top of `rodentmon.py`)

All game data is defined as module-level constants before any functions or classes:

- **`SPECIES`** — dict of species name → stats, type, colour, `moves_learn` (level→move name), evolution target
- **`MOVES`** — dict of move name → power, type, acc, desc, optional `"effect"` key
- **`TYPE_CHART`** — attacker type → defender type → float multiplier. Six types: Normal, Sand, Forest, Dark, Water, Ice
- **`TYPE_COLORS`** — type → RGB tuple (used for UI badges and move dots)
- **`ENCOUNTER_TABLES`** — map key → list of `(species, min_lv, max_lv, weight)` tuples
- **`SHOP_ITEMS`** — list of `{species, level, price}` dicts
- **`TRAINER_DATA`** — route key → list of trainer dicts `{name, pos, party, msg_before, msg_after, reward}`
- **`GYM_DATA`** — gym int (1–3) → leader info, party, badge name, reward

### Map system

Maps are plain dicts built by factory functions (`make_hometown()`, `make_town2()`, etc., `make_route()`, `make_interior_*()`) and stored in `Game.maps`. Each map dict has:

```python
{
    "tiles": 2D list of char,   # W H R A F N G D L S P . ~ # T
    "w": int, "h": int,
    "exits": [{x, y, dest, dx, dy}, ...],   # tile-step triggers
    "doors": {(x,y): {action/dest/dx/dy}},  # Z-interact triggers
    "signs": {(x,y): str},
    "trainers": [...],
    "encounters": str,          # key into ENCOUNTER_TABLES
    "spawn": (x, y),
}
```

Tile characters: `#`=border tree, `.`=grass (wild encounters), `~`=water, `P`=path, `W`=wall, `F`=floor, `R`=roof, `H`=exterior wall, `D`=door, `A`=arena, `N`=NPC, `G`=exit tile, `L`=lab equipment, `S`=sign, `T`=trainer.

### Classes

**`Rodent`** — holds species, level, HP, moves list (max 4, later moves randomly replace earlier ones when the cap is hit), XP, and battle stat modifiers. Key methods: `gain_xp()`, `to_dict()` / `from_dict()` for save serialisation.

**`Battle`** — self-contained turn-based battle state machine with states `STATE_INTRO → STATE_MENU → STATE_MOVE_SELECT / STATE_SWITCH → STATE_EXECUTING → STATE_XP → STATE_RESULT`. Handles move ordering by speed, STAB (1.3×), type chart, and special move effects (`drain`, `poison`, `def_up/down`, `atk_down`, `acc_down`, `underdog`, `pierce`).

- `underdog` effect: damage scaled up to 2× when attacker level < defender level (5% per level gap)
- `pierce` effect: overrides sub-1.0 type effectiveness to 1.0, allowing neutral damage in same-type matchups

**`Game`** — top-level state machine. States: `STATE_TITLE`, `STATE_SLOT_SELECT`, `STATE_STARTER`, `STATE_OVERWORLD`, `STATE_BATTLE`, `STATE_MENU`, `STATE_SETTINGS`, `STATE_MERGE`, `STATE_RELEASE`, `STATE_SHOP`. Save/load is JSON via `_save_game()` / `_load_game(slot)` to `rodentmon_save_{slot}.json`. Auto-saves on map transitions and battle ends.

### Adding content

**New species**: add entry to `SPECIES`, add moves to `MOVES`, add to `ENCOUNTER_TABLES` and/or `SHOP_ITEMS`, add drawing branch in `draw_rodent_sprite()`.

**New move effect**: implement in `Battle._calc_damage()` (damage multipliers) and/or `Battle._apply_effect()` (stat changes, drain, poison), add message in `Battle._do_turn()` if needed.

**New map area**: write a `make_*()` factory returning the map dict, register it in `Game.__init__` under `self.maps`, add a display name to `Game._MAP_LABELS`.

**New interior**: use `make_interior_*()` pattern — fixed-width layout string rows, NPC at tile `N`, exit at tile `G`. Wire the entrance door in the parent town's `doors` dict.
