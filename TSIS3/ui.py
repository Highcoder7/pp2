import pygame


class Button:
    def __init__(self, rect, text, bg=(60, 60, 180), fg=(255, 255, 255)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.bg = bg
        self.fg = fg

    def draw(self, surface, font):
        pygame.draw.rect(surface, self.bg, self.rect, border_radius=8)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2, border_radius=8)
        lbl = font.render(self.text, True, self.fg)
        surface.blit(lbl, lbl.get_rect(center=self.rect.center))

    def hit(self, pos):
        return self.rect.collidepoint(pos)


def draw_text(surface, text, font, color, center):
    surf = font.render(text, True, color)
    surface.blit(surf, surf.get_rect(center=center))


def username_screen(screen, clock, font_big, font_md):
    name = ""
    W, H = screen.get_size()
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
        screen.fill((20, 20, 40))
        draw_text(screen, "Enter your name", font_big, (255, 220, 50), (W//2, H//2 - 60))
        draw_text(screen, name + "|", font_md, (255, 255, 255), (W//2, H//2))
        draw_text(screen, "Press Enter to start", font_md, (180, 180, 180), (W//2, H//2 + 50))
        pygame.display.flip()
        clock.tick(30)


def main_menu(screen, clock, font_big, font_md):
    W, H = screen.get_size()
    buttons = [
        Button((W//2 - 100, 200, 200, 44), "Play"),
        Button((W//2 - 100, 260, 200, 44), "Leaderboard"),
        Button((W//2 - 100, 320, 200, 44), "Settings"),
        Button((W//2 - 100, 380, 200, 44), "Quit", bg=(160, 40, 40)),
    ]
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return "quit"
            if ev.type == pygame.MOUSEBUTTONDOWN:
                for i, b in enumerate(buttons):
                    if b.hit(ev.pos):
                        return ["play", "leaderboard", "settings", "quit"][i]
        screen.fill((20, 20, 40))
        draw_text(screen, "RACER", font_big, (255, 220, 50), (W//2, 120))
        for b in buttons:
            b.draw(screen, font_md)
        pygame.display.flip()
        clock.tick(30)


def leaderboard_screen(screen, clock, font_big, font_md, font_sm, entries):
    W, H = screen.get_size()
    back_btn = Button((W//2 - 60, H - 70, 120, 40), "Back")
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return
            if ev.type == pygame.MOUSEBUTTONDOWN and back_btn.hit(ev.pos):
                return
        screen.fill((10, 10, 30))
        draw_text(screen, "Leaderboard", font_big, (255, 220, 50), (W//2, 50))
        headers = f"{'#':<4} {'Name':<16} {'Score':>8} {'Dist':>8}"
        draw_text(screen, headers, font_sm, (180, 180, 255), (W//2, 100))
        for i, e in enumerate(entries[:10]):
            line = f"{i+1:<4} {e['username']:<16} {e['score']:>8} {e['distance']:>7}m"
            draw_text(screen, line, font_sm, (220, 220, 220), (W//2, 130 + i * 28))
        back_btn.draw(screen, font_md)
        pygame.display.flip()
        clock.tick(30)


def gameover_screen(screen, clock, font_big, font_md, score, distance, coins):
    W, H = screen.get_size()
    retry_btn = Button((W//2 - 110, H//2 + 60, 100, 40), "Retry")
    menu_btn = Button((W//2 + 10, H//2 + 60, 100, 40), "Menu")
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return "quit"
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if retry_btn.hit(ev.pos):
                    return "retry"
                if menu_btn.hit(ev.pos):
                    return "menu"
        screen.fill((30, 10, 10))
        draw_text(screen, "GAME OVER", font_big, (255, 60, 60), (W//2, H//2 - 100))
        draw_text(screen, f"Score: {score}", font_md, (255, 255, 200), (W//2, H//2 - 40))
        draw_text(screen, f"Distance: {int(distance)} m", font_md, (200, 255, 200), (W//2, H//2))
        draw_text(screen, f"Coins: {coins}", font_md, (255, 220, 80), (W//2, H//2 + 30))
        retry_btn.draw(screen, font_md)
        menu_btn.draw(screen, font_md)
        pygame.display.flip()
        clock.tick(30)


def settings_screen(screen, clock, font_big, font_md, settings):
    W, H = screen.get_size()
    save_btn = Button((W//2 - 80, H - 80, 160, 40), "Save & Back")
    colors = [(0, 100, 255), (255, 50, 50), (50, 200, 50), (255, 165, 0), (200, 0, 200)]
    color_idx = 0
    for i, c in enumerate(colors):
        if list(c) == settings.get("car_color", [0, 100, 255]):
            color_idx = i
    diff_options = ["easy", "normal", "hard"]
    diff_idx = diff_options.index(settings.get("difficulty", "normal"))

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return settings
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if save_btn.hit(ev.pos):
                    settings["car_color"] = list(colors[color_idx])
                    settings["difficulty"] = diff_options[diff_idx]
                    return settings
                # Sound toggle
                st = pygame.Rect(W//2 + 40, 180, 80, 30)
                if st.collidepoint(ev.pos):
                    settings["sound"] = not settings.get("sound", True)
                # Color cycle
                cc = pygame.Rect(W//2 + 40, 240, 80, 30)
                if cc.collidepoint(ev.pos):
                    color_idx = (color_idx + 1) % len(colors)
                # Difficulty cycle
                dc = pygame.Rect(W//2 + 40, 300, 80, 30)
                if dc.collidepoint(ev.pos):
                    diff_idx = (diff_idx + 1) % len(diff_options)

        screen.fill((20, 30, 50))
        draw_text(screen, "Settings", font_big, (255, 220, 50), (W//2, 80))

        draw_text(screen, "Sound:", font_md, (220, 220, 220), (W//2 - 60, 195))
        snd_lbl = "ON" if settings.get("sound", True) else "OFF"
        pygame.draw.rect(screen, (60, 120, 60) if settings.get("sound") else (120, 60, 60),
                         (W//2 + 40, 180, 80, 30), border_radius=5)
        draw_text(screen, snd_lbl, font_md, (255, 255, 255), (W//2 + 80, 195))

        draw_text(screen, "Car Color:", font_md, (220, 220, 220), (W//2 - 80, 255))
        pygame.draw.rect(screen, colors[color_idx], (W//2 + 40, 240, 80, 30), border_radius=5)

        draw_text(screen, "Difficulty:", font_md, (220, 220, 220), (W//2 - 80, 315))
        pygame.draw.rect(screen, (60, 60, 160), (W//2 + 40, 300, 80, 30), border_radius=5)
        draw_text(screen, diff_options[diff_idx].capitalize(), font_md, (255, 255, 255),
                  (W//2 + 80, 315))

        save_btn.draw(screen, font_md)
        pygame.display.flip()
        clock.tick(30)
