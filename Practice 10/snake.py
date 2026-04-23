import pygame
import random
import sys

pygame.init()

# Cell and grid size
CELL  = 20
COLS  = 30
ROWS  = 30
WIDTH  = CELL * COLS
HEIGHT = CELL * ROWS + 50   # extra strip for HUD

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")

clock = pygame.time.Clock()

# Colors
BLACK      = (0,   0,   0)
DARK_GREEN = (0,   120, 0)
LIGHT_GREEN= (0,   200, 0)
RED        = (220, 50,  50)
WHITE      = (255, 255, 255)
YELLOW     = (255, 215, 0)
GRAY       = (40,  40,  40)
WALL_COLOR = (80,  80,  80)

# Directions
UP    = (0, -1)
DOWN  = (0,  1)
LEFT  = (-1, 0)
RIGHT = (1,  0)

font_hud   = pygame.font.SysFont("Arial", 22, bold=True)
font_large = pygame.font.SysFont("Arial", 40, bold=True)
font_small = pygame.font.SysFont("Arial", 24)

# Foods needed to advance to next level
FOODS_PER_LEVEL = 3
BASE_SPEED      = 8    # frames per second at level 1
SPEED_INCREMENT = 2    # extra fps per level


# ── Wall layout ───────────────────────────────────────────────────────────────

def build_walls():
    """Return a set of (col, row) tuples representing border walls."""
    walls = set()
    for c in range(COLS):
        walls.add((c, 0))
        walls.add((c, ROWS - 1))
    for r in range(ROWS):
        walls.add((0, r))
        walls.add((COLS - 1, r))
    return walls


# ── Food placement ────────────────────────────────────────────────────────────

def random_food(snake_body, walls):
    """Choose a random cell that is not occupied by the snake or walls."""
    free = [
        (c, r)
        for c in range(1, COLS - 1)
        for r in range(1, ROWS - 1)
        if (c, r) not in snake_body and (c, r) not in walls
    ]
    return random.choice(free) if free else None


# ── Drawing helpers ───────────────────────────────────────────────────────────

def draw_cell(surface, col, row, color, border_radius=4):
    rect = pygame.Rect(col * CELL + 1, row * CELL + 1, CELL - 2, CELL - 2)
    pygame.draw.rect(surface, color, rect, border_radius=border_radius)


def draw_game(surface, snake, food, walls, score, level):
    surface.fill(BLACK)

    # Grid background
    for c in range(COLS):
        for r in range(ROWS):
            pygame.draw.rect(surface, GRAY,
                             (c * CELL, r * CELL, CELL, CELL), 1)

    # Walls
    for (c, r) in walls:
        draw_cell(surface, c, r, WALL_COLOR, border_radius=0)

    # Food
    if food:
        draw_cell(surface, food[0], food[1], RED, border_radius=CELL // 2)

    # Snake body (lighter shade) then head (darker)
    for i, (c, r) in enumerate(snake):
        color = DARK_GREEN if i == 0 else LIGHT_GREEN
        draw_cell(surface, c, r, color)

    # HUD bar below the grid
    hud_y = ROWS * CELL
    pygame.draw.rect(surface, (20, 20, 20), (0, hud_y, WIDTH, 50))
    score_surf = font_hud.render(f"Score: {score}", True, WHITE)
    level_surf = font_hud.render(f"Level: {level}", True, YELLOW)
    surface.blit(score_surf, (10, hud_y + 12))
    surface.blit(level_surf, (WIDTH - level_surf.get_width() - 10, hud_y + 12))


def show_centered(surface, text, font, color, y):
    img = font.render(text, True, color)
    surface.blit(img, img.get_rect(centerx=WIDTH // 2, y=y))


def message_screen(surface, title, subtitle, color=RED):
    surface.fill(BLACK)
    show_centered(surface, title,    font_large, color,  HEIGHT // 2 - 60)
    show_centered(surface, subtitle, font_small, WHITE,  HEIGHT // 2)
    pygame.display.flip()
    wait_for_key()


def wait_for_key():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                return


# ── Main game ─────────────────────────────────────────────────────────────────

def main():
    walls = build_walls()

    # Initial snake: three cells in the middle, moving right
    mid_c, mid_r = COLS // 2, ROWS // 2
    snake   = [(mid_c, mid_r), (mid_c - 1, mid_r), (mid_c - 2, mid_r)]
    direction = RIGHT
    pending   = RIGHT   # buffer for the next direction change

    food  = random_food(set(snake), walls)
    score = 0
    level = 1
    foods_eaten   = 0      # count within current level
    speed = BASE_SPEED

    running = True
    while running:
        clock.tick(speed)

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                # Prevent reversing into yourself
                if event.key == pygame.K_UP    and direction != DOWN:
                    pending = UP
                elif event.key == pygame.K_DOWN  and direction != UP:
                    pending = DOWN
                elif event.key == pygame.K_LEFT  and direction != RIGHT:
                    pending = LEFT
                elif event.key == pygame.K_RIGHT and direction != LEFT:
                    pending = RIGHT
                elif event.key == pygame.K_ESCAPE:
                    running = False

        direction = pending

        # ── Move snake ────────────────────────────────────────────────────────
        head_c, head_r = snake[0]
        new_head = (head_c + direction[0], head_r + direction[1])

        # Wall collision
        if new_head in walls:
            message_screen(screen, "GAME OVER",
                           f"Score: {score}  Level: {level}  — Press any key")
            main(); return

        # Self collision
        if new_head in snake:
            message_screen(screen, "GAME OVER",
                           f"Score: {score}  Level: {level}  — Press any key")
            main(); return

        snake.insert(0, new_head)

        # Check food collection
        if new_head == food:
            score        += 10 * level   # more points on higher levels
            foods_eaten  += 1

            # Level up when enough foods have been eaten
            if foods_eaten >= FOODS_PER_LEVEL:
                foods_eaten = 0
                level      += 1
                speed       = BASE_SPEED + (level - 1) * SPEED_INCREMENT
                message_screen(screen,
                               f"Level {level}!",
                               "Speed increased — Press any key",
                               YELLOW)

            food = random_food(set(snake), walls)
            if food is None:
                # No free cell — player wins
                message_screen(screen, "YOU WIN!",
                               f"Final Score: {score} — Press any key",
                               LIGHT_GREEN)
                main(); return
        else:
            # Remove tail only when no food was eaten (normal movement)
            snake.pop()

        # ── Draw ──────────────────────────────────────────────────────────────
        draw_game(screen, snake, food, walls, score, level)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
