import os
import random
import sys

import pygame

from persistence import load_leaderboard, save_leaderboard, add_score, load_settings, save_settings
from racer import (
    PlayerCar, TrafficCar, Obstacle, Coin, PowerUp, NitroStrip,
    Road, LANE_COUNT, DIFF_PARAMS, POWERUP_TYPES,
    CAR_H, CAR_W, POWERUP_SIZE, ROAD_LEFT, ROAD_RIGHT,
)
from ui import (
    main_menu, leaderboard_screen, gameover_screen,
    settings_screen, username_screen, draw_text,
)

W, H = 800, 650
FPS = 60


def run_game(screen, clock, username, settings, fonts):
    font_big, font_md, font_sm = fonts
    diff = settings.get("difficulty", "normal")
    params = DIFF_PARAMS[diff]
    car_color = tuple(settings.get("car_color", [0, 100, 255]))

    road = Road()
    road.speed = params["base_speed"]

    player = PlayerCar(car_color)
    traffic = []
    obstacles = []
    coins = []
    powerups = []
    nitro_strips = []

    score = 0
    coin_count = 0
    distance = 0.0
    frame = 0

    active_powerup = None
    powerup_end = 0
    active_powerup_label = ""

    # Load scrolling background image (grass + trees scenery on sides of road)
    _asset_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    bg_path = os.path.join(_asset_dir, "дорога.png")
    bg_img = None
    if os.path.exists(bg_path):
        bg_img = pygame.image.load(bg_path).convert()
        bg_img = pygame.transform.scale(bg_img, (W, H))
    bg_scroll = 0.0  # vertical scroll position for the background image

    alive = True
    key_cooldown = 0
    lane_change_grace = 0  # ms timestamp until which lane-change grace is active

    while alive:
        clock.tick(FPS)
        frame += 1
        now = pygame.time.get_ticks()

        # ---- Events ----
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_LEFT, pygame.K_a) and key_cooldown == 0:
                    player.move("left")
                    key_cooldown = 8
                    lane_change_grace = now + 200
                if ev.key in (pygame.K_RIGHT, pygame.K_d) and key_cooldown == 0:
                    player.move("right")
                    key_cooldown = 8
                    lane_change_grace = now + 200

        if key_cooldown > 0:
            key_cooldown -= 1

        # ---- Speed ----
        base = params["base_speed"]
        speed_mult = 1 + coin_count // 10 * 0.15
        if diff == "hard":
            speed_mult += 0.05
        current_speed = base * speed_mult

        if active_powerup == "nitro" and now < powerup_end:
            current_speed *= 1.6
        elif active_powerup == "slow" and now < powerup_end:
            current_speed *= 0.5
        elif active_powerup and now >= powerup_end and active_powerup != "shield":
            active_powerup = None

        road.speed = current_speed

        # ---- Spawning ----
        sr = max(20, int(params["spawn_rate"] / speed_mult))
        if frame % sr == 0:
            # pick a lane that doesn't already have a car near the player's y
            safe_lanes = [
                l for l in range(LANE_COUNT)
                if not any(t.lane == l and t.y > player.y - 300 for t in traffic)
            ]
            if safe_lanes:
                lane = random.choice(safe_lanes)
                traffic.append(TrafficCar(lane, current_speed * 0.7))

        obs_r = max(60, int(params["obstacle_rate"] / speed_mult))
        if frame % obs_r == 0:
            # don't spawn obstacle in player's current lane
            safe_lanes = [l for l in range(LANE_COUNT) if l != player.lane]
            if safe_lanes:
                lane = random.choice(safe_lanes)
                kind = random.choice(["barrier", "oil", "pothole"])
                obstacles.append(Obstacle(lane, current_speed, kind))

        if frame % 45 == 0:
            lane = random.randint(0, LANE_COUNT - 1)
            value = random.choices([1, 3, 5], weights=[6, 3, 1])[0]
            coins.append(Coin(lane, current_speed, value))

        if frame % 200 == 0 and not any(isinstance(p, PowerUp) for p in powerups):
            lane = random.randint(0, LANE_COUNT - 1)
            kind = random.choice(POWERUP_TYPES)
            powerups.append(PowerUp(lane, current_speed, kind))

        if frame % 300 == 0:
            lane = random.randint(0, LANE_COUNT - 1)
            nitro_strips.append(NitroStrip(lane, current_speed))

        # ---- Update ----
        road.update()
        distance += current_speed * (1 / FPS) * 10

        for t in traffic[:]:
            t.speed = current_speed * 0.7
            t.update()
            if t.y > H + CAR_H:
                traffic.remove(t)

        for o in obstacles[:]:
            o.speed = current_speed
            o.update()
            if o.y > H + 50:
                obstacles.remove(o)

        for c in coins[:]:
            c.speed = current_speed
            c.update()
            if c.y > H + 30:
                coins.remove(c)
            elif c.rect().colliderect(player.rect()):
                coin_count += c.value
                score += c.value * 10
                coins.remove(c)

        for p in powerups[:]:
            p.speed = current_speed
            p.update()
            if p.y > H + POWERUP_SIZE or p.expired():
                powerups.remove(p)
            elif p.rect().colliderect(player.rect()):
                powerups.remove(p)
                if p.kind == "nitro":
                    active_powerup = "nitro"
                    powerup_end = now + 4000
                    active_powerup_label = "NITRO"
                elif p.kind == "shield":
                    player.shield = True
                    active_powerup = "shield"
                    active_powerup_label = "SHIELD"
                elif p.kind == "repair":
                    score += 50
                    active_powerup = None
                    active_powerup_label = "REPAIR +50"
                    powerup_end = now + 1500

        for ns in nitro_strips[:]:
            ns.speed = current_speed
            ns.update()
            if ns.y > H + 20:
                nitro_strips.remove(ns)
            elif ns.rect().colliderect(player.rect()):
                nitro_strips.remove(ns)
                active_powerup = "nitro"
                powerup_end = now + 3000
                active_powerup_label = "NITRO STRIP"

        # ---- Collisions (skip during lane-change grace window) ----
        if now >= lane_change_grace:
            for t in traffic:
                if t.rect().colliderect(player.rect()):
                    if player.shield:
                        player.shield = False
                        active_powerup = None
                        traffic.remove(t)
                        break
                    else:
                        alive = False
                        break

            for o in obstacles:
                if o.rect().colliderect(player.rect()):
                    if player.shield:
                        player.shield = False
                        active_powerup = None
                        obstacles.remove(o)
                        break
                    elif o.kind == "oil":
                        active_powerup = "slow"
                        powerup_end = now + 2000
                        active_powerup_label = "OIL SLIP"
                        obstacles.remove(o)
                        break
                    else:
                        alive = False
                        break

        score += int(current_speed * 0.01)

        # ---- Draw ----
        # Scroll the scenery background at a fraction of the road speed
        bg_scroll = (bg_scroll + current_speed * 0.35) % H
        if bg_img:
            # Blit two copies for seamless vertical loop
            screen.blit(bg_img, (0, int(bg_scroll) - H))
            screen.blit(bg_img, (0, int(bg_scroll)))
        else:
            screen.fill((80, 130, 80))
        # Road (grey surface + lane markings) drawn on top of the scenery
        road.draw(screen, H)

        for ns in nitro_strips:
            ns.draw(screen)
        for t in traffic:
            t.draw(screen)
        for o in obstacles:
            o.draw(screen)
        for c in coins:
            c.draw(screen)
        for p in powerups:
            p.draw(screen)
        player.draw(screen)

        # HUD
        pygame.draw.rect(screen, (0, 0, 0, 160), (0, 0, W, 36))
        draw_text(screen, f"Score: {score}", font_sm, (255, 255, 255), (80, 18))
        draw_text(screen, f"Dist: {int(distance)}m", font_sm, (200, 255, 200), (220, 18))
        draw_text(screen, f"Coins: {coin_count}", font_sm, (255, 215, 0), (360, 18))
        draw_text(screen, f"Speed: {current_speed:.1f}", font_sm, (200, 200, 255), (500, 18))

        if active_powerup_label:
            remaining = max(0, (powerup_end - now) / 1000) if active_powerup not in ("shield",) else -1
            label = active_powerup_label
            if remaining > 0:
                label += f" {remaining:.1f}s"
            draw_text(screen, label, font_sm, (255, 220, 50), (W - 120, 18))
            if now > powerup_end + 200 and active_powerup not in ("shield",):
                active_powerup_label = ""

        draw_text(screen, username, font_sm, (180, 255, 180), (W - 60, H - 20))

        pygame.display.flip()

    add_score(username, score, distance)
    return score, distance, coin_count


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
    pygame.display.set_caption("Racer")
    clock = pygame.time.Clock()

    font_big = pygame.font.SysFont("Arial", 48, bold=True)
    font_md = pygame.font.SysFont("Arial", 24)
    font_sm = pygame.font.SysFont("Arial", 18)
    fonts = (font_big, font_md, font_sm)

    _asset_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    settings_music = os.path.join(_asset_dir, "настроки машина.mp3")

    settings = load_settings()
    username = None

    # Start menu music immediately on launch
    _play_settings_music(settings_music, settings.get("sound", True))

    while True:
        action = main_menu(screen, clock, font_big, font_md)

        if action == "quit":
            _stop_music()
            break

        elif action == "leaderboard":
            lb = load_leaderboard()
            leaderboard_screen(screen, clock, font_big, font_md, font_sm, lb)

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

            result = run_game(screen, clock, username, settings, fonts)
            score, distance, coins = result
            outcome = gameover_screen(screen, clock, font_big, font_md, score, distance, coins)

            # Resume menu music after returning from game
            _play_settings_music(settings_music, settings.get("sound", True))

            if outcome == "quit":
                break
            elif outcome == "retry":
                _stop_music()
                result = run_game(screen, clock, username, settings, fonts)
                score, distance, coins = result
                gameover_screen(screen, clock, font_big, font_md, score, distance, coins)
                _play_settings_music(settings_music, settings.get("sound", True))
            # "menu" → loop back

    save_settings(settings)
    pygame.quit()


if __name__ == "__main__":
    main()
