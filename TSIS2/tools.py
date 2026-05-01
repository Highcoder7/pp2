from collections import deque

import pygame


# ---------------------------------------------------------------------------
# Flood fill
# ---------------------------------------------------------------------------

def flood_fill(surface, x, y, fill_color):
    target = surface.get_at((x, y))[:3]
    fill = fill_color[:3]
    if target == fill:
        return
    width, height = surface.get_size()
    queue = deque()
    queue.append((x, y))
    visited = set()
    visited.add((x, y))
    while queue:
        cx, cy = queue.popleft()
        if cx < 0 or cy < 0 or cx >= width or cy >= height:
            continue
        if surface.get_at((cx, cy))[:3] != target:
            continue
        surface.set_at((cx, cy), fill_color)
        for nx, ny in ((cx+1,cy),(cx-1,cy),(cx,cy+1),(cx,cy-1)):
            if (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny))
