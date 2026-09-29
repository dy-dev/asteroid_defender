# student_loops.py — the repetitions file
#
# Each block matches a game event. When the event happens, the game runs
# its loop one turn at a time, spread over time: the effect of each turn
# shows on screen.
# No functions here: only loops inside event blocks.
#
# Available events (found while paused, by hovering over the ship):
#   countdown · charging · burst

# --- Start countdown: repeat while the counter is not zero ---------------
if event == "countdown":
    while countdown > 0:
        countdown -= 1

# --- Charged shot: climb to the maximum, then leave the loop -------------
if event == "charging":
    while True:
        charge += charge_rate
        if charge >= max_charge:
            break

# --- Burst: repeat a known number of times, skipping every other turn ----
if event == "burst":
    for i in range(burst_count):
        if i % 2 == 1:
            continue
        fired += 1
