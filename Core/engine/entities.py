"""
entities.py - Internal game objects (ship, bullets, asteroids, bonuses).
LOCKED: do not modify.

Everything is drawn with geometric shapes: the project needs no image
file and runs anywhere without missing assets.
"""

import math
import random

import pygame

from engine import assets
from engine import config as C


class Ship:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.lives = 3
        self.ammo = 0
        self.invuln = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x - C.SHIP_W / 2),
                           int(self.y - C.SHIP_H / 2),
                           C.SHIP_W, C.SHIP_H)

    def move(self, dx, speed):
        self.x += dx * speed
        half = C.SHIP_W / 2
        self.x = max(half, min(C.WIDTH - half, self.x))

    def draw(self, surf, thrust=False, sprite=None, body_color=None):
        # blinks during invincibility
        if self.invuln > 0 and (self.invuln // 4) % 2 == 0:
            return
        cx, cy = int(self.x), int(self.y)
        image = assets.load(sprite, (C.SHIP_W, C.SHIP_H))
        if image is not None:
            if body_color:
                # halo: a picture cannot be recolored, so a translucent
                # disc of the glow color is drawn behind it
                r = max(C.SHIP_W, C.SHIP_H) // 2 + 8
                halo = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(halo, (*body_color[:3], 110), (r, r), r)
                surf.blit(halo, (cx - r, cy - r))
            assets.blit_centered(surf, image, cx, cy)
            if thrust:
                pygame.draw.polygon(surf, C.ORANGE, [
                    (cx - 5, cy + C.SHIP_H // 4), (cx + 5, cy + C.SHIP_H // 4),
                    (cx, cy + C.SHIP_H // 2 + random.randint(4, 12))])
            return
        h = C.SHIP_H // 2
        w = C.SHIP_W // 2
        body = [(cx, cy - h), (cx - w, cy + h), (cx, cy + h // 2), (cx + w, cy + h)]
        pygame.draw.polygon(surf, body_color or C.BLUE, body)
        pygame.draw.polygon(surf, C.WHITE, body, 2)
        pygame.draw.circle(surf, C.WHITE, (cx, cy - 2), 3)
        if thrust:
            flame = [(cx - 5, cy + h // 2), (cx + 5, cy + h // 2),
                     (cx, cy + h + random.randint(4, 12))]
            pygame.draw.polygon(surf, C.ORANGE, flame)


class Bullet:
    def __init__(self, x, y, speed, damage=1):
        self.x = float(x)
        self.y = float(y)
        self.speed = float(speed)
        self.damage = damage
        # enemies already hit: a bullet that stays several frames inside
        # the same enemy deals its damage to it only once
        self.hit_enemies = set()

    @property
    def rect(self):
        return pygame.Rect(int(self.x - C.BULLET_W / 2), int(self.y),
                           C.BULLET_W, C.BULLET_H)

    def update(self):
        self.y -= self.speed

    @property
    def dead(self):
        return self.y < -C.BULLET_H

    def draw(self, surf, sprite=None):
        power = getattr(self, "charged_power", 1)  # 1..5 for charged shots
        image = assets.load(sprite, (C.BULLET_W * 3, C.BULLET_H))
        if image is not None:
            assets.blit_centered(surf, image, self.x, self.y + C.BULLET_H / 2)
            return
        # Charged shot: bigger + brighter halo. Regular shot: standard.
        if power > 1:
            # halo glow (bigger with more power)
            halo_r = int(6 + power * 4)
            halo_color = (255, 220, 80) if power >= 4 else (255, 180, 60)
            halo = pygame.Surface((halo_r * 2, halo_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(halo, (*halo_color, 100), (halo_r, halo_r), halo_r)
            surf.blit(halo, (int(self.x - halo_r), int(self.y - halo_r + C.BULLET_H // 2)))
            # bigger core rectangle
            w = C.BULLET_W + power * 2
            h = C.BULLET_H + power
            rect = pygame.Rect(int(self.x - w // 2), int(self.y), w, h)
            pygame.draw.rect(surf, halo_color, rect)
            pygame.draw.rect(surf, C.WHITE, (rect.x, rect.y, w, 4))
        else:
            pygame.draw.rect(surf, C.AMBER, self.rect)
            pygame.draw.rect(surf, C.WHITE,
                             (self.rect.x, self.rect.y, C.BULLET_W, 4))


class Asteroid:
    """Internal enemy, used when student_config.py defines no enemy class."""

    def __init__(self, x, y, speed, radius=None):
        self.x = float(x)
        self.y = float(y)
        self.speed = float(speed)
        self.hp = 1
        self.radius = radius or random.randint(C.ASTEROID_MIN, C.ASTEROID_MAX)
        self.spin = random.uniform(-3, 3)
        self.angle = random.uniform(0, 360)
        self.shape = [random.uniform(0.72, 1.0) for _ in range(9)]

    @property
    def rect(self):
        r = self.radius
        return pygame.Rect(int(self.x - r), int(self.y - r), r * 2, r * 2)

    def move(self):
        self.y += self.speed
        self.angle += self.spin

    def update(self):
        self.move()

    @property
    def dead(self):
        return self.y - self.radius > C.HEIGHT

    def draw(self, surf, sprite=None):
        d = self.radius * 2
        image = assets.load(sprite, (d, d))
        if image is not None:
            assets.blit_centered(surf, image, self.x, self.y, self.angle)
            return
        pts = []
        for i, k in enumerate(self.shape):
            a = math.radians(self.angle + i * (360 / len(self.shape)))
            r = self.radius * k
            pts.append((self.x + math.cos(a) * r, self.y + math.sin(a) * r))
        pygame.draw.polygon(surf, (86, 96, 116), pts)
        pygame.draw.polygon(surf, (140, 152, 174), pts, 2)


class StudentEnemy:
    """Wrapper around an enemy class written by the student.

    The engine does not know the exact type: it calls move() and reads
    x / y.
    """

    def __init__(self, instance, fallback_speed=2.0):
        self.obj = instance
        self.fallback_speed = fallback_speed
        self.radius = 20
        self.broken = False

    @property
    def x(self):
        value = getattr(self.obj, "x", C.WIDTH // 2)
        return value if isinstance(value, (int, float)) else C.WIDTH // 2

    @property
    def y(self):
        value = getattr(self.obj, "y", 0)
        return value if isinstance(value, (int, float)) else 0

    @property
    def hp(self):
        value = getattr(self.obj, "hp", 1)
        return value if isinstance(value, (int, float)) else 1

    @hp.setter
    def hp(self, value):
        try:
            self.obj.hp = value
        except Exception:  # noqa: BLE001
            pass

    @property
    def rect(self):
        r = self.radius
        return pygame.Rect(int(self.x - r), int(self.y - r), r * 2, r * 2)

    def move(self):
        """Calls the student's move(), with a safety net."""
        mover = getattr(self.obj, "move", None)
        if callable(mover) and not self.broken:
            try:
                mover()
                return
            except Exception:  # noqa: BLE001
                self.broken = True   # no more retries: degraded mode
        try:
            self.obj.y = self.y + self.fallback_speed
        except Exception:  # noqa: BLE001
            pass

    def update(self):
        self.move()

    @property
    def dead(self):
        return self.y - self.radius > C.HEIGHT

    def draw(self, surf, sprite=None):
        cx, cy = int(self.x), int(self.y)
        # a sprite can be declared on the class itself:
        #     class Kamikaze(Enemy):
        #         sprite = "images/kamikaze.png"
        own = getattr(self.obj, "sprite", None)
        d = self.radius * 2
        image = assets.load(own, (d, d)) or assets.load(sprite, (d, d))
        if image is not None:
            assets.blit_centered(surf, image, cx, cy)
            return
        name = type(self.obj).__name__
        # one tint per type, so each enemy type stands out
        tint = C.COLOR_NAMES[list(C.COLOR_NAMES)[hash(name) % len(C.COLOR_NAMES)]]
        pygame.draw.circle(surf, tint, (cx, cy), self.radius)
        pygame.draw.circle(surf, C.WHITE, (cx, cy), self.radius, 2)
        pygame.draw.circle(surf, C.DARK, (cx, cy), max(3, self.radius // 3))


class PowerUp:
    def __init__(self, x, y, color_name, effect, duration):
        self.x = float(x)
        self.y = float(y)
        self.color_name = color_name
        self.effect = effect
        self.duration = duration
        self.speed = 2.0
        self.t = 0

    @property
    def rect(self):
        s = C.POWERUP_SIZE
        return pygame.Rect(int(self.x - s / 2), int(self.y - s / 2), s, s)

    def update(self):
        self.y += self.speed
        self.t += 1

    @property
    def dead(self):
        return self.y - C.POWERUP_SIZE > C.HEIGHT

    def draw(self, surf, sprite=None):
        s_ = C.POWERUP_SIZE
        image = assets.load(sprite, (s_ + 4, s_ + 4))
        if image is not None:
            assets.blit_centered(surf, image, self.x, self.y)
            return
        col = C.COLOR_NAMES.get(str(self.color_name).lower(), C.WHITE)
        s = C.POWERUP_SIZE
        pulse = 2 + int(2 * math.sin(self.t * 0.15))
        rect = pygame.Rect(int(self.x - s / 2), int(self.y - s / 2), s, s)
        pygame.draw.rect(surf, col, rect, border_radius=4)
        pygame.draw.rect(surf, C.WHITE, rect.inflate(pulse, pulse), 2,
                         border_radius=5)
