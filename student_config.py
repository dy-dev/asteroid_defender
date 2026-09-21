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

# title shown at the top of the window
window_title = "Asteroid Defender"

# name shown in the HUD
player_name = "Nova"

# amount of ammunition: the ship can fire
nb_ammo = 40

# movement speed of the ship
ship_speed = 6

# speed of the bullets
bullet_speed = 9.0

# number of lives at the start
starting_lives = 3
