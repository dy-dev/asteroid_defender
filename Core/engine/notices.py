"""
notices.py - Warnings: what the game ignored or replaced without blocking.
LOCKED: do not modify.

The red banner stays for the errors that stop a file from working. The
warnings found here go to the yellow banner: a near-miss name, an
unknown color or effect, a weapon key the engine does not read. They
change nothing in the game, they only say what was set aside.
"""

import types

from engine import config as C
from engine.i18n import t


WEAPON_KEYS = ("damage", "cooldown")
MAX_DISTANCE = 2


def _distance(a, b):
    """Edit distance (insert, delete, replace, swap two neighbours)."""
    rows = [list(range(len(b) + 1))]
    for i in range(1, len(a) + 1):
        row = [i] + [0] * len(b)
        for j in range(1, len(b) + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            row[j] = min(rows[i - 1][j] + 1, row[j - 1] + 1,
                         rows[i - 1][j - 1] + cost)
            if (i > 1 and j > 1 and a[i - 1] == b[j - 2]
                    and a[i - 2] == b[j - 1]):
                row[j] = min(row[j], rows[i - 2][j - 2] + 1)
        rows.append(row)
    return rows[-1][-1]


def suggest(name, candidates):
    """Closest candidate to name (case ignored, at most two letters
    apart, one for a short name), or None."""
    low = name.lower()
    limit = 1 if len(name) <= 4 else MAX_DISTANCE
    best, best_d = None, limit + 1
    for cand in candidates:
        d = _distance(low, cand.lower())
        if d < best_d:
            best, best_d = cand, d
    return best


def _quoted(value):
    return f'"{value}"' if isinstance(value, str) else repr(value)


def _is_color(value):
    return isinstance(value, str) and value.lower().strip() in C.COLOR_NAMES


def check_config(features, chapter, catalog):
    """Warnings for student_config.py, in file order of the checks.

    catalog: (name, chapter) pairs of the pause catalog. Every catalog
    name and every name the loader reads counts as known; only the
    names revealed at this chapter are offered as a suggestion, so a
    warning never reveals a later notion.
    """
    cfg = features.cfg
    if cfg is None:
        return []
    warnings = []
    known = {n for n, _ in catalog} | set(features.unlocked)
    revealed = [n for n, chap in catalog if chap <= chapter]

    def checked(name):
        # a collection is checked once the game reads it at this chapter
        return features.unlocked.get(name) and name in revealed

    for name, value in vars(cfg).items():
        if name.startswith("_") or name in known:
            continue
        if isinstance(value, (types.ModuleType, type)):
            continue
        hint = suggest(name, revealed)
        if hint:
            warnings.append(t("warn_unknown_name", name=name, hint=hint))

    known_colors = ", ".join(C.COLOR_NAMES)
    if checked("powerup_colors"):
        for color in features.powerup_colors:
            if not _is_color(color):
                warnings.append(t("warn_unknown_color", where="powerup_colors",
                                  color=_quoted(color), known=known_colors))
    if checked("powerup_effects"):
        for color, effect in features.powerup_effects.items():
            if not _is_color(color):
                warnings.append(t("warn_unknown_color", where="powerup_effects",
                                  color=_quoted(color), known=known_colors))
            if str(effect).lower() not in C.POWERUP_EFFECTS:
                warnings.append(t("warn_unknown_effect", color=_quoted(color),
                                  effect=_quoted(effect),
                                  known=", ".join(C.POWERUP_EFFECTS)))

    raw_weapons = getattr(cfg, "weapons", None) if checked("weapons") else None
    for wname, item in (raw_weapons or {}).items():
        if not isinstance(item, dict):
            continue
        for key in item:
            if key not in WEAPON_KEYS:
                warnings.append(t("warn_weapon_key", weapon=_quoted(wname),
                                  field=_quoted(key), known=", ".join(WEAPON_KEYS)))
    if checked("unlocked_weapons"):
        for wname in sorted(features.unlocked_weapons, key=str):
            if wname not in (raw_weapons or {}):
                warnings.append(t("warn_unlocked_missing", weapon=_quoted(wname)))
    return warnings
