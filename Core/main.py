"""
main.py - Entry point of the game.
LOCKED: do not modify.

This is the file to run (right click > Run), never student_config.py.
"""

import os
import sys

# This file lives in Core/. Python must find:
#  - the engine (engine/) and language.py, next to this file, in Core/
#  - the student files (student_config.py...) and the images/ folder,
#    at the project root, one level above Core/
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_HERE, _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)
os.chdir(_ROOT)

from engine.i18n import t  # noqa: E402 - needs the paths above


def _print(msg):
    """Prints a message, even on a console that cannot show accents."""
    try:
        print(msg)
    except UnicodeEncodeError:
        enc = sys.stdout.encoding or "ascii"
        print(msg.encode(enc, errors="replace").decode(enc))


# ---------------------------------------------------------------------
#  Python version check
#  pygame has no ready-made build for the latest Python versions: on a
#  too recent Python, the install tries to recompile everything and
#  fails. The check below shows a clear message instead of a crash.
# ---------------------------------------------------------------------
_PY_MIN = (3, 10)
_PY_MAX = (3, 12)   # latest version with a ready-to-install pygame


def _check_python_version():
    v = sys.version_info
    if _PY_MIN <= (v.major, v.minor) <= _PY_MAX:
        return
    cur = f"{v.major}.{v.minor}.{v.micro}"
    msg = (
        "\n" + "=" * 62 + "\n"
        "  " + t("py_wrong_title") + "\n"
        + "=" * 62 + "\n"
        + t("py_wrong_body",
            min=f"{_PY_MIN[0]}.{_PY_MIN[1]}",
            max=f"{_PY_MAX[0]}.{_PY_MAX[1]}",
            cur=cur)
        + "=" * 62 + "\n"
    )
    _print(msg)
    # Also tries a graphical window if Tk is available (more visible
    # than the console)
    try:
        import tkinter
        from tkinter import messagebox
        root = tkinter.Tk()
        root.withdraw()
        messagebox.showerror(t("py_wrong_window"), msg)
        root.destroy()
    except Exception:  # noqa: BLE001
        pass
    sys.exit(1)


_check_python_version()

try:
    import pygame
except ModuleNotFoundError:
    _print(
        "\n" + "=" * 62 + "\n"
        + t("pygame_missing")
        + "=" * 62 + "\n"
        + t("pygame_install")
        + "=" * 62 + "\n"
    )
    sys.exit(1)

from engine import config as C  # noqa: E402
from engine.game import Game  # noqa: E402
from engine.hud import Fonts  # noqa: E402


def main():
    pygame.init()
    screen = pygame.display.set_mode((C.WIDTH, C.HEIGHT))
    clock = pygame.time.Clock()
    fonts = Fonts()

    game = Game(screen, fonts)
    pygame.display.set_caption(str(game.features.window_title))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif not game.handle_event(event):
                running = False

        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(C.FPS)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
