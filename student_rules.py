# student_rules.py — the live rules file
#
# This file is re-read every frame during the game. The conditions below
# decide what happens based on the current game state.
# No functions here: conditions only.
#
# Available states (read-only, discovered in pause by hovering game elements):
#   lives, ammo, shield, score, combo, active_bonus, player_name

# --- Game over: turns the raw freeze into a proper game-over screen ----
if lives == 0:
    game_over = True

# --- Empty magazine alert -----------------------------------------------
if ammo == 0:
    show_empty_alert = True

# --- HUD danger on last life (if / else) --------------------------------
if lives <= 1:
    hud_danger = True
else:
    hud_danger = False

# --- Player rank by score (if / elif / else: intervals) -----------------
if score < 500:
    player_rank = "Rookie"
elif score < 2000:
    player_rank = "Ace"
else:
    player_rank = "Legend"

# --- Critical state: no ammo AND last life (and) ------------------------
if ammo == 0 and lives == 1:
    critical_state = True
else:
    critical_state = False

# --- Active bonus: the ship glows during the effect (is None) -----------
# active_bonus is None when no gold bonus is active, otherwise the
# multiplier (e.g. 2). The ship takes a color during the effect.
if active_bonus is None:
    ship_glow = ""              # no bonus: normal ship
else:
    ship_glow = "yellow"        # bonus active: the ship turns yellow

# --- Name tease (in on string) ------------------------------------------
# Checks if a pattern is found in the player's name, and responds with a quip.
if "player" in player_name:
    name_tease = "\"player\" in the name: not very original"
elif "admin" in player_name:
    name_tease = "Admin access attempt detected"
elif "pro" in player_name:
    name_tease = "Skill is proven, not declared"
elif "xx" in player_name:
    name_tease = "Year-2000 style detected"
elif "noob" in player_name:
    name_tease = "Humility is a fine quality"
else:
    name_tease = ""

# --- Shield display by level (match / case: discrete values) ------------
# shield takes exactly 4 values: 0, 1, 2, 3.
match shield:
    case 3:
        shield_label = "Shield full"
        shield_color = "cyan"
    case 2:
        shield_label = "Shield damaged"
        shield_color = "green"
    case 1:
        shield_label = "Shield low"
        shield_color = "orange"
    case _:
        shield_label = "No shield"
        shield_color = "red"
