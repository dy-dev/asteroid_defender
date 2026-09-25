# =====================================================================
#  student_loops.py
#
#  The game repetitions file. It is empty for now: that is normal.
#
#  -------------------------------------------------------------------
#  How it works
#  -------------------------------------------------------------------
#
#  Each block matches a game event and starts with a condition on that
#  event, for example:  if event == "countdown":
#  The block holds a loop. When the event happens, the game runs that
#  loop one turn at a time, spread over time: the effect of each turn
#  shows on screen — the countdown value changing, the gauge rising, a
#  projectile leaving.
#
#  No functions here: only loops inside event blocks.
#
#  -------------------------------------------------------------------
#  Where to find the names
#  -------------------------------------------------------------------
#
#  The events are discovered in the game. Pause the game with Esc, then
#  hover over the ship: the "REPETITIONS in student_loops.py" section
#  gives the exact name of each event, its effect and the values
#  provided inside the block.
#
#  -------------------------------------------------------------------
#  If something goes wrong
#  -------------------------------------------------------------------
#
#  A faulty loop never blocks the game: the game stops it and shows the
#  problem in a red banner at the bottom of the screen. A loop that
#  never ends is cut after 1000 turns.
# =====================================================================
