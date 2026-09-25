# Asteroid Defender

Project for the introduction to Python course.

## ⚠ Python version — read this first

This project needs **Python 3.10 to 3.12** (ideally **3.12**).

pygame, the game library, **does not install** on the most recent
Python versions (3.13, 3.14): the install tries to recompile everything
and fails. Use Python 3.12.

## Installation (in order, without skipping a step)

The order matters. Opening the project and letting PyCharm do the rest
ends with an environment created automatically with the **latest**
Python version — the one that does not work. The environment must be
created by hand **first**.

1. **Create the virtual environment with Python 3.12.**
   Two paths lead to the same screen in PyCharm, either one:

   - through the settings: *Settings → Project → Python Interpreter →
     Add Interpreter → Add Local Interpreter*
   - or, shorter: click the **interpreter selector**, at the bottom
     right of the status bar, then *Add New Interpreter →
     Add Local Interpreter*

   In both cases, then choose *Virtualenv Environment → New*,
   then **Base interpreter: Python 3.12**.
   (If 3.12 does not appear, install it first — see below.)

2. **Install the dependencies** once the venv is created and active:

       python -m pip install -r requirements.txt

3. **Run the game**: in the `Core/` folder, **right click on
   `main.py` → Run 'main'**. This right click creates the run
   configuration automatically; after that, the ▶ button at the top
   right is enough.

The game **always** starts from **`Core/main.py`**, never from
`student_config.py`.

### If Python 3.12 is not on the machine

Download it from **python.org/downloads** (pick 3.12.x), install it,
then go back to step 1: PyCharm will offer 3.12 as the base
interpreter.

## What the root contains

    asteroid_defender/
    ├── student_config.py   ★ values, read once at startup
    ├── student_rules.py    ★ rules, read again and again during play
    ├── student_loops.py    ★ repetitions, played when an event happens
    ├── images/             personal visuals (bonus mission)
    ├── README.md           this file
    ├── requirements.txt    dependencies (pygame)
    └── Core/               the engine — LOCKED, do not touch

The whole engine lives in **Core/**, which never needs to be opened.
The working files are the three `student_*.py` files, at the root.

## Finding the exact names

Pause the game with **Esc**: the concept map appears. It lists every
feature, shows the ones already active, and gives on hover the
**exact name** to write in `student_config.py`.

The name must be copied letter for letter — same letters, same case,
same underscores. `nb_ammo` works, `nbAmmo` unlocks nothing.

The same tooltip also gives the states to read in `student_rules.py`
("TO READ in the rules" section) and the events to write in
`student_loops.py` ("REPETITIONS" section).

## Controls

| Key | Effect |
|-----|--------|
| ← → | move the ship |
| Space | fire |
| Space held | charged shot (release to fire) |
| B | burst fire |
| Tab | switch weapon |
| Esc | concept map / resume |
| R | replay (end screen) |

## The habit to build

Change a value → save → run `Core/main.py` again →
observe.
