import os
import random
from collections import deque

import pygame
from config import CELL, COLS, ROWS


# ---------------------------------------------------------------------------
# Direction vectors (grid steps)
# ---------------------------------------------------------------------------

UP    = (0, -1)
DOWN  = (0,  1)
LEFT  = (-1, 0)
RIGHT = (1,  0)
OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}

_ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


# ---------------------------------------------------------------------------
# Sprite transparency helper
# ---------------------------------------------------------------------------

def _make_transparent_bfs(surf):
    """Remove the checkered/white background using BFS flood fill from all four
    corners.  Preserves internal white/light details (e.g. snowflake crystals)
    that the flood fill cannot reach from outside the sprite boundary."""
    w, h = surf.get_size()
    result = pygame.Surface((w, h), pygame.SRCALPHA)

    # Sample background colour from each corner
    bg_samples = set()
    for cx, cy in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        bg_samples.add(surf.get_at((cx, cy))[:3])

    transparent = set()
    queue = deque([(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)])

    while queue:
        x, y = queue.popleft()
        if (x, y) in transparent or not (0 <= x < w and 0 <= y < h):
            continue
        pixel = surf.get_at((x, y))[:3]
        # Mark as background if close (L1 distance ≤ 60) to any corner colour
        is_bg = any(
            abs(pixel[0] - bc[0]) + abs(pixel[1] - bc[1]) + abs(pixel[2] - bc[2]) <= 60
            for bc in bg_samples
        )
        if is_bg:
            transparent.add((x, y))
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                queue.append((x + dx, y + dy))

    for x in range(w):
        for y in range(h):
            if (x, y) in transparent:
                result.set_at((x, y), (0, 0, 0, 0))
            else:
                result.set_at((x, y), surf.get_at((x, y)))
    return result


# ---------------------------------------------------------------------------
# Food sprite sheet loader
# ---------------------------------------------------------------------------

_food_sprites: dict | None = None  # cached after first load


def get_food_sprites():
    """Load and cache food sprites from the sprite sheet.
    Returns a dict mapping kind → Surface, or None if asset is missing."""
    global _food_sprites
    if _food_sprites is not None:
        return _food_sprites if _food_sprites else None

    path = os.path.join(_ASSET_DIR, "еда.png")
    if not os.path.exists(path):
        _food_sprites = {}  # empty = unavailable
        return None

    sheet = pygame.image.load(path).convert()
    item_w = sheet.get_width() // 4   # sprite sheet has 4 items in a row
    item_h = sheet.get_height()
    size   = CELL - 1                 # fit exactly inside one grid cell

    # Order in the sprite sheet: apple, coin, mushroom, snowflake
    # Mapping to food kinds: normal, gold, poison, disappear
    kinds = ["normal", "gold", "poison", "disappear"]
    sprites = {}
    for i, kind in enumerate(kinds):
        sub  = sheet.subsurface(pygame.Rect(i * item_w, 0, item_w, item_h))
        sub  = pygame.transform.scale(sub, (size, size))
        sprites[kind] = _make_transparent_bfs(sub)

    _food_sprites = sprites
    return _food_sprites


# ---------------------------------------------------------------------------
# Snake
# ---------------------------------------------------------------------------

class Snake:
    """Player-controlled snake.  Body is a list of (col, row) grid positions;
    index 0 is the head."""

    def __init__(self, color):
        self.body      = [(COLS // 2, ROWS // 2), (COLS // 2 - 1, ROWS // 2)]
        self.direction = RIGHT
        self.color     = color
        self.grew      = False  # flag consumed by move()

    def change_dir(self, new_dir):
        """Change direction, ignoring 180° reversals."""
        if new_dir != OPPOSITE.get(self.direction):
            self.direction = new_dir

    def move(self):
        """Advance the snake one cell.  Keeps tail if grew flag is set."""
        hx, hy   = self.body[0]
        dx, dy   = self.direction
        new_head = (hx + dx, hy + dy)
        self.body.insert(0, new_head)
        if not self.grew:
            self.body.pop()
        else:
            self.grew = False

    def grow(self, n=1):
        """Schedule n segments of growth on the next move."""
        for _ in range(n):
            self.grew = True

    def shrink(self, n=2):
        """Remove n tail segments (used by poison food)."""
        for _ in range(n):
            if len(self.body) > 1:
                self.body.pop()

    @property
    def head(self):
        return self.body[0]

    def collides_wall(self):
        hx, hy = self.head
        return hx < 0 or hy < 0 or hx >= COLS or hy >= ROWS

    def collides_self(self):
        return self.head in self.body[1:]

    def collides_obstacles(self, blocks):
        return self.head in blocks

    def draw(self, surface):
        # Draw body with a gradient shade fading toward the tail
        for i, (x, y) in enumerate(self.body):
            r     = pygame.Rect(x * CELL, y * CELL, CELL - 1, CELL - 1)
            shade = max(30, self.color[1] - i * 3)
            color = (self.color[0], shade, self.color[2])
            pygame.draw.rect(surface, color, r, border_radius=3)
        # Eye on the head
        hx, hy = self.head
        pygame.draw.circle(surface, (0, 0, 0),
                           (hx * CELL + CELL - 5, hy * CELL + 5), 3)


# ---------------------------------------------------------------------------
# Food items
# ---------------------------------------------------------------------------

class Food:
    """A food item the snake can eat.

    Kinds and their point weights (randomly generated, different weights):
      normal    → 1 pt  – always present, never disappears
      gold      → 3 pts – higher reward, spawned randomly
      disappear → 2 pts – spawns with a TTL; vanishes if not eaten in time
      poison    → 0 pts – shortens the snake by 2 segments on contact
    """

    def __init__(self, kind="normal"):
        self.kind       = kind
        self.pos        = None
        self.spawn_tick = 0
        self.ttl        = None  # milliseconds before vanishing; None = never

    def place(self, forbidden, now_ms):
        """Place at a random cell not in the forbidden set."""
        occupied = set(forbidden)
        while True:
            pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
            if pos not in occupied:
                self.pos        = pos
                self.spawn_tick = now_ms
                break

    def expired(self, now_ms):
        """Return True if the item has exceeded its time-to-live."""
        if self.ttl is None:
            return False
        return now_ms - self.spawn_tick > self.ttl

    @property
    def points(self):
        return {"normal": 1, "gold": 3, "poison": 0, "disappear": 2}.get(self.kind, 1)

    @property
    def fallback_color(self):
        """Colour used when the sprite asset is unavailable."""
        return {
            "normal":    (220, 50,  50),
            "gold":      (255, 215,  0),
            "poison":    (100,  0,  20),
            "disappear": (50,  200, 200),
        }.get(self.kind, (200, 200, 200))

    def draw(self, surface):
        if not self.pos:
            return
        x, y = self.pos
        r = pygame.Rect(x * CELL, y * CELL, CELL - 1, CELL - 1)

        sprites = get_food_sprites()
        if sprites and self.kind in sprites:
            # Draw the pixel-art sprite from the sprite sheet
            surface.blit(sprites[self.kind], r.topleft)
        else:
            # Fallback: coloured rectangle
            pygame.draw.rect(surface, self.fallback_color, r, border_radius=4)
            if self.kind == "poison":
                pygame.draw.rect(surface, (200, 0, 50), r, 2, border_radius=4)


# ---------------------------------------------------------------------------
# Power-ups
# ---------------------------------------------------------------------------

POWERUP_COLORS = {
    "speed":  (255, 200,   0),
    "slow":   (100, 100, 255),
    "shield": (0,   200, 255),
}


class PowerUpItem:
    """A collectible granting a temporary effect.
    - speed  → faster snake for 5 s
    - slow   → slower snake for 5 s
    - shield → absorbs the next fatal collision
    Disappears from the field after 8 seconds if not collected."""

    def __init__(self, kind, pos, now_ms):
        self.kind       = kind
        self.pos        = pos
        self.spawn_tick = now_ms

    def expired(self, now_ms):
        return now_ms - self.spawn_tick > 8000

    def draw(self, surface):
        x, y = self.pos
        r    = pygame.Rect(x * CELL, y * CELL, CELL - 1, CELL - 1)
        pygame.draw.rect(surface, POWERUP_COLORS.get(self.kind, (200, 200, 200)),
                         r, border_radius=5)
        font = pygame.font.SysFont("Arial", 9, bold=True)
        lbl  = font.render(self.kind[:2].upper(), True, (0, 0, 0))
        surface.blit(lbl, lbl.get_rect(center=r.center))


# ---------------------------------------------------------------------------
# Obstacles (from Level 3 onwards)
# ---------------------------------------------------------------------------

def generate_obstacles(level, snake_body):
    """Place wall blocks for the current level.
    A 7×7 safe zone around the snake head is always kept clear."""
    count     = (level - 3) * 3 + 4
    blocks    = set()
    forbidden = set(snake_body)
    hx, hy    = snake_body[0]
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            forbidden.add((hx + dx, hy + dy))
    attempts = 0
    while len(blocks) < count and attempts < 1000:
        pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
        if pos not in forbidden:
            blocks.add(pos)
        attempts += 1
    return blocks


def draw_obstacles(surface, blocks):
    """Draw obstacle blocks as brown bricks."""
    for (x, y) in blocks:
        r = pygame.Rect(x * CELL, y * CELL, CELL - 1, CELL - 1)
        pygame.draw.rect(surface, (130, 90, 40), r)
        pygame.draw.rect(surface, (90, 60, 20),  r, 2)


# ---------------------------------------------------------------------------
# Grid overlay and background
# ---------------------------------------------------------------------------

_bg_surf_cache = None  # cached background surface


def get_bg_surf(w, h):
    """Load (once) and return the game-field background image scaled to w×h."""
    global _bg_surf_cache
    if _bg_surf_cache is not None:
        return _bg_surf_cache if _bg_surf_cache is not False else None
    path = os.path.join(_ASSET_DIR, "поле.png")
    if os.path.exists(path):
        raw = pygame.image.load(path).convert()
        _bg_surf_cache = pygame.transform.scale(raw, (w, h))
    else:
        _bg_surf_cache = False
    return _bg_surf_cache if _bg_surf_cache is not False else None


def draw_grid(surface):
    """Draw thin grid lines between every cell (optional overlay)."""
    for x in range(COLS):
        pygame.draw.line(surface, (40, 40, 40),
                         (x * CELL, 0), (x * CELL, ROWS * CELL))
    for y in range(ROWS):
        pygame.draw.line(surface, (40, 40, 40),
                         (0, y * CELL), (COLS * CELL, y * CELL))
