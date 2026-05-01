import os
import random
from collections import deque

import pygame


# ---------------------------------------------------------------------------
# Road layout constants
# ---------------------------------------------------------------------------

ROAD_LEFT  = 150   # left edge of the drivable road (pixels)
ROAD_RIGHT = 650   # right edge of the drivable road (pixels)
LANE_COUNT = 4     # number of lanes
ROAD_W     = ROAD_RIGHT - ROAD_LEFT
LANE_W     = ROAD_W // LANE_COUNT  # width of each individual lane

CAR_W, CAR_H = 40, 70   # collision box dimensions for all cars
POWERUP_SIZE  = 30       # square size of power-up items on the road

# Difficulty presets
DIFF_PARAMS = {
    "easy":   {"base_speed": 4,  "spawn_rate": 120, "obstacle_rate": 200},
    "normal": {"base_speed": 6,  "spawn_rate": 80,  "obstacle_rate": 140},
    "hard":   {"base_speed": 9,  "spawn_rate": 50,  "obstacle_rate": 90},
}

POWERUP_TYPES  = ["nitro", "shield", "repair"]
POWERUP_COLORS = {
    "nitro":  (255, 200, 0),
    "shield": (0, 200, 255),
    "repair": (0, 220, 80),
}

_ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def lane_center(lane):
    """Return the x pixel coordinate of the left edge of a car centred in the given lane."""
    return ROAD_LEFT + lane * LANE_W + LANE_W // 2 - CAR_W // 2


# ---------------------------------------------------------------------------
# Sprite transparency helper
# ---------------------------------------------------------------------------

def _make_transparent_bfs(surf):
    """Remove the checkered/white background using BFS flood fill from corners.
    This preserves white details inside the sprite (like racing stripes) that
    the flood fill cannot reach from outside."""
    w, h = surf.get_size()
    result = pygame.Surface((w, h), pygame.SRCALPHA)

    # Sample the background colours from all four corners
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
        # A pixel is background if it is close (L1 distance) to any sampled corner colour
        is_bg = any(
            abs(pixel[0] - bc[0]) + abs(pixel[1] - bc[1]) + abs(pixel[2] - bc[2]) <= 60
            for bc in bg_samples
        )
        if is_bg:
            transparent.add((x, y))
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                queue.append((x + dx, y + dy))

    # Build the output surface
    for x in range(w):
        for y in range(h):
            if (x, y) in transparent:
                result.set_at((x, y), (0, 0, 0, 0))
            else:
                result.set_at((x, y), surf.get_at((x, y)))
    return result


# ---------------------------------------------------------------------------
# Car sprite (loaded once, cached)
# ---------------------------------------------------------------------------

_car_sprite_cache = None


def get_car_sprite():
    """Load the player car sprite and cache it.  Returns None if the file is missing."""
    global _car_sprite_cache
    if _car_sprite_cache is not None:
        return _car_sprite_cache if _car_sprite_cache is not False else None
    path = os.path.join(_ASSET_DIR, "моя машина.png")
    if os.path.exists(path):
        raw = pygame.image.load(path).convert()
        # Scale to the car collision-box size first, then remove background
        raw = pygame.transform.scale(raw, (CAR_W, CAR_H))
        _car_sprite_cache = _make_transparent_bfs(raw)
    else:
        _car_sprite_cache = False
    return _car_sprite_cache if _car_sprite_cache is not False else None


# ---------------------------------------------------------------------------
# Game objects
# ---------------------------------------------------------------------------

class PlayerCar:
    """The car controlled by the player.  Moves between lanes on key press."""

    def __init__(self, color):
        self.lane   = 1                   # start in the second lane from the left
        self.x      = lane_center(self.lane)
        self.y      = 500                 # fixed vertical position near the bottom
        self.color  = color
        self.shield = False              # True while a shield power-up is active
        self.nitro  = False
        self.nitro_end = 0
        self.slow_end  = 0

    def move(self, direction):
        """Shift one lane left or right, clamped to road boundaries."""
        if direction == "left" and self.lane > 0:
            self.lane -= 1
        elif direction == "right" and self.lane < LANE_COUNT - 1:
            self.lane += 1
        self.x = lane_center(self.lane)

    def rect(self):
        return pygame.Rect(self.x, self.y, CAR_W, CAR_H)

    def draw(self, surface):
        sprite = get_car_sprite()
        if sprite:
            # Draw the pixel-art sprite
            surface.blit(sprite, (self.x, self.y))
        else:
            # Fallback: plain coloured rectangle
            pygame.draw.rect(surface, self.color, self.rect(), border_radius=6)
            pygame.draw.rect(surface, (180, 230, 255),
                             (self.x + 6, self.y + 8, CAR_W - 12, 18), border_radius=3)
        # Cyan shield glow drawn on top of the sprite
        if self.shield:
            pygame.draw.rect(surface, (0, 220, 255), self.rect(), 3, border_radius=6)


class TrafficCar:
    """An oncoming enemy car that scrolls downward.
    Colliding with it ends the run unless the player has a shield."""

    def __init__(self, lane, speed):
        self.lane  = lane
        self.x     = lane_center(lane)
        # Spawn well above the visible screen so the player has time to react
        self.y     = -CAR_H - random.randint(200, 500)
        self.speed = speed
        self.color = random.choice([
            (200, 50, 50), (50, 180, 50), (180, 180, 50), (180, 100, 50)
        ])

    def update(self):
        """Move the car downward each frame."""
        self.y += self.speed

    def rect(self):
        return pygame.Rect(self.x, self.y, CAR_W, CAR_H)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect(), border_radius=6)
        pygame.draw.rect(surface, (180, 230, 255),
                         (self.x + 6, self.y + 8, CAR_W - 12, 18), border_radius=3)


class Obstacle:
    """A road hazard that scrolls downward.
    - barrier / pothole → instant game over on collision
    - oil               → temporary slow-down effect"""

    def __init__(self, lane, speed, kind="barrier"):
        self.lane  = lane
        self.x     = lane_center(lane)
        self.y     = -CAR_H
        self.speed = speed
        self.kind  = kind  # "barrier" | "oil" | "pothole"

    def update(self):
        self.y += self.speed

    def rect(self):
        return pygame.Rect(self.x, self.y, CAR_W, CAR_H // 2)

    def draw(self, surface):
        color = {
            "barrier": (200, 80, 0),
            "oil":     (40, 40, 80),
            "pothole": (80, 60, 40),
        }.get(self.kind, (150, 150, 150))
        pygame.draw.rect(surface, color, self.rect(), border_radius=4)
        lbl = pygame.font.SysFont("Arial", 11).render(
            self.kind[:3].upper(), True, (255, 255, 255)
        )
        surface.blit(lbl, lbl.get_rect(center=self.rect().center))


class Coin:
    """A coin collectible with a point weight.
    value=1 (gold) is common; value=3 (silver) and value=5 (platinum) are rarer.
    Collecting N coins increases enemy speed — higher-value coins accelerate this faster."""

    def __init__(self, lane, speed, value=1):
        self.lane  = lane
        self.x     = lane_center(lane) + CAR_W // 2 - 12
        self.y     = -30
        self.speed = speed
        self.value = value

    def update(self):
        self.y += self.speed

    def rect(self):
        return pygame.Rect(self.x, self.y, 24, 24)

    def draw(self, surface):
        # Gold for common coins, grey for higher-value ones
        color = (255, 215, 0) if self.value == 1 else (200, 200, 200)
        pygame.draw.circle(surface, color, self.rect().center, 12)
        pygame.draw.circle(surface, (180, 150, 0), self.rect().center, 12, 2)


class PowerUp:
    """A temporary collectible granting a special effect.
    Disappears automatically after 8 seconds if not collected."""

    def __init__(self, lane, speed, kind):
        self.lane  = lane
        self.x     = lane_center(lane) + CAR_W // 2 - POWERUP_SIZE // 2
        self.y     = -POWERUP_SIZE
        self.speed = speed
        self.kind  = kind
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        self.y += self.speed

    def rect(self):
        return pygame.Rect(self.x, self.y, POWERUP_SIZE, POWERUP_SIZE)

    def expired(self):
        """Return True if 8 seconds have passed since this power-up spawned."""
        return pygame.time.get_ticks() - self.spawn_time > 8000

    def draw(self, surface):
        color = POWERUP_COLORS.get(self.kind, (200, 200, 200))
        pygame.draw.rect(surface, color, self.rect(), border_radius=6)
        lbl = pygame.font.SysFont("Arial", 10, bold=True).render(
            self.kind[:2].upper(), True, (0, 0, 0)
        )
        surface.blit(lbl, lbl.get_rect(center=self.rect().center))


class NitroStrip:
    """A full-lane speed-boost strip painted on the road."""

    def __init__(self, lane, speed):
        self.lane  = lane
        self.x     = ROAD_LEFT + lane * LANE_W
        self.y     = -20
        self.speed = speed

    def update(self):
        self.y += self.speed

    def rect(self):
        return pygame.Rect(self.x, self.y, LANE_W, 20)

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 80, 0), self.rect())
        lbl = pygame.font.SysFont("Arial", 11).render("NITRO", True, (255, 255, 200))
        surface.blit(lbl, lbl.get_rect(center=self.rect().center))


# ---------------------------------------------------------------------------
# Scrolling road renderer
# ---------------------------------------------------------------------------

class Road:
    """Draws the road surface with animated lane markings.
    The background image (grass + scenery) is handled by main.py;
    this class draws only the grey road rectangle and dashed lane dividers."""

    def __init__(self):
        self.offset = 0   # current scroll offset for lane markings (pixels)
        self.speed  = 6

    def update(self):
        # Advance and wrap the lane-marking scroll offset
        self.offset = (self.offset + self.speed) % 80

    def draw(self, surface, H):
        # Dark grey road surface (covers the centre of the background image)
        pygame.draw.rect(surface, (60, 60, 60), (ROAD_LEFT, 0, ROAD_W, H))

        # Dashed yellow lane dividers, scrolling downward
        for lane in range(1, LANE_COUNT):
            x = ROAD_LEFT + lane * LANE_W
            y = -80 + self.offset
            while y < H:
                pygame.draw.rect(surface, (255, 255, 100), (x - 2, y, 4, 40))
                y += 80

        # White edge lines on each side of the road
        pygame.draw.rect(surface, (255, 255, 255), (ROAD_LEFT,      0, 4, H))
        pygame.draw.rect(surface, (255, 255, 255), (ROAD_RIGHT - 4, 0, 4, H))
