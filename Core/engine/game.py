"""
game.py — Logique du jeu : vagues, tirs, collisions, score, états.
VERROUILLÉ : ne pas modifier.
"""

import random

import pygame

from engine import assets
from engine import config as C
from engine import hud
from engine.entities import Asteroid, Bullet, PowerUp, Ship, StudentEnemy
from engine.loader import StudentFeatures


PLAYING, PAUSED, GAMEOVER, COUNTDOWN = "playing", "paused", "gameover", "countdown"


class Game:
    def __init__(self, screen, fonts):
        self.screen = screen
        self.fonts = fonts
        self.features = StudentFeatures().load()
        self.current_chapter = self._load_chapter()
        self.reset()

    # ------------------------------------------------------------------
    def _load_chapter(self):
        """Lit Core/chapter.py (géré par l'enseignant). Défaut : 1."""
        try:
            import importlib, sys
            if "chapter" in sys.modules:
                mod = importlib.reload(sys.modules["chapter"])
            else:
                mod = importlib.import_module("chapter")
            value = getattr(mod, "CURRENT_CHAPTER", 1)
            return int(value) if isinstance(value, int) else 1
        except Exception:  # noqa: BLE001
            return 1

    def _hover_zones(self):
        """Rectangles survolables en pause.

        Règle du contrat (chapitre 2) : une zone n'est survolable que si
        une instance de son élément est présente à l'écran. ship et hud
        sont toujours là ; asteroid n'existe que s'il y a un astéroïde ;
        bonus n'existe que si un bonus est tombé.
        """
        ship = pygame.Rect(int(self.ship.x - 60), int(self.ship.y - 50), 120, 100)
        ship = ship.clip(pygame.Rect(0, 36, C.WIDTH, C.HEIGHT))
        zones = {
            "hud": pygame.Rect(0, 0, C.WIDTH, 34),
            "ship": ship,
            "field": pygame.Rect(0, 40, C.WIDTH, C.HEIGHT - 200),
        }
        # astéroïde : la zone entoure le premier astéroïde présent
        if self.enemies:
            e = self.enemies[0]
            r = getattr(e, "radius", 24)
            zones["asteroid"] = pygame.Rect(int(e.x - r - 10), int(e.y - r - 10),
                                            int(r * 2 + 20), int(r * 2 + 20))
        # bonus : la zone entoure le premier bonus tombé
        if self.powerups:
            p = self.powerups[0]
            zones["bonus"] = pygame.Rect(int(p.x - 24), int(p.y - 24), 48, 48)
        return zones

    # ------------------------------------------------------------------
    def reset(self):
        f = self.features
        sx, sy = self._start_position()
        self.ship = Ship(sx, sy)
        self.ship.lives = max(1, int(f.starting_lives))
        self.ship.ammo = int(f.nb_ammo)
        self.max_ammo = int(f.nb_ammo)

        self.bullets = []
        self.enemies = []
        self.powerups = []
        self.particles = []

        self.score = 0
        self.combo = 1
        self.wave = 0
        self.wave_timer = 30

        # --- Chapitre 2 : score, combo, bonus ---
        self.combo_timer = 0            # frames depuis le dernier tir tiré
        self.bonus_next = None          # prochain palier de score (bonus)
        self.bonus_mult = 1.0           # multiplicateur de bonus actif
        self.bonus_active_frames = 0    # frames restantes du bonus actif
        self.hud_highlight = False      # HUD en mode mise en avant
        self.low_ammo_alert = False     # alerte munitions basses

        self.fire_cd = 0
        self.reloading = 0
        self.shield = 0
        self.rapid = 0

        self.weapon_name = self._pick_weapon()
        self.highscores = []

        countdown = int(f.start_countdown)
        if countdown > 0:
            self.state = COUNTDOWN
            self.countdown_frames = countdown * C.FPS
        else:
            self.state = PLAYING
            self.countdown_frames = 0

        self.hud_line = ""
        self.game_over_line = ""

    def _start_position(self):
        pos = self.features.start_position
        try:
            x, y = pos
            if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                return float(x), float(y)
        except (TypeError, ValueError):
            pass
        return C.DEFAULT_START

    def _pick_weapon(self):
        weapons = self.features.weapons
        unlocked = self.features.unlocked_weapons
        for name in weapons:
            if not unlocked or name in unlocked:
                return name
        return next(iter(weapons))

    @property
    def weapon(self):
        return self.features.weapons.get(self.weapon_name)

    # ------------------------------------------------------------------
    #  Boucle
    # ------------------------------------------------------------------
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.state == PAUSED:
                    self.state = PLAYING
                elif self.state in (PLAYING, COUNTDOWN):
                    self.state = PAUSED
                else:
                    return False
            elif event.key == pygame.K_r and self.state == GAMEOVER:
                self.features = StudentFeatures().load()
                self.reset()
            elif event.key == pygame.K_TAB and self.state == PLAYING:
                self._cycle_weapon()
        return True

    def _cycle_weapon(self):
        names = list(self.features.weapons)
        if len(names) < 2:
            return
        i = names.index(self.weapon_name)
        self.weapon_name = names[(i + 1) % len(names)]

    def update(self):
        if self.state == COUNTDOWN:
            self.countdown_frames -= 1
            if self.countdown_frames <= -C.FPS // 2:
                self.state = PLAYING
            return
        if self.state != PLAYING:
            return

        f = self.features
        keys = pygame.key.get_pressed()

        self._update_ship(keys, f)
        self._update_firing(keys, f)
        self._update_bullets()
        self._update_enemies(f)
        self._update_powerups()
        self._collisions(f)
        self._spawn_logic(f)
        self._timers()
        self._timers_ch2(f)
        self._student_hook()

        self.hud_line = f.hud(f.player_name, self.score, self.ship.ammo)

    # ------------------------------------------------------------------
    def _update_ship(self, keys, f):
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_q] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        self.ship.move(dx, float(f.ship_speed))
        self.thrust = dx != 0
        if self.ship.invuln > 0:
            self.ship.invuln -= 1

    def _update_firing(self, keys, f):
        held = keys[pygame.K_SPACE]
        if self.fire_cd > 0:
            self.fire_cd -= 1

        w = self.weapon
        wobj = w.get("object") if w else None
        # Une arme objet (séance 12) gère son propre temps : on la fait
        # avancer sans jamais toucher à son état interne.
        if wobj is not None:
            try:
                if callable(getattr(wobj, "tick", None)):
                    wobj.tick()
            except Exception:  # noqa: BLE001
                pass

        if self.reloading > 0:
            self.reloading -= 1
            if self.reloading == 0:
                self.ship.ammo = self.max_ammo
            return

        if not held:
            return
        if not f.keep_firing(self.ship.ammo, held):
            return
        if self.ship.ammo <= 0:
            if int(f.reload_time) > 0 and self.max_ammo > 0:
                self.reloading = int(f.reload_time)
            return

        # cooldown : géré par l'objet arme s'il existe, sinon par le moteur
        if wobj is not None:
            fired = 0
            try:
                if callable(getattr(wobj, "can_fire", None)) and not wobj.can_fire():
                    return
                if callable(getattr(wobj, "fire", None)):
                    fired = wobj.fire() or 0
            except Exception:  # noqa: BLE001
                fired = 0
            if not fired:
                return
            dmg = f.compute_damage(int(fired), 2.0 if self.rapid else 1.0)
        else:
            if self.fire_cd > 0:
                return
            cd = int(w.get("cooldown", 12)) if w else 12
            self.fire_cd = max(1, cd // (2 if self.rapid else 1))
            base = int(w.get("damage", 1)) if w else 1
            dmg = f.compute_damage(base, 2.0 if self.rapid else 1.0)

        self.ship.ammo -= 1
        speed = float(f.bullet_speed) or 8.0
        spread = 3 if (w and "spread" in str(w.get("name", "")).lower()) else 1
        for i in range(spread):
            offset = (i - (spread - 1) / 2) * 14
            self.bullets.append(
                Bullet(self.ship.x + offset, self.ship.y - C.SHIP_H / 2,
                       speed, dmg))

    def _update_bullets(self):
        for b in self.bullets:
            b.update()
        # un tir qui sort par le haut sans avoir touché = tir raté -> reset combo
        missed = [b for b in self.bullets if b.dead]
        if missed and self.combo > 1:
            self.combo = 1
            self.combo_timer = 0
        self.bullets = [b for b in self.bullets if not b.dead]

    def _update_enemies(self, f):
        for e in self.enemies:
            e.update()
        self.enemies = [e for e in self.enemies if not e.dead]

    def _update_powerups(self):
        for p in self.powerups:
            p.update()
        self.powerups = [p for p in self.powerups if not p.dead]

    # ------------------------------------------------------------------
    def _collisions(self, f):
        # tirs contre ennemis
        for b in list(self.bullets):
            for e in list(self.enemies):
                if b.rect.colliderect(e.rect):
                    if b in self.bullets:
                        self.bullets.remove(b)
                    e.hp = e.hp - b.damage
                    if e.hp <= 0:
                        self._destroy(e, f)
                    break

        # vaisseau contre ennemis
        if self.ship.invuln <= 0:
            for e in list(self.enemies):
                if self.ship.rect.colliderect(e.rect):
                    self.enemies.remove(e)
                    if self.shield > 0:
                        self.shield = 0
                    else:
                        self._hurt(f)
                    break

        # vaisseau contre bonus
        for p in list(self.powerups):
            if self.ship.rect.colliderect(p.rect):
                self.powerups.remove(p)
                self._apply_powerup(p, f)

        # tir allié : les tirs peuvent aussi toucher le vaisseau en retombant
        if f.friendly_fire:
            for b in list(self.bullets):
                if b.y > C.HEIGHT - 8 and b.rect.colliderect(self.ship.rect):
                    self.bullets.remove(b)

    def _points_per_hit(self, f):
        """Points par astéroïde. Si l'étudiant a défini points_per_hit,
        on l'utilise ; sinon on le calcule (base_hit_points * bonus_points)
        comme le fait le fil rouge. Défaut neutre = 0."""
        if f.unlocked.get("points_per_hit") and f.points_per_hit:
            return float(f.points_per_hit)
        return float(f.base_hit_points) * float(f.bonus_points)

    def _destroy(self, enemy, f):
        if enemy in self.enemies:
            self.enemies.remove(enemy)

        # score = points par tir × multiplicateur de combo (si enchaînement)
        #         × multiplicateur de bonus actif
        base = self._points_per_hit(f)
        combo_factor = self.combo * float(f.combo_multiplier) if self.combo > 1 else 1
        gain = base * combo_factor * self.bonus_mult
        self.score += max(0, int(round(gain)))

        # un tir réussi prolonge l'enchaînement
        self.combo += 1
        self.combo_timer = 0

        # bonus récurrent (modèle A) : un bonus tombe à chaque palier franchi
        self._check_bonus_threshold(f, enemy.x, enemy.y)

        for _ in range(8):
            self.particles.append([enemy.x, enemy.y,
                                   random.uniform(-3, 3),
                                   random.uniform(-3, 3), 20])

    def _check_bonus_threshold(self, f, x, y):
        """Modèle A : bonus à chaque multiple de bonus_threshold, palier
        réarmé ensuite."""
        thr = float(f.bonus_threshold)
        if thr <= 0 or thr >= 10 ** 9:
            return
        if self.bonus_next is None:
            self.bonus_next = thr
        # peut franchir plusieurs paliers d'un coup sur un gros gain
        dropped = False
        while self.score >= self.bonus_next:
            self.bonus_next += thr
            dropped = True
        if dropped:
            self._spawn_bonus(x, y, f)

    def _spawn_bonus(self, x, y, f):
        """Fait tomber un bonus (power-up chapitre 2)."""
        pu = PowerUp(x, y, "gold", "score_bonus", float(f.bonus_duration))
        self.powerups.append(pu)

    def _hurt(self, f):
        self.ship.lives -= 1
        self.combo = 1               # le vaisseau touché casse le combo
        self.combo_timer = 0
        self.ship.invuln = C.INVULN_FRAMES
        if self.ship.lives <= 0:
            self._end_game(f)

    def _end_game(self, f):
        self.state = GAMEOVER
        self.game_over_line = f.game_over(f.player_name, self.score)
        f.save_score(f.player_name, self.score)
        self.highscores = f.load_scores()

    def _spawn_powerup(self, x, y, f):
        colors = list(f.powerup_colors)
        student_pu = f.powerups
        if not colors and not student_pu:
            return
        if random.random() > 0.16:
            return
        if student_pu:
            p = random.choice(student_pu)
            self.powerups.append(
                PowerUp(x, y, p["color"], p["effect"], p["duration"]))
        else:
            self.powerups.append(
                PowerUp(x, y, random.choice(colors), "heal", 0))

    def _apply_powerup(self, p, f=None):
        effect = str(p.effect).lower()
        frames = int(float(p.duration or 0) * C.FPS)
        if effect == "score_bonus":
            # Chapitre 2 : active le multiplicateur de bonus pour sa durée.
            mult = float(f.bonus_points) if f else 1.0
            self.bonus_mult = mult if mult > 0 else 1.0
            self.bonus_active_frames = max(frames, 1)
        elif effect == "shield":
            self.shield = max(frames, C.FPS * 3)
        elif effect in ("rapid_fire", "rapid"):
            self.rapid = max(frames, C.FPS * 3)
        else:  # heal et tout effet inconnu
            self.ship.lives += 1
        if self.max_ammo and effect != "score_bonus":
            self.ship.ammo = min(self.max_ammo, self.ship.ammo + 5)

    # ------------------------------------------------------------------
    def _spawn_logic(self, f):
        if self.wave_timer > 0:
            self.wave_timer -= 1
            return
        if self.enemies:
            return

        self.wave += 1
        count, speed = f.wave_pattern(self.wave)
        count = max(1, min(24, count))

        level = f.difficulty(self.score)
        factor = {"easy": 1.0, "normal": 1.35, "hard": 1.8}.get(str(level).lower(), 1.0)
        # mode difficile (chapitre 2) : is_hard accélère le jeu
        hard_factor = 1.4 if f.is_hard else 1.0
        speed = max(0.5, speed * factor * hard_factor * float(f.global_difficulty))

        positions = f.row_positions(count)
        types = f.enemy_types

        for i in range(count):
            x = positions[i % len(positions)]
            x = max(20, min(C.WIDTH - 20, float(x)))
            y = -30 - (i // max(1, len(positions))) * 60
            if types:
                cls = types[i % len(types)]
                try:
                    inst = cls(x, y)
                except Exception:  # noqa: BLE001
                    self.enemies.append(Asteroid(x, y, speed))
                    continue
                self.enemies.append(StudentEnemy(inst, speed))
            else:
                self.enemies.append(Asteroid(x, y, speed))

        self.wave_timer = C.BASE_WAVE_DELAY

    def debug_value(self, key):
        """Valeur courante d'une grandeur pour l'overlay debug."""
        if key == "score":
            return self.score
        if key == "ammo":
            return self.ship.ammo
        if key == "lives":
            return self.ship.lives
        if key == "points_per_hit":
            return int(self._points_per_hit(self.features))
        if key == "combo":
            return f"x{self.combo}" if self.combo > 1 else "-"
        if key == "bonus_mult":
            return f"x{self.bonus_mult:g}" if self.bonus_mult > 1 else "-"
        return "?"

    def _timers(self):
        if self.shield > 0:
            self.shield -= 1
        if self.rapid > 0:
            self.rapid -= 1
        for p in self.particles:
            p[0] += p[2]
            p[1] += p[3]
            p[4] -= 1
        self.particles = [p for p in self.particles if p[4] > 0]

    def _timers_ch2(self, f):
        """Chapitre 2 : combo delay, bonus actif, HUD highlight, alerte."""
        # délai de combo : reset après combo_reset_delay secondes sans tir
        delay = float(f.combo_reset_delay)
        if delay > 0 and self.combo > 1:
            self.combo_timer += 1
            if self.combo_timer >= delay * C.FPS:
                self.combo = 1
                self.combo_timer = 0
        # bonus actif : décompte puis retour au multiplicateur 1
        if self.bonus_active_frames > 0:
            self.bonus_active_frames -= 1
            if self.bonus_active_frames == 0:
                self.bonus_mult = 1.0
        # HUD de mise en avant : score au-delà du seuil
        hl = float(f.highlight_score)
        self.hud_highlight = (hl < 10 ** 9) and (self.score >= hl)
        # alerte munitions basses
        lat = float(f.low_ammo_threshold)
        self.low_ammo_alert = (lat >= 0) and (self.ship.ammo <= lat)

    def _student_hook(self):
        """Point d'extension libre de la séance 15."""
        if not self.features.has_student_update:
            return
        state = {
            "score": self.score,
            "wave": self.wave,
            "lives": self.ship.lives,
            "ammo": self.ship.ammo,
            "ship_x": self.ship.x,
            "ship_y": self.ship.y,
            "enemies": len(self.enemies),
        }
        try:
            self.features.cfg.student_update(state)
        except Exception:  # noqa: BLE001
            pass

    # ------------------------------------------------------------------
    #  Rendu
    # ------------------------------------------------------------------
    def draw(self):
        s = self.screen
        f = self.features
        bg = assets.load(f.background_image, (C.WIDTH, C.HEIGHT))
        if bg is not None:
            s.blit(bg, (0, 0))
        else:
            s.fill(C.BLACK)
            self._draw_starfield(s)

        for e in self.enemies:
            # un astéroïde interne prend asteroid_sprite (ch2) ; un ennemi
            # de l'étudiant (classe) prend enemy_sprite (ch5).
            spr = f.asteroid_sprite if isinstance(e, Asteroid) else f.enemy_sprite
            e.draw(s, spr)
        for p in self.powerups:
            # un bonus de score (ch2) prend bonus_sprite ; les autres
            # power-ups prennent powerup_sprite (ch8).
            spr = f.bonus_sprite if str(p.effect).lower() == "score_bonus" else f.powerup_sprite
            p.draw(s, spr)
        for b in self.bullets:
            b.draw(s, f.bullet_sprite)
        for px, py, _, _, life in self.particles:
            pygame.draw.circle(s, C.ORANGE, (int(px), int(py)),
                               max(1, life // 6))

        if self.state != GAMEOVER:
            self.ship.draw(s, getattr(self, "thrust", False), f.ship_sprite)
            if self.shield > 0:
                pygame.draw.circle(s, C.BLUE,
                                   (int(self.ship.x), int(self.ship.y)),
                                   C.SHIP_W, 2)

        hud.draw_hud(s, self.fonts, self)

        # overlay debug (chapitre 2) : si show_debug est activé
        if self.features.show_debug and self.state == PLAYING:
            hud.draw_debug_overlay(s, self.fonts, self, self.current_chapter)

        if self.reloading > 0:
            ratio = 1 - self.reloading / max(1, int(self.features.reload_time))
            hud.draw_reloading(s, self.fonts, ratio)

        if self.state == COUNTDOWN:
            hud.draw_countdown(s, self.fonts,
                               (self.countdown_frames + C.FPS - 1) // C.FPS)

        if self.features.has_student_draw:
            try:
                self.features.cfg.student_draw(s, {"score": self.score,
                                                   "wave": self.wave})
            except Exception:  # noqa: BLE001
                pass

        if self.state == GAMEOVER:
            hud.draw_game_over(s, self.fonts, self)
        elif self.state == PAUSED:
            hud.draw_pause(s, self.fonts, self.features,
                           self.current_chapter, self._hover_zones(),
                           pygame.mouse.get_pos())

        if self.state == PLAYING and self.wave == 0:
            hud.text(s, self.fonts.small,
                     "Échap : carte des notions    ←/→ : bouger    Espace : tirer",
                     C.WIDTH // 2, C.HEIGHT - 26, C.GREY, center=True)

    def _draw_starfield(self, s):
        if not hasattr(self, "_stars"):
            self._stars = [[random.randint(0, C.WIDTH),
                            random.randint(0, C.HEIGHT),
                            random.uniform(0.3, 1.4)] for _ in range(70)]
        for st in self._stars:
            st[1] += st[2]
            if st[1] > C.HEIGHT:
                st[0] = random.randint(0, C.WIDTH)
                st[1] = -2
            shade = int(90 + st[2] * 90)
            s.set_at((int(st[0]), int(st[1]) % C.HEIGHT),
                     (shade, shade, min(255, shade + 30)))
