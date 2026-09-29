# Convention: imports go at the top of the file.
import random

# =====================================================================
#  student_config.py
#
#  The only file to fill in. It fills up session after session: every
#  line already written stays, the new ones are added below.
#
#  -------------------------------------------------------------------
#  How to write a setting
#  -------------------------------------------------------------------
#
#  A setting fits on a single line, always in the same form:
#
#      name = value
#
#  On the left, the name of the setting. On the right, the value to
#  give it.
#
#  Text goes between quotes, numbers go without:
#
#      name = "some text between quotes"
#      name = 12
#
#  A number placed between quotes becomes text: the game can no longer
#  use it as a quantity.
#
#  -------------------------------------------------------------------
#  Where to find the names
#  -------------------------------------------------------------------
#
#  No name is given here: they are discovered in the game.
#  Pause the game with Esc, then hover over an element on screen: the
#  ship, the top bar, the play area. Each element shows the available
#  settings, their exact name, their type and their effect.
#
#  The name must be copied letter for letter: same letters, same case,
#  same underscores. A misspelled name activates nothing, and the game
#  keeps running without any error.
#
#  -------------------------------------------------------------------
#  Seeing the result
#  -------------------------------------------------------------------
#
#  Write the line, save the file, then run Core/main.py again.
#  The effect appears at the next launch.
#
#  The game always starts from Core/main.py, never from this file.
# =====================================================================

# name shown in the HUD
# Text is a sequence of characters: take a slice of it.
full_name = "Nova Starfighter"
player_name = full_name[:4]

# title shown at the top of the window
window_title = f"Asteroid Defender - pilot {player_name}"

# amount of ammunition: the ship can fire
nb_ammo = 40

# movement speed of the ship
ship_speed = 6

# speed of the bullets
bullet_speed = 9.0

# number of lives at the start
starting_lives = 3

# base points for an asteroid
base_hit_points = 10

# multiplier applied when the bonus is picked up
bonus_points = 3

# points per hit: a calculation between variables
points_per_hit = base_hit_points * bonus_points

# the chained score is multiplied by this number
combo_multiplier = 2

# seconds without firing before the combo resets
combo_reset_delay = 3.0

# boolean set by hand: shows the debug overlay
show_debug = True

# resulting boolean: hard mode with fewer than 3 lives
is_hard = starting_lives < 3

# threshold above which the HUD changes
highlight_score = 1000

# threshold below which an alert appears
low_ammo_threshold = 5

# every N points, a bonus appears
bonus_threshold = 500

# duration of the multiplier, in seconds
bonus_duration = 5.0

# --- Chapter 5: collections and randomness -------------------------------

# A list: the colours of the bonuses that drop during play.
powerup_colors = ["red", "blue", "green"]
powerup_colors.append("pink")

# A simple dictionary: the effect of each bonus colour.
# A colour missing from the dictionary gives a bonus that restores a life.
powerup_effects = {
    "red": "heal",
    "blue": "ammo_refill",
    "green": "shield_up",
}
powerup_effects["pink"] = "rapid_fire"

# A dictionary of dictionaries: each weapon paired with its characteristics.
# Press Tab to switch from one weapon to another.
weapons = {
    "laser": {"damage": 1, "cooldown": 8},
    "cannon": {"damage": 3, "cooldown": 30},
    "gatling": {"damage": 1, "cooldown": 3},
}

# A set: the weapons available, with no possible duplicate.
unlocked_weapons = {"laser", "cannon"}

# A tuple: the starting position, which must not change.
# The horizontal coordinate is drawn at random on each launch.
start_position = (random.randint(100, 700), 510)
