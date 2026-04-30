import pygame
import random
import sys

pygame.init()

# Window dimensions
WIDTH, HEIGHT = 500, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer")

clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE   = (255, 255, 255)
BLACK   = (0,   0,   0)
GRAY    = (100, 100, 100)
YELLOW  = (255, 215, 0)
RED     = (220, 50,  50)
BLUE    = (50,  100, 220)
GREEN   = (50,  200, 50)

# Road layout
ROAD_LEFT  = 100
ROAD_RIGHT = 400
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT
LANE_WIDTH = ROAD_WIDTH // 3  # three lanes

# Fonts
font_large = pygame.font.SysFont("Arial", 36, bold=True)
font_small = pygame.font.SysFont("Arial", 22)


# ── Helpers ──────────────────────────────────────────────────────────────────

def random_lane_x():
    """Return the centre x of a randomly chosen lane."""
    lane = random.randint(0, 2)
    return ROAD_LEFT + lane * LANE_WIDTH + LANE_WIDTH // 2


# ── Classes ──────────────────────────────────────────────────────────────────

class PlayerCar:
    """The car controlled by the player."""
    WIDTH, HEIGHT = 50, 80

    def __init__(self):
        self.x = WIDTH // 2 - self.WIDTH // 2
        self.y = HEIGHT - 120
        self.speed = 5
        self.rect = pygame.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)

    def draw(self, surface):
        # Car body
        pygame.draw.rect(surface, BLUE, self.rect, border_radius=8)
        # Windshield
        pygame.draw.rect(surface, (180, 220, 255),
                         (self.rect.x + 8, self.rect.y + 10, 34, 20), border_radius=4)
        # Wheels
        for wx, wy in [(self.rect.x - 6, self.rect.y + 8),
                       (self.rect.right, self.rect.y + 8),
                       (self.rect.x - 6, self.rect.bottom - 24),
                       (self.rect.right, self.rect.bottom - 24)]:
            pygame.draw.rect(surface, BLACK, (wx, wy, 10, 16), border_radius=3)

    def move(self, keys):
        if keys[pygame.K_LEFT]  and self.rect.left  > ROAD_LEFT  + 5:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < ROAD_RIGHT - 5:
            self.rect.x += self.speed
        if keys[pygame.K_UP]   and self.rect.top    > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed


class EnemyCar:
    """Oncoming enemy vehicle that scrolls downward."""
    WIDTH, HEIGHT = 50, 80
    COLORS = [RED, GREEN, (180, 90, 200), (200, 140, 30)]

    def __init__(self, scroll_speed):
        self.color = random.choice(self.COLORS)
        self.rect = pygame.Rect(0, -self.HEIGHT, self.WIDTH, self.HEIGHT)
        self.rect.centerx = random_lane_x()
        self.speed = scroll_speed

    def update(self):
        self.rect.y += self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (180, 220, 255),
                         (self.rect.x + 8, self.rect.y + 10, 34, 20), border_radius=4)
        for wx, wy in [(self.rect.x - 6, self.rect.y + 8),
                       (self.rect.right, self.rect.y + 8),
                       (self.rect.x - 6, self.rect.bottom - 24),
                       (self.rect.right, self.rect.bottom - 24)]:
            pygame.draw.rect(surface, BLACK, (wx, wy, 10, 16), border_radius=3)

    def is_off_screen(self):
        return self.rect.top > HEIGHT


class Coin:
    """A collectible coin that appears randomly on the road."""
    RADIUS = 12

    def __init__(self, scroll_speed):
        self.rect = pygame.Rect(0, 0, self.RADIUS * 2, self.RADIUS * 2)
        self.rect.centerx = random_lane_x()
        self.rect.centery = -self.RADIUS
        self.speed = scroll_speed
        self.collected = False

    def update(self):
        self.rect.y += self.speed

    def draw(self, surface):
        if not self.collected:
            pygame.draw.circle(surface, YELLOW, self.rect.center, self.RADIUS)
            pygame.draw.circle(surface, (200, 170, 0), self.rect.center, self.RADIUS, 2)
            # Dollar sign
            label = font_small.render("$", True, BLACK)
            surface.blit(label, label.get_rect(center=self.rect.center))

    def is_off_screen(self):
        return self.rect.top > HEIGHT


class RoadLine:
    """Dashed centre-lane divider line for scrolling road effect."""
    WIDTH, HEIGHT = 10, 60
    GAP = 40

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def update(self, speed):
        self.y += speed
        if self.y > HEIGHT:
            self.y -= self.HEIGHT + self.GAP

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, (self.x, self.y, self.WIDTH, self.HEIGHT))


# ── Game state ────────────────────────────────────────────────────────────────

def create_road_lines():
    """Create dashed lane markers for all three lane borders."""
    lines = []
    # Two dividers between the three lanes
    for i in range(1, 3):
        x = ROAD_LEFT + i * LANE_WIDTH - RoadLine.WIDTH // 2
        y = 0
        while y < HEIGHT:
            lines.append(RoadLine(x, y))
            y += RoadLine.HEIGHT + RoadLine.GAP
    return lines


def draw_road(surface):
    """Draw the static road background."""
    # Grass / side areas
    surface.fill(GREEN)
    # Road
    pygame.draw.rect(surface, GRAY, (ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT))
    # Kerbs
    pygame.draw.rect(surface, WHITE, (ROAD_LEFT - 6, 0, 6, HEIGHT))
    pygame.draw.rect(surface, WHITE, (ROAD_RIGHT, 0, 6, HEIGHT))


def show_text_center(surface, text, font, color, y):
    img = font.render(text, True, color)
    surface.blit(img, img.get_rect(centerx=WIDTH // 2, y=y))


def game_over_screen(surface, score, coins):
    surface.fill(BLACK)
    show_text_center(surface, "GAME OVER", font_large, RED, 220)
    show_text_center(surface, f"Score: {score}", font_small, WHITE, 290)
    show_text_center(surface, f"Coins: {coins}", font_small, YELLOW, 320)
    show_text_center(surface, "Press R to restart or Q to quit", font_small, GRAY, 370)
    pygame.display.flip()


# ── Main loop ─────────────────────────────────────────────────────────────────

def main():
    player = PlayerCar()
    road_lines = create_road_lines()

    scroll_speed   = 5      # initial speed for enemies / coins / road lines
    enemy_cars     = []
    coins          = []
    enemy_timer    = 0
    coin_timer     = 0
    enemy_interval = 90    # frames between enemy spawns
    coin_interval  = 150   # frames between coin spawns
    score          = 0
    coin_count     = 0
    running        = True
    game_over      = False

    while running:
        clock.tick(FPS)

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()   # restart
                    return
                if event.key == pygame.K_q:
                    running = False

        if game_over:
            game_over_screen(screen, score, coin_count)
            continue

        # ── Update ────────────────────────────────────────────────────────────
        keys = pygame.key.get_pressed()
        player.move(keys)

        # Gradually increase difficulty
        score += 1
        if score % 600 == 0:
            scroll_speed += 1
            enemy_interval = max(40, enemy_interval - 5)

        # Update road dashes
        for line in road_lines:
            line.update(scroll_speed)

        # Spawn enemies
        enemy_timer += 1
        if enemy_timer >= enemy_interval:
            enemy_timer = 0
            enemy_cars.append(EnemyCar(scroll_speed))

        # Spawn coins at random intervals
        coin_timer += 1
        if coin_timer >= coin_interval:
            coin_timer = 0
            # Random chance so not every interval produces a coin
            if random.random() < 0.7:
                coins.append(Coin(scroll_speed))

        # Update enemies and check collision
        for car in enemy_cars[:]:
            car.update()
            if car.rect.colliderect(player.rect):
                game_over = True
            if car.is_off_screen():
                enemy_cars.remove(car)

        # Update coins and check collection
        for coin in coins[:]:
            coin.update()
            if not coin.collected and coin.rect.colliderect(player.rect):
                coin.collected = True
                coin_count += 1
                coins.remove(coin)
            elif coin.is_off_screen():
                coins.remove(coin)

        # ── Draw ──────────────────────────────────────────────────────────────
        draw_road(screen)

        for line in road_lines:
            line.draw(screen)
        for car in enemy_cars:
            car.draw(screen)
        for coin in coins:
            coin.draw(screen)
        player.draw(screen)

        # HUD — score (top left)
        score_surf = font_small.render(f"Score: {score // 60}", True, WHITE)
        screen.blit(score_surf, (10, 10))

        # HUD — coin counter (top right)
        coin_surf = font_small.render(f"Coins: {coin_count}", True, YELLOW)
        screen.blit(coin_surf, (WIDTH - coin_surf.get_width() - 10, 10))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
