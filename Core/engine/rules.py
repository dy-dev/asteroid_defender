"""
rules.py - Runs the live file `student_rules.py` (chapter 3+).
LOCKED: do not modify.

Contract:
- `student_rules.py` is evaluated every frame. The disk is read again
  only when the file has changed; the injected state is refreshed
  every frame.
- The engine INJECTS the current state as plain variables
  (lives, ammo, shield, score, combo, active_bonus, player_name).
- The file holds plain conditions that set OUTPUTS
  (game_over, show_empty_alert, hud_danger, player_rank,
  critical_state, shield_label, shield_color, ship_glow, name_tease).
- The engine reads these outputs back after execution and applies them.
- Safety: a wrong, missing or inconsistent rule never makes the game
  unplayable. On a syntax error, the last valid code is kept. The
  fallback game over is handled elsewhere.
"""
import os

# injected state names (read-only in student_rules.py)
INJECTED = ("lives", "ammo", "score", "combo", "active_bonus", "player_name",
            "shield")

# outputs read back by the engine, with their neutral default value
OUTPUTS = {
    "game_over": False,
    "show_empty_alert": False,
    "hud_danger": False,
    "player_rank": "",
    "critical_state": False,
    "shield_label": "",
    "shield_color": "",
    "ship_glow": "",
    "name_tease": "",
}


class RulesEngine:
    """Loads and executes student_rules.py, with conditional reload."""

    def __init__(self, path):
        self.path = path
        self._source = ""
        self._code = None
        self._mtime = 0
        self._last_error = None
        self._reload_if_changed()

    def _reload_if_changed(self):
        """Only re-reads from disk if the file has changed (mtime)."""
        try:
            mtime = os.path.getmtime(self.path)
        except OSError:
            # file missing: no rules, neutral behavior
            self._code = None
            self._source = ""
            self._mtime = 0
            return
        if mtime == self._mtime and self._code is not None:
            return
        self._mtime = mtime
        try:
            with open(self.path, "r", encoding="utf-8") as fh:
                self._source = fh.read()
            self._code = compile(self._source, self.path, "exec")
            self._last_error = None
        except (SyntaxError, ValueError) as exc:
            # syntactically invalid rule: keep the last valid code
            # if it exists, otherwise no rules. Never crash.
            self._last_error = exc
            if self._code is None:
                self._code = None

    def evaluate(self, state):
        """Executes the rules with the injected state. Returns the dict of
        outputs (default values for the outputs the file does not set)."""
        self._reload_if_changed()
        outputs = dict(OUTPUTS)  # valeurs neutres
        if self._code is None:
            return outputs
        # namespace: injected states (read) + pre-initialized outputs
        ns = {k: state.get(k) for k in INJECTED}
        ns.update(outputs)
        try:
            exec(self._code, {"__builtins__": _SAFE_BUILTINS}, ns)
        except Exception as exc:  # noqa: BLE001
            # runtime error (unknown name, type...): break nothing,
            # return outputs as set before the error.
            self._last_error = exc
        # read back only known outputs
        for key in OUTPUTS:
            if key in ns:
                outputs[key] = ns[key]
        return outputs

    @property
    def last_error(self):
        return self._last_error


# A safe subset of builtins: the rules are simple conditions;
# no need to open the full environment. `match`/`in`/`is`
# work without builtins. A few conversions are exposed.
_SAFE_BUILTINS = {
    "True": True, "False": False, "None": None,
    "int": int, "float": float, "str": str, "bool": bool,
    "len": len, "abs": abs, "min": min, "max": max,
}
