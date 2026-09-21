"""
clipboard.py - Copies a short text to the clipboard.
LOCKED: do not modify.

Copies the exact NAME of a variable from the pause tooltip, so it does
not have to be typed by hand.

Several methods are tried in turn, since the clipboard depends on the
platform. If none works, the function returns False and never crashes:
the tooltip shows the name in plain text anyway.
"""


def copy_text(text):
    """Tries to copy `text`. Returns True if a method succeeded."""
    text = str(text)

    # 1) API pygame moderne (pygame >= 2.2 : scrap.put_text)
    try:
        import pygame.scrap as scrap
        if hasattr(scrap, "put_text"):
            scrap.put_text(text)
            return True
    except Exception:  # noqa: BLE001
        pass

    # 2) ancien pygame.scrap (SDL) — fonctionne bien sous Windows
    try:
        import pygame
        if not pygame.scrap.get_init():
            pygame.scrap.init()
        pygame.scrap.put(pygame.SCRAP_TEXT, text.encode("utf-8"))
        return True
    except Exception:  # noqa: BLE001
        pass

    # 3) tkinter (included in standard Python, independent of SDL display)
    try:
        import tkinter
        r = tkinter.Tk()
        r.withdraw()
        r.clipboard_clear()
        r.clipboard_append(text)
        r.update()
        r.destroy()
        return True
    except Exception:  # noqa: BLE001
        pass

    return False
