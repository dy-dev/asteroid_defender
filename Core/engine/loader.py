"""
loader.py - Detects what student_config.py defines.
LOCKED: do not modify.

The engine requires nothing. It looks at what exists in
student_config.py and adapts the game. When a name is missing, a
degraded default behavior takes over, so the game always runs, even
with an empty file.
"""

import ast
import io
import os
import re
import sys
import tokenize
import types

from engine import config as C
from engine.i18n import t


# ----------------------------------------------------------------------
#  Tolerant import of the student file
# ----------------------------------------------------------------------

# Game states: they exist in student_rules.py (chapter 3), never in the
# configuration. Using one in student_config.py means a condition was
# written in the wrong file.
GAME_STATES = ("lives", "ammo", "score", "shield", "combo", "active_bonus",
               "player_name")
MAX_SYNTAX_FIXES = 20
# the answers difficulty_level may give
DIFFICULTY_LEVELS = ("easy", "normal", "hard")
# loader.py is in Core/engine/: student_config.py is two levels above
CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "student_config.py")


def import_student_config():
    """Runs student_config.py without ever crashing the game.

    The file is run statement by statement: a faulty statement is
    skipped and the others still apply. A line Python cannot read at all
    (syntax error) is set aside, with the block it opens, and the rest
    of the file is read again. Returns (module, problems): problems is
    the list of messages, one per skipped part, in file order.
    """
    module = types.ModuleType("student_config")
    problems = []
    path = CONFIG_PATH
    if not os.path.isfile(path):
        return module, problems
    module.__file__ = path
    try:
        with open(path, encoding="utf-8-sig") as fh:
            lines = fh.read().split("\n")
    except Exception as exc:  # noqa: BLE001 - unreadable file
        problems.append(t("error_runtime_noline", kind=type(exc).__name__))
        return module, problems

    tree = None
    for _ in range(MAX_SYNTAX_FIXES):
        try:
            tree = ast.parse("\n".join(lines), path)
            break
        except SyntaxError as exc:
            idx = _faulty_index(exc, lines)
            if idx is None:
                problems.append((exc.lineno or 0, t(
                    "error_syntax", line=exc.lineno or "?", msg=exc.msg, code="")))
                break
            code = lines[idx]
            problems.append((idx + 1, _with_hint(
                t("error_syntax", line=idx + 1, msg=exc.msg, code=_short(code)),
                code)))
            _set_aside(lines, idx)
    if tree is None:
        return module, _in_file_order(problems)

    sys.modules["student_config"] = module
    for node in tree.body:
        stmt = ast.Module(body=[node], type_ignores=[])
        try:
            exec(compile(stmt, path, "exec"), module.__dict__)
        except Exception as exc:  # noqa: BLE001 - every error must be caught
            problems.append((node.lineno, _runtime_problem(exc, node, lines)))
    return module, _in_file_order(problems)


def _faulty_index(exc, lines):
    """Index of the line to set aside for a syntax error, or None when
    no line can be blamed. A block opened without a body is reported
    by Python on the next line ("expected an indented block after 'if'
    statement on line N"): the line to set aside is then line N."""
    found = re.search(r"on line (\d+)", str(exc.msg or ""))
    line = int(found.group(1)) if found else exc.lineno
    if not line or line > len(lines) or not lines[line - 1].strip():
        return None
    return line - 1


def _set_aside(lines, idx):
    """Blanks line idx and, when it opens a block (ends with ":"), the
    more indented lines under it."""
    head = lines[idx]
    lines[idx] = ""
    if not head.rstrip().endswith(":"):
        return
    indent = len(head) - len(head.lstrip())
    j = idx + 1
    while j < len(lines):
        line = lines[j]
        if line.strip() and len(line) - len(line.lstrip()) <= indent:
            break
        lines[j] = ""
        j += 1


def _in_file_order(problems):
    """Messages of (line, message) pairs, sorted by line."""
    return [msg for _, msg in sorted(problems, key=lambda p: p[0])]


def _with_hint(msg, code):
    """Adds the pointer to student_rules.py when the faulty line uses a
    game state (a condition written in the wrong file)."""
    try:
        names = {tok.string for tok in tokenize.generate_tokens(io.StringIO(code).readline)
                 if tok.type == tokenize.NAME}
    except Exception:  # noqa: BLE001 - half-written line
        names = set(code.replace("(", " ").replace(")", " ").split())
    if names & set(GAME_STATES):
        return msg + " — " + t("config_hint_rules")
    return msg


def _short(code, limit=48):
    """The faulty line, trimmed to fit the pause screen."""
    code = (code or "").strip()
    return code if len(code) <= limit else code[:limit - 3] + "..."


def display_name(name, limit=16):
    """Player name as shown on screen: cut to `limit` characters, the
    last one being an ellipsis. The value given to the rules is not
    affected."""
    name = str(name)
    return name if len(name) <= limit else name[:limit - 1] + "…"


def _runtime_problem(exc, node, lines):
    """Message for a statement of student_config.py that raised: its
    line, the error type, the faulty code, and for an unknown name the
    name itself (plus the pointer to student_rules.py for a game state).
    Python's own sentence stays out: the name says more to a beginner."""
    kind = type(exc).__name__
    line = getattr(node, "lineno", None)
    code = lines[line - 1] if line and line <= len(lines) else ""
    name = getattr(exc, "name", None) if isinstance(exc, NameError) else None
    if name:
        msg = t("error_name", line=line, name=name, code=_short(code))
        if name in GAME_STATES:
            msg += " — " + t("config_hint_rules")
        return msg
    if line:
        return t("error_runtime", line=line, kind=kind, code=_short(code))
    return t("error_runtime_noline", kind=kind)


# ----------------------------------------------------------------------
#  Safe access
# ----------------------------------------------------------------------

def get_value(cfg, name, default, expected=None):
    """Reads a student variable, otherwise returns the degraded default.

    expected: expected type or tuple of types. If the value does not
    match, the default is kept (a value of an unusable type must not
    break the game).
    """
    if not hasattr(cfg, name):
        return default, False
    value = getattr(cfg, name)
    if expected is not None and not isinstance(value, expected):
        return default, False
    return value, True


def has_callable(cfg, name):
    """True if the student has defined a function (or any callable)."""
    return callable(getattr(cfg, name, None))


def safe_call(cfg, name, default, *args, on_error=None, on_none=None, **kwargs):
    """Calls a student function with a safety net.

    If the function is missing, raises, or returns None, the default
    is used. No traceback ever reaches the screen. When it raises,
    on_error (if given) receives the exception, so that the game can
    name the function in its red banner. A None result is not an error:
    on_none (if given) is called, for the yellow warning banner.
    """
    fn = getattr(cfg, name, None)
    if not callable(fn):
        return default, False
    try:
        result = fn(*args, **kwargs)
    except Exception as exc:  # noqa: BLE001
        if on_error is not None:
            on_error(exc)
        return default, False
    if result is None:
        if on_none is not None:
            on_none()
        return default, False
    return result, True


# ----------------------------------------------------------------------
#  Dict / object normalization
# ----------------------------------------------------------------------
#  Weapons and power-ups can be described with dicts or as objects.
#  The engine accepts both forms without breaking.

def field(item, name, default=None):
    """Reads a field, whether the item is a dict or an object."""
    if isinstance(item, dict):
        return item.get(name, default)
    return getattr(item, name, default)


def normalize_powerup(item):
    """Normalizes a power-up (dict or PowerUp object) to a unified form."""
    return {
        "color": field(item, "color", "white"),
        "effect": field(item, "effect", "heal"),
        "duration": field(item, "duration", 0),
        "source": item,
    }


def normalize_weapon(name, item):
    """Normalizes a weapon (dict or Weapon object) to a unified form.

    A Weapon object manages its own cooldown through its methods: the
    engine never touches its internal state, it calls can_fire() /
    fire() / tick(). A dict has no methods: the engine counts the time
    for it.
    """
    is_object = not isinstance(item, dict) and (
        callable(getattr(item, "fire", None))
        or callable(getattr(item, "can_fire", None))
    )
    return {
        "name": field(item, "name", name),
        "damage": field(item, "damage", field(item, "_damage", 1)),
        "cooldown": field(item, "cooldown", field(item, "_cooldown", 12)),
        "object": item if is_object else None,
    }


# ----------------------------------------------------------------------
#  Full configuration loading
# ----------------------------------------------------------------------

class StudentFeatures:
    """State of all concepts: value used + enabled or not.

    `unlocked` feeds the pause screen: it tells which names are already
    defined and which remain, with the exact expected name.
    """

    def __init__(self):
        self.cfg = None
        self.problem = None
        self.problems = []
        self.unlocked = {}
        self.call_error = None      # last error raised by a student function
        self.call_warnings = []     # (function, message) not yet shown
        self._warned = set()        # functions already warned about

    # -- utilitaires internes -------------------------------------------------
    def _val(self, name, default, expected=None):
        value, ok = get_value(self.cfg, name, default, expected)
        self.unlocked[name] = ok
        return value

    def _fn(self, name):
        ok = has_callable(self.cfg, name)
        self.unlocked[name] = ok
        return ok

    # -- chargement -----------------------------------------------------------
    def load(self):
        self.cfg, self.problems = import_student_config()
        # first problem for the pause screen, with the count of the others
        self.problem = None
        if self.problems:
            self.problem = self.problems[0]
            if len(self.problems) > 1:
                self.problem += " " + t("config_more", n=len(self.problems) - 1)
        cfg = self.cfg

        # --- first variables ----------------------------
        self.window_title = self._val("window_title", t("default_title"), str)
        self.player_name = self._val("player_name", t("default_player_name"), str)
        self.nb_ammo = self._val("nb_ammo", 0, (int, float))
        self.ship_speed = self._val("ship_speed", 0, (int, float))
        self.bullet_speed = self._val("bullet_speed", 8.0, (int, float))
        self.starting_lives = self._val("starting_lives", 3, int)

        # --- score, combo, bonus, comparisons ----------------------------
        # Neutral defaults: nothing should look like success.
        # Until base_hit_points / points_per_hit are defined,
        # the score doesn't increase (0). Default thresholds never
        # trigger (unreachable value).
        self.base_hit_points = self._val("base_hit_points", 0, (int, float))
        self.bonus_points = self._val("bonus_points", 1, (int, float))
        self.points_per_hit = self._val("points_per_hit", 0, (int, float))
        self.combo_multiplier = self._val("combo_multiplier", 1, (int, float))
        self.combo_reset_delay = self._val("combo_reset_delay", 0, (int, float))
        self.show_debug = self._val("show_debug", False, bool)
        self.is_hard = self._val("is_hard", False, bool)
        self.highlight_score = self._val("highlight_score", 10 ** 9, (int, float))
        self.low_ammo_threshold = self._val("low_ammo_threshold", -1, (int, float))
        self.bonus_threshold = self._val("bonus_threshold", 10 ** 9, (int, float))
        self.bonus_duration = self._val("bonus_duration", 0, (int, float))
        # chapter 2 sprites
        self.asteroid_sprite = self._val("asteroid_sprite", None, str)
        self.bonus_sprite = self._val("bonus_sprite", None, str)
        # compat: older name of points_per_hit, dormant.
        self.score_per_hit = self._val("score_per_hit", 0, (int, float))

        # --- booleans and conditions --------------------------
        self.friendly_fire = self._val("friendly_fire", False, bool)
        self.has_difficulty = self._fn("difficulty_level")

        # --- for loop -----------------------------------------
        self.has_spawn_row = self._fn("spawn_row")

        # --- while loop ---------------------------------------
        self.reload_time = self._val("reload_time", 0, (int, float))
        self.start_countdown = self._val("start_countdown", 0, (int, float))
        self.has_keep_firing = self._fn("should_keep_firing")

        # --- strings ------------------------------------------
        self.has_hud_text = self._fn("hud_text")
        self.has_game_over_text = self._fn("game_over_text")

        # --- collections --------------------------------------
        self.powerup_colors = self._val("powerup_colors", [], (list, tuple))
        self.powerup_effects = self._val("powerup_effects", {}, dict)
        self.start_position = self._val("start_position", C.DEFAULT_START, (tuple, list))
        self.unlocked_weapons = self._val("unlocked_weapons", set(), (set, frozenset))
        raw_weapons = self._val("weapons", {}, dict)

        # --- functions ----------------------------------------
        self.has_damage = self._fn("damage")
        self.has_spawn_pattern = self._fn("spawn_pattern")

        # --- modules and scope --------------------------------
        self.global_difficulty = self._val("GLOBAL_DIFFICULTY", 1.0, (int, float))

        # --- classes ------------------------------------------
        raw_powerups = self._val("powerups", [], (list, tuple))
        self.powerups = [normalize_powerup(p) for p in raw_powerups]

        # --- encapsulation ------------------------------------
        single_weapon = getattr(cfg, "weapon", None)
        self.unlocked["weapon"] = single_weapon is not None

        # Unified weapon table (dicts and Weapon objects)
        self.weapons = {}
        for name, item in (raw_weapons or {}).items():
            self.weapons[name] = normalize_weapon(name, item)
        if single_weapon is not None:
            wname = field(single_weapon, "name", "weapon")
            self.weapons[wname] = normalize_weapon(wname, single_weapon)
        if not self.weapons:
            self.weapons = {"laser": {"name": "laser", "damage": 1,
                                      "cooldown": 12, "object": None}}

        # --- Enemy types: classes with a move() method -------------------
        raw_types = self._val("enemy_types", [], (list, tuple))
        self.enemy_types = [t for t in raw_types if isinstance(t, type)]

        # --- files and exceptions -----------------------------
        self.has_save_highscore = self._fn("save_highscore")
        self.has_load_highscores = self._fn("load_highscores")

        # --- free extension point -----------------------------
        self.has_student_update = self._fn("student_update")
        self.has_student_draw = self._fn("student_draw")

        # --- Bonus missions: personal visuals ------------------------------
        # Image paths declared by the student. If missing or unreadable,
        # the engine falls back to geometric drawing.
        self.ship_sprite = self._val("ship_sprite", None, str)
        self.enemy_sprite = self._val("enemy_sprite", None, str)
        self.bullet_sprite = self._val("bullet_sprite", None, str)
        self.powerup_sprite = self._val("powerup_sprite", None, str)
        self.background_image = self._val("background_image", None, str)

        return self

    # -- student function calls, always protected ----------------------------

    def _call(self, name, default, *args, none_key="warn_none_value"):
        """safe_call that keeps the error of a function that raises and
        the warning of a function that returns nothing (none_key: its
        text, None when returning nothing is normal)."""
        def remember(exc):
            self.call_error = t("error_function", name=name,
                                kind=type(exc).__name__, msg=exc)
        def nothing():
            if none_key:
                self._warn(name, t(none_key, name=name))
        return safe_call(self.cfg, name, default, *args, on_error=remember,
                         on_none=nothing)

    def pop_call_error(self):
        """Last error raised by a student function, then forgotten."""
        err, self.call_error = self.call_error, None
        return err

    def _warn(self, name, msg):
        """Keeps a warning about a student function, once per function."""
        if name not in self._warned:
            self._warned.add(name)
            self.call_warnings.append((name, msg))

    def pop_call_warnings(self):
        """Warnings about student functions not shown yet, then forgotten."""
        found, self.call_warnings = self.call_warnings, []
        return found

    def _warn_type(self, name, expected_key):
        self._warn(name, t("warn_bad_type", name=name, expected=t(expected_key)))

    def difficulty(self, score):
        value, ok = self._call("difficulty_level", "easy", score)
        if ok and str(value).lower() not in DIFFICULTY_LEVELS:
            self._warn("difficulty_level", t(
                "warn_bad_answer", name="difficulty_level",
                value=f'"{value}"' if isinstance(value, str) else repr(value),
                default="easy"))
        return value if isinstance(value, str) else "easy"

    def row_positions(self, n):
        default = [C.WIDTH // 2]
        value, ok = self._call("spawn_row", default, n)
        if not ok:
            return default
        if not isinstance(value, (list, tuple)):
            self._warn_type("spawn_row", "expected_number_list")
            return default
        clean = [p for p in value if isinstance(p, (int, float))]
        if not clean:
            self._warn_type("spawn_row", "expected_number_list")
        elif len(clean) < len(value):
            self._warn("spawn_row", t("warn_spawn_row_items", name="spawn_row"))
        return clean or default

    def keep_firing(self, ammo, trigger_held):
        default = ammo > 0 and trigger_held
        value, ok = self._call("should_keep_firing", default,
                              ammo, trigger_held)
        return bool(value) if ok else default

    def hud(self, name, score, ammo, chapter=1):
        # from chapter 6 the default announces the function to write:
        # a default must not look like a success
        if chapter >= 6:
            default = t("missing_hud_text")
        else:
            default = t("default_hud_line", name=display_name(name),
                        score=score, ammo=ammo)
        value, ok = self._call("hud_text", default, name, score, ammo,
                               none_key="warn_none_text")
        return str(value) if ok else default

    def game_over(self, name, score, chapter=1):
        if chapter >= 6:
            default = t("missing_game_over_text")
        else:
            default = t("default_game_over_line", name=display_name(name),
                        score=score)
        value, ok = self._call("game_over_text", default, name, score,
                               none_key="warn_none_text")
        return str(value) if ok else default

    def compute_damage(self, base, multiplier=1.0):
        value, ok = self._call("damage", base, base, multiplier)
        if not ok:
            return base
        if not isinstance(value, (int, float)):
            self._warn_type("damage", "expected_number")
            return base
        return int(value)

    def wave_pattern(self, wave):
        default = (1, 2.0)
        value, ok = self._call("spawn_pattern", default, wave)
        if not ok:
            return default
        try:
            count, speed = value
            return int(count), float(speed)
        except (TypeError, ValueError):
            self._warn_type("spawn_pattern", "expected_number_pair")
            return default

    def save_score(self, name, score):
        # a function that only writes a file returns nothing: no warning
        self._call("save_highscore", None, name, score, none_key=None)

    def load_scores(self):
        value, ok = self._call("load_highscores", [])
        if not ok or not isinstance(value, (list, tuple)):
            return []
        return list(value)[:C.HIGHSCORE_SHOWN]
