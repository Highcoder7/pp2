import json
import os
import random
import sys

import pygame

from config import CELL, COLS, ROWS, W, H, FPS
from game import (
    Snake, Food, PowerUpItem, generate_obstacles, draw_obstacles, draw_grid,
    get_bg_surf, UP, DOWN, LEFT, RIGHT,
)
from db import init_db, get_or_create_player, save_session, get_personal_best, get_top10

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

# ---------------------------------------------------------------------------
# Settings helpers
# ---------------------------------------------------------------------------

def load_settings():
    defaults = {"snake_color": [0, 200, 80], "grid": True, "sound": True}
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, encoding="utf-8") as f:
            data = json.load(f)
        defaults.update(data)
    return defaults


def save_settings(s):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(s, f, indent=2)


# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------

def draw_text(surface, text, font, color, center):
    surf = font.render(text, True, color)
    surface.blit(surf, surf.get_rect(center=center))


class Button:
    def __init__(self, rect, label, bg=(60, 60, 180)):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.bg = bg

    def draw(self, surface, font):
        pygame.draw.rect(surface, self.bg, self.rect, border_radius=7)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2, border_radius=7)
        draw_text(surface, self.label, font, (255, 255, 255), self.rect.center)

    def hit(self, pos):
        return self.rect.collidepoint(pos)


# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------

def username_screen(screen, clock, font_big, font_md):
    name = ""
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return None
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif ev.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif ev.unicode.isprintable() and len(name) < 16:
                    name += ev.unicode
        screen.fill((15, 15, 30))
        draw_text(screen, "Snake Game", font_big, (80, 220, 80), (W // 2, H // 2 - 80))
        draw_text(screen, "Enter username:", font_md, (200, 200, 200), (W // 2, H // 2 - 20))
        draw_text(screen, name + "|", font_md, (255, 255, 255), (W // 2, H // 2 + 20))
        draw_text(screen, "Press Enter", font_md, (140, 140, 140), (W // 2, H // 2 + 60))
        pygame.display.flip()
        clock.tick(30)


def main_menu(screen, clock, font_big, font_md):
    btns = [
        Button((W // 2 - 90, 200, 180, 42), "Play"),
        Button((W // 2 - 90, 258, 180, 42), "Leaderboard"),
        Button((W // 2 - 90, 316, 180, 42), "Settings"),
        Button((W // 2 - 90, 374, 180, 42), "Quit", bg=(160, 40, 40)),
    ]
    actions = ["play", "leaderboard", "settings", "quit"]
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return "quit"
            if ev.type == pygame.MOUSEBUTTONDOWN:
                for i, b in enumerate(btns):
                    if b.hit(ev.pos):
                        return actions[i]
        screen.fill((15, 15, 30))
        draw_text(screen, "SNAKE", font_big, (80, 220, 80), (W // 2, 120))
        for b in btns:
            b.draw(screen, font_md)
        pygame.display.flip()
        clock.tick(30)


def leaderboard_screen(screen, clock, font_big, font_md, font_sm):
    rows = get_top10()
    back = Button((W // 2 - 60, H - 70, 120, 40), "Back")
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return
            if ev.type == pygame.MOUSEBUTTONDOWN and back.hit(ev.pos):
                return
        screen.fill((10, 10, 25))
        draw_text(screen, "Leaderboard", font_big, (80, 220, 80), (W // 2, 50))
        header = f"{'#':<4}{'Name':<16}{'Score':>7}{'Lvl':>5}{'Date':>12}"
        draw_text(screen, header, font_sm, (180, 180, 255), (W // 2, 100))
        for i, (uname, sc, lvl, dt) in enumerate(rows):
            line = f"{i+1:<4}{uname:<16}{sc:>7}{lvl:>5}{dt:>12}"
            draw_text(screen, line, font_sm, (220, 220, 220), (W // 2, 130 + i * 28))
        back.draw(screen, font_md)
        pygame.display.flip()
        clock.tick(30)


def gameover_screen(screen, clock, font_big, font_md, score, level, best):
    retry = Button((W // 2 - 110, H // 2 + 60, 100, 40), "Retry")
    menu  = Button((W // 2 + 10,  H // 2 + 60, 100, 40), "Menu")
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return "quit"
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if retry.hit(ev.pos): return "retry"
                if menu.hit(ev.pos):  return "menu"
        screen.fill((30, 10, 10))
        draw_text(screen, "GAME OVER", font_big, (255, 60, 60), (W // 2, H // 2 - 100))
        draw_text(screen, f"Score: {score}",   font_md, (255, 255, 200), (W // 2, H // 2 - 30))
        draw_text(screen, f"Level: {level}",   font_md, (200, 255, 200), (W // 2, H // 2 + 5))
        draw_text(screen, f"Best:  {best}",    font_md, (255, 215,   0), (W // 2, H // 2 + 40))
        retry.draw(screen, font_md)
        menu.draw(screen, font_md)
        pygame.display.flip()
        clock.tick(30)


def settings_screen(screen, clock, font_big, font_md, settings):
    save_btn = Button((W // 2 - 90, H - 80, 180, 42), "Save & Back")
    colors = [(0, 200, 80), (80, 80, 255), (255, 80, 80), (255, 200, 0), (200, 0, 200)]
    col_idx = 0
    for i, c in enumerate(colors):
        if list(c) == settings.get("snake_color", [0, 200, 80]):
            col_idx = i

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return settings
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if save_btn.hit(ev.pos):
                    settings["snake_color"] = list(colors[col_idx])
                    return settings
                # Grid toggle
                if pygame.Rect(W // 2 + 30, 180, 90, 30).collidepoint(ev.pos):
                    settings["grid"] = not settings.get("grid", True)
                # Sound toggle
                if pygame.Rect(W // 2 + 30, 230, 90, 30).collidepoint(ev.pos):
                    settings["sound"] = not settings.get("sound", True)
                # Color cycle
                if pygame.Rect(W // 2 + 30, 280, 90, 30).collidepoint(ev.pos):
                    col_idx = (col_idx + 1) % len(colors)

        screen.fill((20, 30, 50))
        draw_text(screen, "Settings", font_big, (80, 220, 80), (W // 2, 80))

        draw_text(screen, "Grid:", font_md, (220, 220, 220), (W // 2 - 60, 195))
        gc = (60, 140, 60) if settings.get("grid") else (120, 60, 60)
        pygame.draw.rect(screen, gc, (W // 2 + 30, 180, 90, 30), border_radius=5)
        draw_text(screen, "ON" if settings.get("grid") else "OFF", font_md,
                  (255, 255, 255), (W // 2 + 75, 195))

        draw_text(screen, "Sound:", font_md, (220, 220, 220), (W // 2 - 70, 245))
        sc = (60, 140, 60) if settings.get("sound") else (120, 60, 60)
        pygame.draw.rect(screen, sc, (W // 2 + 30, 230, 90, 30), border_radius=5)
        draw_text(screen, "ON" if settings.get("sound") else "OFF", font_md,
                  (255, 255, 255), (W // 2 + 75, 245))

        draw_text(screen, "Color:", font_md, (220, 220, 220), (W // 2 - 70, 295))
        pygame.draw.rect(screen, colors[col_idx], (W // 2 + 30, 280, 90, 30), border_radius=5)

        save_btn.draw(screen, font_md)
        pygame.display.flip()
        clock.tick(30)


# ---------------------------------------------------------------------------
# Core gameplay
# ---------------------------------------------------------------------------

def run_game(screen, clock, username, player_id, personal_best, settings, fonts):
    font_big, font_md, font_sm = fonts
    snake_color = tuple(settings.get("snake_color", [0, 200, 80]))
    show_grid   = settings.get("grid", True)

    snake = Snake(snake_color)
    level = 1
    score = 0
    food_eaten = 0
    speed = FPS
    obstacles = set()

    # Food
    normal_food = Food("normal")
    now = pygame.time.get_ticks()
    normal_food.place(snake.body, now)

    disappear_food = None
    poison_food    = None
    powerup_item   = None

    active_effect  = None
    effect_end     = 0
    shield_active  = False

    frame_counter  = 0

    running = True
    while running:
        now = pygame.time.get_ticks()
        clock.tick(speed)
        frame_counter += 1

        # ---- Input ----
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_UP,    pygame.K_w): snake.change_dir(UP)
                if ev.key in (pygame.K_DOWN,  pygame.K_s): snake.change_dir(DOWN)
                if ev.key in (pygame.K_LEFT,  pygame.K_a): snake.change_dir(LEFT)
                if ev.key in (pygame.K_RIGHT, pygame.K_d): snake.change_dir(RIGHT)

        # ---- Speed effect ----
        eff_speed = speed
        if active_effect == "speed" and now < effect_end:
            eff_speed = min(FPS * 3, speed * 2)
        elif active_effect == "slow" and now < effect_end:
            eff_speed = max(3, speed // 2)
        elif active_effect and now >= effect_end and active_effect != "shield":
            active_effect = None
            shield_active = False

        clock.tick(eff_speed)

        # ---- Move ----
        snake.move()

        # ---- Collision: wall / self / obstacle ----
        died = False
        if snake.collides_wall() or snake.collides_self() or snake.collides_obstacles(obstacles):
            if shield_active:
                shield_active = False
                active_effect = None
                # push snake back in bounds
                snake.body[0] = (
                    max(0, min(COLS - 1, snake.body[0][0])),
                    max(0, min(ROWS - 1, snake.body[0][1])),
                )
            else:
                died = True

        if died:
            save_session(player_id, score, level)
            best = max(personal_best, score)
            return gameover_screen(screen, clock, font_big, font_md, score, level, best), score, level

        # ---- Eat normal food ----
        if snake.head == normal_food.pos:
            snake.grow()
            score += normal_food.points * 10
            food_eaten += 1
            normal_food.place(snake.body + list(obstacles), now)
            if food_eaten % 5 == 0:
                level += 1
                speed = FPS + level * 2
                if level >= 3 and not obstacles:
                    obstacles = generate_obstacles(level, snake.body)
                elif level >= 3:
                    obstacles |= generate_obstacles(level, snake.body)

        # ---- Eat disappear food ----
        if disappear_food:
            if disappear_food.expired(now):
                disappear_food = None
            elif snake.head == disappear_food.pos:
                snake.grow()
                score += disappear_food.points * 10
                disappear_food = None

        # ---- Eat poison food ----
        if poison_food and snake.head == poison_food.pos:
            snake.shrink(2)
            poison_food = None
            if len(snake.body) <= 1:
                save_session(player_id, score, level)
                best = max(personal_best, score)
                return gameover_screen(screen, clock, font_big, font_md, score, level, best), score, level

        # ---- Eat power-up ----
        if powerup_item and snake.head == powerup_item.pos:
            if powerup_item.kind == "speed":
                active_effect = "speed"
                effect_end = now + 5000
            elif powerup_item.kind == "slow":
                active_effect = "slow"
                effect_end = now + 5000
            elif powerup_item.kind == "shield":
                active_effect = "shield"
                shield_active = True
            powerup_item = None

        # ---- Spawn disappear food (random) ----
        if disappear_food is None and random.random() < 0.003:
            df = Food("disappear")
            df.ttl = 6000
            df.place(snake.body + [normal_food.pos] + list(obstacles), now)
            disappear_food = df

        # ---- Spawn poison food ----
        if poison_food is None and random.random() < 0.002:
            pf = Food("poison")
            pf.place(snake.body + [normal_food.pos] + list(obstacles), now)
            poison_food = pf

        # ---- Spawn power-up ----
        if powerup_item is None and random.random() < 0.001:
            kind = random.choice(["speed", "slow", "shield"])
            pos_set = set(snake.body) | {normal_food.pos} | obstacles
            candidates = [(x, y) for x in range(COLS) for y in range(ROWS) if (x, y) not in pos_set]
            if candidates:
                pos = random.choice(candidates)
                powerup_item = PowerUpItem(kind, pos, now)

        if powerup_item and powerup_item.expired(now):
            powerup_item = None

        # ---- Draw ----
        # Draw background: use the field image if available, else solid colour
        bg = get_bg_surf(W, ROWS * CELL)
        if bg:
            screen.fill((20, 20, 20))          # fill HUD area below game field
            screen.blit(bg, (0, 0))            # background covers only the play area
        else:
            screen.fill((20, 20, 20))
        # Grid overlay: skip when background image already shows a grid pattern
        if show_grid and not bg:
            draw_grid(screen)

        draw_obstacles(surface=screen, blocks=obstacles)
        normal_food.draw(screen)
        if disappear_food:
            disappear_food.draw(screen)
        if poison_food:
            poison_food.draw(screen)
        if powerup_item:
            powerup_item.draw(screen)
        snake.draw(screen)

        # HUD
        hud_y = ROWS * CELL
        pygame.draw.rect(screen, (10, 10, 10), (0, hud_y, W, 60))
        draw_text(screen, f"Score: {score}", font_sm, (255, 255, 255), (80, hud_y + 15))
        draw_text(screen, f"Level: {level}", font_sm, (200, 255, 200), (200, hud_y + 15))
        draw_text(screen, f"Best: {personal_best}", font_sm, (255, 215, 0), (320, hud_y + 15))
        if active_effect:
            rem = max(0, (effect_end - now) / 1000) if active_effect != "shield" else 0
            label = active_effect.upper() + (f" {rem:.1f}s" if rem > 0 else "")
            draw_text(screen, label, font_sm, (255, 180, 0), (W - 100, hud_y + 15))

        pygame.display.flip()

    return "menu", score, level


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def _play_settings_music(music_path, sound_on):
    """Start looping the settings background music if sound is enabled."""
    if not sound_on or not os.path.exists(music_path):
        return
    try:
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play(-1)  # -1 = loop forever
    except Exception as e:
        print(f"Music error: {e}")


def _stop_music():
    """Fade out and stop any currently playing music."""
    try:
        pygame.mixer.music.fadeout(400)
    except Exception:
        pass


def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()

    font_big = pygame.font.SysFont("Arial", 44, bold=True)
    font_md  = pygame.font.SysFont("Arial", 22)
    font_sm  = pygame.font.SysFont("Arial", 16)
    fonts = (font_big, font_md, font_sm)

    _asset_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    settings_music = os.path.join(_asset_dir, "настройки змея.mp3")

    try:
        init_db()
    except Exception as e:
        print(f"DB init failed: {e}. Running without DB.")

    settings = load_settings()
    username  = None
    player_id = None
    personal_best = 0

    # Start menu music immediately on launch
    _play_settings_music(settings_music, settings.get("sound", True))

    while True:
        action = main_menu(screen, clock, font_big, font_md)

        if action == "quit":
            _stop_music()
            break

        elif action == "leaderboard":
            try:
                leaderboard_screen(screen, clock, font_big, font_md, font_sm)
            except Exception as e:
                print(f"Leaderboard error: {e}")

        elif action == "settings":
            settings = settings_screen(screen, clock, font_big, font_md, settings)
            save_settings(settings)
            # Sync music with updated sound toggle
            if settings.get("sound", True) and not pygame.mixer.music.get_busy():
                _play_settings_music(settings_music, True)
            elif not settings.get("sound", True):
                _stop_music()

        elif action == "play":
            # Stop music before the game starts
            _stop_music()
            if not username:
                username = username_screen(screen, clock, font_big, font_md)
                if not username:
                    break
                try:
                    player_id = get_or_create_player(username)
                    personal_best = get_personal_best(player_id)
                except Exception:
                    player_id = None
                    personal_best = 0

            outcome, score, level = run_game(
                screen, clock, username, player_id, personal_best, settings, fonts
            )
            personal_best = max(personal_best, score)

            # Resume menu music after returning from game
            _play_settings_music(settings_music, settings.get("sound", True))

            if outcome == "quit":
                break
            elif outcome == "retry":
                _stop_music()
                continue
            # "menu" → loop back

    save_settings(settings)
    pygame.quit()


if __name__ == "__main__":
    main()
