"""
game.py - Game logic: waves, shots, collisions, score, states.
LOCKED: do not modify.
"""

import random

import pygame

from engine import assets
from engine import config as C
from engine import hud
from engine.entities import Asteroid, Bullet, PowerUp, Ship, StudentEnemy
from engine.i18n import t
from engine.loader import StudentFeatures


PLAYING, PAUSED, GAMEOVER, COUNTDOWN = "playing", "paused", "gameover", "countdown"
# FROZEN: raw ending when student_rules.py sets no game_over output.
# The ship explodes and the game freezes in place: it does not close
# (the game never crashes), but there is no end screen.
# The game_over rule output turns this freeze into a proper
# game-over screen (score, replay).
FROZEN = "frozen"

# Chapter 4 — pace of the slow-motion loops (engine side, not student side)
COUNTDOWN_HOLD = C.FPS // 2     # frames a new countdown value stays on screen
COUNTDOWN_MAX_HOLDS = 20        # beyond this, the countdown runs at frame pace
BURST_STEP_FRAMES = 8           # frames between two turns of the burst loop
LOOP_MSG_FRAMES = C.FPS * 8     # how long a student_loops.py error stays on screen


class Game:
    def __init__(self, screen, fonts):
        self.screen = screen
        self.fonts = fonts
        self.features = StudentFeatures().load()
        self.current_chapter = self._load_chapter()
        # Chapter 3+: the live file student_rules.py (conditions).
        self.rules = None
        if self.current_chapter >= 3:
            from engine.rules import RulesEngine
            import os
            root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self.rules = RulesEngine(os.path.join(root, "student_rules.py"))
        self.rule_outputs = {}
        # Chapter 4+: the live file student_loops.py (loops).
        self.slow_loops = None
        if self.current_chapter >= 4:
            from engine.loops import SlowLoopEngine
            import os
            root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self.slow_loops = SlowLoopEngine(os.path.join(root, "student_loops.py"))
        # Chapter 4 state: charge shot and burst fire tracking
        self.charge = 0
        self.charging = False
        self.burst_remaining = 0
        self.last_charge = 0        # charge reached by the last charged shot
        self.last_fired = 0         # value of fired at the end of the last burst
        self.loop_turns = 0         # turns done by the loop currently / last run
        self.loop_msg = None        # (text, frames, footer) red error banner
        self.repair_active = False
        self.reset()
        self._show_config_problems()

    # ------------------------------------------------------------------
    def _load_chapter(self):
        """Reads Core/chapter.py (managed by the instructor). Default: 1."""
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
        """Hoverable rectangles in pause.

        A zone can be hovered only if an instance of its element is on
        screen. ship and hud are always there; asteroid exists only if
        an asteroid is present; bonus only if a bonus has dropped.
        """
        ship = pygame.Rect(int(self.ship.x - 60), int(self.ship.y - 50), 120, 100)
        ship = ship.clip(pygame.Rect(0, 36, C.WIDTH, C.HEIGHT))
        zones = {
            "hud": pygame.Rect(0, 0, C.WIDTH, 34),
            "ship": ship,
            "field": pygame.Rect(0, 40, C.WIDTH, C.HEIGHT - 200),
        }
        # asteroid: the zone surrounds the first asteroid present
        if self.enemies:
            e = self.enemies[0]
            r = getattr(e, "radius", 24)
            zones["asteroid"] = pygame.Rect(int(e.x - r - 10), int(e.y - r - 10),
                                            int(r * 2 + 20), int(r * 2 + 20))
        # bonus: the zone surrounds the first dropped bonus
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

        # --- Chapter 2: score, combo, bonus ---
        self.combo_timer = 0            # frames since the last shot
        self.bonus_next = None          # next score threshold (bonus)
        self.bonus_mult = 1.0           # active bonus multiplier
        self.bonus_active_frames = 0    # frames left for the active bonus
        self.hud_highlight = False      # HUD en mode mise en avant
        self.low_ammo_alert = False     # low ammo alert

        self.fire_cd = 0
        self.reloading = 0
        self.shield_level = 0           # shield level 0..3 (chapter 3)
        self.rapid = 0

        self.weapon_name = self._pick_weapon()
        self.highscores = []

        # Chapter 4: if the student defines a "countdown" event, use it
        # (their while loop controls the countdown). Otherwise engine default.
        self.countdown_value = 3   # visible value shown to player
        self.countdown_hold = 0    # frames left showing the current value
        self.countdown_changes = 0 # number of value changes already held
        self.countdown_done = False
        countdown = int(f.start_countdown)
        self._check_loops_syntax()
        if self.slow_loops and self._start_loop("countdown", {"countdown": 3}):
            self.state = COUNTDOWN
            self.countdown_frames = 999  # student loop controls duration
            self.countdown_student = True
            self.countdown_value = self.slow_loops.namespace.get("countdown", 3)
            self.countdown_hold = COUNTDOWN_HOLD
        elif countdown > 0:
            self.state = COUNTDOWN
            self.countdown_frames = countdown * C.FPS
            self.countdown_student = False
        else:
            self.state = PLAYING
            self.countdown_student = False
            self.countdown_frames = 0

        # filled at once: the top bar shows the name from the first frame,
        # countdown included
        self.hud_line = f.hud(f.player_name, self.score, self.ship.ammo)
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
                    # back to the state paused from: a countdown in
                    # progress goes on where it stopped
                    self.state = getattr(self, "resume_state", PLAYING)
                elif self.state in (PLAYING, COUNTDOWN):
                    self.resume_state = self.state
                    self.state = PAUSED
                else:
                    return False
            elif self.state == PAUSED:
                self._handle_copy_key(event)
            elif event.key == pygame.K_r and self.state in (GAMEOVER, FROZEN):
                self.features = StudentFeatures().load()
                self.reset()
                self._show_config_problems()
            elif event.key == pygame.K_TAB and self.state == PLAYING:
                self._cycle_weapon()
            elif event.key == pygame.K_b and self.state == PLAYING:
                # Chapter 4: burst fire (student's for loop drives count)
                if self.burst_remaining == 0 and not self.charging:
                    self._fire_burst(self.features)
        return True

    def _handle_copy_key(self, event):
        """In pause: C copies the variable if the tooltip shows only one,
        1..9 copy the n-th variable listed in the tooltip."""
        names = getattr(self, "_paused_copyable", None) or []
        if not names:
            return
        idx = None
        if event.key == pygame.K_c and len(names) == 1:
            idx = 0
        elif pygame.K_1 <= event.key <= pygame.K_9:
            idx = event.key - pygame.K_1
        if idx is None or idx >= len(names):
            return
        from engine.clipboard import copy_text
        name = names[idx]
        if copy_text(name):
            self.features._copied_flash = (name, C.FPS)

    def _cycle_weapon(self):
        names = list(self.features.weapons)
        if len(names) < 2:
            return
        i = names.index(self.weapon_name)
        self.weapon_name = names[(i + 1) % len(names)]

    def update(self):
        if self.state == COUNTDOWN:
            if self.countdown_student and self.slow_loops:
                # Student's while loop drives the countdown. Pace: one
                # turn per frame, but each time the displayed value
                # changes the engine holds it COUNTDOWN_HOLD frames so it
                # can be read. Only the first COUNTDOWN_MAX_HOLDS changes
                # are held: a loop that never ends (counter going up, for
                # instance) then runs at frame pace and reaches the
                # 1000-turn safety net in seconds, not minutes.
                if self.countdown_hold > 0:
                    self.countdown_hold -= 1
                    return
                if self.countdown_done:
                    self.state = PLAYING
                    return
                running, ns = self.slow_loops.step_event("countdown")
                self.loop_turns = self.slow_loops.iterations("countdown")
                value = ns.get("countdown", 0)
                if value != self.countdown_value:
                    self.countdown_value = value
                    if self.countdown_changes < COUNTDOWN_MAX_HOLDS:
                        self.countdown_changes += 1
                        self.countdown_hold = COUNTDOWN_HOLD
                if not running:
                    if self._report_loop_error("countdown"):
                        self.state = PLAYING
                        return
                    self.countdown_done = True
                    self.countdown_hold = COUNTDOWN_HOLD
            else:
                self.countdown_frames -= 1
                if self.countdown_frames <= -C.FPS // 2:
                    self.state = PLAYING
            return
        if self.state == FROZEN:
            # Raw ending: the game is frozen. Let the explosion animate
            # and keep evaluating the rules: once game_over is set,
            # the game switches to the proper game-over screen.
            self._update_particles()
            if self.rules is not None:
                self._eval_rules(self.features)
            return
        if self.state != PLAYING:
            return

        f = self.features
        keys = pygame.key.get_pressed()

        self._update_ship(keys, f)
        self._update_firing(keys, f)
        if self.burst_remaining != 0:
            self._step_burst(f)
        self._update_bullets()
        self._update_enemies(f)
        self._update_powerups()
        self._collisions(f)
        self._spawn_logic(f)
        self._timers()
        self._timers_ch2(f)
        self._eval_rules(f)
        self._student_hook()

        self.hud_line = f.hud(f.player_name, self.score, self.ship.ammo)

    def _update_particles(self):
        for p in self.particles:
            p[0] += p[2]
            p[1] += p[3]
            p[4] -= 1
        self.particles = [p for p in self.particles if p[4] > 0]

    def _eval_rules(self, f):
        """Chapter 3: executes student_rules.py with the current state
        injected, then applies the outputs set by the student."""
        if self.rules is None:
            return
        # active_bonus: None when no golden bonus is active, otherwise
        # the current multiplier (e.g. 2). Returns to None at the end of
        # the effect.
        active_bonus = int(self.bonus_mult) if self.bonus_active_frames > 0 else None
        state = {
            "lives": self.ship.lives,
            "ammo": self.ship.ammo,
            "score": self.score,
            "combo": self.combo,
            "active_bonus": active_bonus,
            "player_name": f.player_name,
            "shield": self.shield_level,
        }
        out = self.rules.evaluate(state)
        self.rule_outputs = out
        # apply outputs (the engine always keeps its safety checks)
        if out.get("hud_danger"):
            self.hud_highlight = True  # reuses the amber HUD of chapter 2
        if out.get("show_empty_alert"):
            self.low_ammo_alert = True
        # Rule-driven game over: if the rule sets game_over at 0 lives,
        # the raw ending (freeze) becomes a proper game-over screen.
        # Without this rule, the game stays frozen.
        if out.get("game_over") and self.ship.lives <= 0:
            self._end_game(f)

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

        # --- Chapter 4: charged shot (student's while loop drives charge) ---
        # Space is held: charge builds up frame by frame via student's while.
        # Space released: shot fires with charge-proportional power.
        if self.slow_loops and "charging" in self.slow_loops.loops:
            if held and not self.charging and self.ship.ammo > 0:
                # start charging
                self.charging = True
                self.charge = 0
                if not self._start_loop("charging", {
                        "charge": 0, "charge_rate": 3, "max_charge": 100}):
                    self.charging = False
            if self.charging:
                if held:
                    # step the student's while loop once per frame (visible pace)
                    running, ns = self.slow_loops.step_event("charging")
                    self.loop_turns = self.slow_loops.iterations("charging")
                    self.charge = self._as_number(ns.get("charge", 0))
                    if not running:
                        self._report_loop_error("charging")
                        # charge reached max or student's break triggered
                        pass  # keep charging state, wait for release
                    return  # don't fire while holding — wait for release
                else:
                    # Space released: fire the charged shot
                    self.slow_loops.stop_event("charging")
                    self.charging = False
                    self.last_charge = self.charge
                    self._fire_charged(f)
                    self.charge = 0
                    return

        w = self.weapon
        wobj = w.get("object") if w else None
        # A weapon object manages its own timing: the engine advances it
        # without ever touching its internal state.
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

        # Auto-reload as soon as the magazine is empty, whether firing
        # or not: prevents getting stuck at 0 ammo. If the student has
        # defined reload_time, their value takes priority; otherwise fallback delay.
        if self.ship.ammo <= 0 and self.max_ammo > 0:
            delay = int(f.reload_time) if int(f.reload_time) > 0 else C.RELOAD_FALLBACK
            self.reloading = delay
            return

        if not held:
            return
        if not f.keep_firing(self.ship.ammo, held):
            return
        if self.ship.ammo <= 0:
            return

        # cooldown: managed by the weapon object if it exists, otherwise by the engine
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

    def _fire_charged(self, f):
        """Chapter 4: fires a shot whose power scales with self.charge (0..100).
        Higher power = more ammo cost, more damage, pierces more asteroids,
        scores bonus points per hit."""
        if self.ship.ammo <= 0:
            return
        # 1..5 tiers based on charge; clamped, since the student may push
        # charge well beyond 100 (other max_charge, forgotten break...)
        power = min(5, max(1, int(self.charge) // 20))
        # ammo cost scales with power: 1, 2, 4, 7, 10 (steeper for high charge)
        ammo_cost = [0, 1, 2, 4, 7, 10][power]
        ammo_cost = min(ammo_cost, self.ship.ammo)  # never below 0
        speed = float(f.bullet_speed) or 8.0
        b = Bullet(self.ship.x, self.ship.y - C.SHIP_H / 2, speed, damage=power)
        b.charged_power = power
        b.pierce_remaining = power  # can pierce through 'power' asteroids
        self.bullets.append(b)
        self.ship.ammo = max(0, self.ship.ammo - ammo_cost)
        self.fire_cd = 12

    def _fire_burst(self, f):
        """Chapter 4: fires N shots in sequence (student's for loop drives N)."""
        if not self.slow_loops or "burst" not in self.slow_loops.loops:
            return
        if not self._start_loop("burst", {"burst_count": 3, "fired": 0}):
            return
        self.burst_remaining = -1  # sentinel: burst is active
        self.burst_wait = 0
        self.last_fired = self._as_number(self.slow_loops.namespace.get("fired", 0))

    def _step_burst(self, f):
        """Step the burst loop one iteration per frame; each iter fires a bullet."""
        if self.burst_remaining == 0 or not self.slow_loops:
            return
        # one turn every BURST_STEP_FRAMES frames: shots are spaced out
        # and a skipped turn leaves a visible gap in the burst.
        if getattr(self, "burst_wait", 0) > 0:
            self.burst_wait -= 1
            return
        self.burst_wait = BURST_STEP_FRAMES
        before = self.last_fired
        running, ns = self.slow_loops.step_event("burst")
        self.loop_turns = self.slow_loops.iterations("burst")
        after = self._as_number(ns.get("fired", 0))
        self.last_fired = after
        # A projectile leaves only when the turn increased fired: a turn
        # abandoned with continue (or a body without fired += 1) fires nothing.
        if after > before and self.ship.ammo > 0:
            speed = float(f.bullet_speed) or 8.0
            self.bullets.append(
                Bullet(self.ship.x, self.ship.y - C.SHIP_H / 2, speed, 1))
            self.ship.ammo = max(0, self.ship.ammo - 1)
        if not running:
            self._report_loop_error("burst")
            self.burst_remaining = 0
            self.fire_cd = 12  # small cooldown after burst

    # ------------------------------------------------------------------
    #  Chapter 4 helpers: start a loop, surface its errors
    # ------------------------------------------------------------------
    @staticmethod
    def _as_number(v):
        return v if isinstance(v, (int, float)) and not isinstance(v, bool) else 0

    def _start_loop(self, event_name, state):
        """Starts the student's loop for an event. Returns True if the
        loop is running (False: no loop written for this event, or an
        error before the first turn, shown in the banner)."""
        if not self.slow_loops:
            return False
        self._check_loops_syntax()
        if not self.slow_loops.start_event(event_name, state):
            return False
        self.loop_turns = 0
        if not self.slow_loops.is_active(event_name):
            self._report_loop_error(event_name)
            return False
        return True

    def _check_loops_syntax(self):
        if self.slow_loops:
            self.slow_loops.reload_if_changed()
            err = self.slow_loops.syntax_error()
            if err:
                self._show_loop_msg(err)

    def _report_loop_error(self, event_name):
        """Shows the error of a stopped loop, if any. Returns True if
        there was one."""
        err = self.slow_loops.get_error(event_name) if self.slow_loops else None
        if err and event_name in self.slow_loops.loops:
            label = hud.loop_event_label(event_name)
            self._show_loop_msg(t("loop_banner_block", name=event_name,
                                  label=label, error=err))
            return True
        return False

    def _show_loop_msg(self, msg):
        self.loop_msg = (f"student_loops.py · {msg}", LOOP_MSG_FRAMES,
                         "loop_banner_footer")

    def _show_config_problems(self):
        """Every chapter: problems of student_config.py shown in the red
        banner at launch and at each restart (not only in pause)."""
        problems = self.features.problems
        if problems:
            msg = "student_config.py · " + "  |  ".join(problems[:3])
            if len(problems) > 3:
                msg += " " + t("config_more", n=len(problems) - 3)
            self.loop_msg = (msg, LOOP_MSG_FRAMES, "config_banner_footer")

    def _update_bullets(self):
        for b in self.bullets:
            b.update()
        # a shot that exits the top without hitting = missed -> reset combo
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
        # bullets against enemies (charged bullets can pierce and score more)
        for b in list(self.bullets):
            for e in list(self.enemies):
                if b.rect.colliderect(e.rect):
                    e.hp = e.hp - b.damage
                    if e.hp <= 0:
                        self._destroy(e, f)
                        # charged shot: bonus points per hit (proportional to power)
                        power = getattr(b, "charged_power", 1)
                        if power > 1:
                            bonus = int(self._points_per_hit(f) * (power - 1) * self.bonus_mult)
                            self.score += max(0, bonus)
                    # pierce: charged bullets keep going through 'pierce_remaining' asteroids
                    pierce = getattr(b, "pierce_remaining", 0)
                    if pierce > 0:
                        b.pierce_remaining = pierce - 1
                        # bullet continues, don't remove it
                    else:
                        if b in self.bullets:
                            self.bullets.remove(b)
                    break

        # ship against enemies
        if self.ship.invuln <= 0:
            for e in list(self.enemies):
                if self.ship.rect.colliderect(e.rect):
                    self.enemies.remove(e)
                    if self.shield_level > 0:
                        # the shield absorbs the hit: one level down
                        self.shield_level -= 1
                        self.ship.invuln = C.INVULN_FRAMES
                    else:
                        self._hurt(f)
                    break

        # ship against bonuses
        for p in list(self.powerups):
            if self.ship.rect.colliderect(p.rect):
                self.powerups.remove(p)
                self._apply_powerup(p, f)

        # friendly fire: bullets can also hit the ship on the way down
        if f.friendly_fire:
            for b in list(self.bullets):
                if b.y > C.HEIGHT - 8 and b.rect.colliderect(self.ship.rect):
                    self.bullets.remove(b)

    def _points_per_hit(self, f):
        """Points per asteroid. If points_per_hit is defined, it is used;
        otherwise it is computed as base_hit_points * bonus_points.
        Neutral default = 0."""
        if f.unlocked.get("points_per_hit") and f.points_per_hit:
            return float(f.points_per_hit)
        return float(f.base_hit_points) * float(f.bonus_points)

    def _destroy(self, enemy, f):
        if enemy in self.enemies:
            self.enemies.remove(enemy)

        # score = points per hit × combo multiplier (if chained)
        #         × active bonus multiplier
        base = self._points_per_hit(f)
        combo_factor = self.combo * float(f.combo_multiplier) if self.combo > 1 else 1
        gain = base * combo_factor * self.bonus_mult
        self.score += max(0, int(round(gain)))

        # a successful hit extends the chain
        self.combo += 1
        self.combo_timer = 0

        # recurring bonus (model A): a bonus drops at each threshold crossed
        self._check_bonus_threshold(f, enemy.x, enemy.y)

        for _ in range(8):
            self.particles.append([enemy.x, enemy.y,
                                   random.uniform(-3, 3),
                                   random.uniform(-3, 3), 20])

    def _check_bonus_threshold(self, f, x, y):
        """Model A: bonus at each multiple of bonus_threshold, threshold
        re-armed afterwards."""
        thr = float(f.bonus_threshold)
        if thr <= 0 or thr >= 10 ** 9:
            return
        if self.bonus_next is None:
            self.bonus_next = thr
        # can cross multiple thresholds at once on a big score gain
        dropped = False
        while self.score >= self.bonus_next:
            self.bonus_next += thr
            dropped = True
        if dropped:
            self._spawn_bonus(x, y, f)

    def _spawn_bonus(self, x, y, f):
        """Drops a bonus. The effect is drawn at random inside the
        engine, among three outcomes: score multiplier (gold), ammo
        refill (cyan) or one shield level (green)."""
        r = random.random()
        if r < 1 / 3:
            pu = PowerUp(x, y, "gold", "score_bonus", float(f.bonus_duration))
        elif r < 2 / 3:
            pu = PowerUp(x, y, "cyan", "ammo_refill", 0)
        else:
            pu = PowerUp(x, y, "green", "shield_up", 0)
        self.powerups.append(pu)

    def _hurt(self, f):
        self.ship.lives -= 1
        self.combo = 1               # a hit on the ship breaks the combo
        self.combo_timer = 0
        self.ship.invuln = C.INVULN_FRAMES
        if self.ship.lives <= 0:
            # Raw ending by default, from chapter 1: the ship
            # explodes and the game freezes (no proper game-over screen).
            # The game_over rule output (chapter 3) turns this freeze into
            # a proper game-over screen. The game never closes: it freezes
            # (the game never crashes).
            self._explode_ship()
            self.state = FROZEN

    def _explode_ship(self):
        """Ship explosion: burst of particles at its position."""
        for _ in range(30):
            self.particles.append([self.ship.x, self.ship.y,
                                   random.uniform(-5, 5),
                                   random.uniform(-5, 5),
                                   random.randint(20, 40)])

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
            # Chapter 2: activates the bonus multiplier for its duration.
            mult = float(f.bonus_points) if f else 1.0
            self.bonus_mult = mult if mult > 0 else 1.0
            self.bonus_active_frames = max(frames, 1)
        elif effect == "ammo_refill":
            # ammo refill (random engine bonus)
            if self.max_ammo > 0:
                self.ship.ammo = min(self.max_ammo, self.ship.ammo + C.BONUS_AMMO_REFILL)
                self.reloading = 0  # cancels a reload in progress if needed
        elif effect == "shield_up":
            # shield bonus (ch3): gains one level, capped at 3
            self.shield_level = min(3, self.shield_level + 1)
        elif effect in ("rapid_fire", "rapid"):
            self.rapid = max(frames, C.FPS * 3)
        else:  # heal and any unknown effect
            self.ship.lives += 1
        if self.max_ammo and effect not in ("score_bonus", "ammo_refill"):
            self.ship.ammo = min(self.max_ammo, self.ship.ammo + 5)

    # ------------------------------------------------------------------
    def _spawn_logic(self, f):
        # If the student has taken over spawn (spawn_row /
        # spawn_pattern, later chapters), we keep THEIR behavior
        # by waves. Otherwise, default engine behavior: X scatter
        # randomized + multiple simultaneous asteroids at a set pace.
        student_controls_spawn = (
            f.unlocked.get("spawn_row") or f.unlocked.get("spawn_pattern")
        )
        if student_controls_spawn:
            self._spawn_waves(f)
        else:
            self._spawn_stream(f)

    def _spawn_stream(self, f):
        """Engine default: a stream of asteroids scattered across the width,
        several on screen, one every SPAWN_INTERVAL frames. The random
        position stays inside the engine."""
        if self.wave_timer > 0:
            self.wave_timer -= 1
            return
        if len(self.enemies) >= C.MAX_ASTEROIDS:
            self.wave_timer = 10
            return

        level = f.difficulty(self.score)
        factor = {"easy": 1.0, "normal": 1.35, "hard": 1.8}.get(str(level).lower(), 1.0)
        hard_factor = 1.4 if f.is_hard else 1.0
        base_speed, _ = 2.0, None
        speed = max(0.5, base_speed * factor * hard_factor * float(f.global_difficulty))

        # X position scattered across the width (random, hidden in Core)
        x = random.uniform(C.SPAWN_MARGIN, C.WIDTH - C.SPAWN_MARGIN)
        y = -30

        types = f.enemy_types
        if types:
            cls = types[random.randrange(len(types))]
            try:
                self.enemies.append(StudentEnemy(cls(x, y), speed))
            except Exception:  # noqa: BLE001
                self.enemies.append(Asteroid(x, y, speed))
        else:
            self.enemies.append(Asteroid(x, y, speed))

        self.wave_timer = C.SPAWN_INTERVAL

    def _spawn_waves(self, f):
        """Wave behavior driven by the student (spawn_row /
        spawn_pattern), reserved for later chapters."""
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
        """Current value of a quantity for the debug overlay."""
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
        if key == "charge":
            v = self.charge if self.charging else self.last_charge
            return f"{v:g}" if isinstance(v, float) else v
        if key == "fired":
            return self.last_fired
        if key == "iterations":
            return self.loop_turns
        return "?"

    def _shield_draw_color(self):
        """Shield circle color: the one chosen by the student
        in their match (shield_color), otherwise blue by default."""
        name = str(self.rule_outputs.get("shield_color", "")).lower().strip()
        return C.COLOR_NAMES.get(name, C.BLUE)

    def _timers(self):
        if self.rapid > 0:
            self.rapid -= 1
        self._update_particles()

    def _timers_ch2(self, f):
        """Chapter 2: combo delay, active bonus, HUD highlight, alert."""
        # combo delay: reset after combo_reset_delay seconds without firing
        delay = float(f.combo_reset_delay)
        if delay > 0 and self.combo > 1:
            self.combo_timer += 1
            if self.combo_timer >= delay * C.FPS:
                self.combo = 1
                self.combo_timer = 0
        # active bonus: countdown then return to multiplier 1
        if self.bonus_active_frames > 0:
            self.bonus_active_frames -= 1
            if self.bonus_active_frames == 0:
                self.bonus_mult = 1.0
        # HUD highlight: score above the threshold
        hl = float(f.highlight_score)
        self.hud_highlight = (hl < 10 ** 9) and (self.score >= hl)
        # low ammo alert
        lat = float(f.low_ammo_threshold)
        self.low_ammo_alert = (lat >= 0) and (self.ship.ammo <= lat)

    def _student_hook(self):
        """Free extension point: student_update(state), if defined."""
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
        # decrements the visual feedback "copied!" (shown in pause)
        flash = getattr(f, "_copied_flash", None)
        if flash and flash[1] > 0:
            f._copied_flash = (flash[0], flash[1] - 1)
        bg = assets.load(f.background_image, (C.WIDTH, C.HEIGHT))
        if bg is not None:
            s.blit(bg, (0, 0))
        else:
            s.fill(C.BLACK)
            self._draw_starfield(s)

        for e in self.enemies:
            # an internal asteroid takes asteroid_sprite (ch2); a student
            # enemy (class) takes enemy_sprite (ch5).
            spr = f.asteroid_sprite if isinstance(e, Asteroid) else f.enemy_sprite
            e.draw(s, spr)
        for p in self.powerups:
            # a score bonus (ch2) takes bonus_sprite; the others
            # power-ups prennent powerup_sprite (ch8).
            spr = f.bonus_sprite if str(p.effect).lower() == "score_bonus" else f.powerup_sprite
            p.draw(s, spr)
        for b in self.bullets:
            b.draw(s, f.bullet_sprite)
        for px, py, _, _, life in self.particles:
            pygame.draw.circle(s, C.ORANGE, (int(px), int(py)),
                               max(1, life // 6))

        if self.state not in (GAMEOVER, FROZEN):
            # ship body color during an active bonus: the
            # student's is None rule sets ship_glow (color name).
            glow = str(self.rule_outputs.get("ship_glow", "")).lower().strip()
            body_color = C.COLOR_NAMES.get(glow) if glow else None
            self.ship.draw(s, getattr(self, "thrust", False), f.ship_sprite,
                           body_color)
            if self.shield_level > 0:
                # color driven by the student's match (shield_color),
                # otherwise blue by default. Thickness = shield level.
                col = self._shield_draw_color()
                pygame.draw.circle(s, col,
                                   (int(self.ship.x), int(self.ship.y)),
                                   C.SHIP_W + 4, self.shield_level + 1)
            # --- Chapter 4: charge bar visible above ship while charging ---
            if self.charging and self.charge > 0:
                bar_w = 60
                bar_h = 8
                bx = int(self.ship.x - bar_w // 2)
                by = int(self.ship.y - C.SHIP_H // 2 - 20)
                # background
                pygame.draw.rect(s, (40, 40, 40), (bx, by, bar_w, bar_h))
                # fill proportional to charge (0..100)
                fill_w = int(bar_w * min(self.charge, 100) / 100)
                # color shifts as charge grows: yellow -> orange -> white-hot
                if self.charge >= 100:
                    fill_col = (255, 255, 255)  # white when maxed
                elif self.charge >= 60:
                    fill_col = (255, 140, 40)   # orange
                else:
                    fill_col = (255, 200, 60)   # yellow
                pygame.draw.rect(s, fill_col, (bx, by, fill_w, bar_h))
                # border
                pygame.draw.rect(s, C.WHITE, (bx, by, bar_w, bar_h), 1)

        # raw ending: the game is frozen, discreet message (no proper screen)
        if self.state == FROZEN:
            hud.text(s, self.fonts.mid, t("ship_destroyed"),
                     C.WIDTH // 2 - 90, C.HEIGHT // 2 - 20, C.RED)
            hud.text(s, self.fonts.small, t("game_frozen"),
                     C.WIDTH // 2 - 95, C.HEIGHT // 2 + 14, C.GREY)

        hud.draw_hud(s, self.fonts, self)

        # debug overlay (chapter 2): if show_debug is enabled
        if self.features.show_debug and self.state in (PLAYING, COUNTDOWN):
            hud.draw_debug_overlay(s, self.fonts, self, self.current_chapter)

        if self.reloading > 0:
            ratio = 1 - self.reloading / max(1, int(self.features.reload_time))
            hud.draw_reloading(s, self.fonts, ratio)

        if self.state == COUNTDOWN:
            hud.draw_countdown(s, self.fonts,
                               self.countdown_value if self.countdown_student
                               else (self.countdown_frames + C.FPS - 1) // C.FPS)

        if self.features.has_student_draw:
            try:
                self.features.cfg.student_draw(s, {"score": self.score,
                                                   "wave": self.wave})
            except Exception:  # noqa: BLE001
                pass

        # red error banner (student_config.py problems, student_loops.py
        # errors): stays a few seconds, frozen in pause while it runs
        if self.loop_msg:
            msg, frames, footer = self.loop_msg
            if frames > 0:
                hud.draw_loop_error(s, self.fonts, msg, footer)
                if self.state != PAUSED:
                    self.loop_msg = (msg, frames - 1, footer)
            else:
                self.loop_msg = None

        if self.state == GAMEOVER:
            hud.draw_game_over(s, self.fonts, self)
        elif self.state == PAUSED:
            self._paused_copyable = hud.draw_pause(
                s, self.fonts, self.features,
                self.current_chapter, self._hover_zones(),
                pygame.mouse.get_pos(),
                set(self.slow_loops.loops) if self.slow_loops else ())

        if self.state == PLAYING and self.wave == 0:
            hud.text(s, self.fonts.small,
                     t("start_hint_ch4") if self.current_chapter >= 4
                     else t("start_hint"),
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
