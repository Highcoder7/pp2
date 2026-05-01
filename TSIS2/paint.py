import os
from datetime import datetime

import pygame

from tools import flood_fill

# ---------------------------------------------------------------------------
# Window and canvas layout constants
# ---------------------------------------------------------------------------

WIDTH, HEIGHT = 1100, 700   # total window size
TOOLBAR_W = 200             # width of the left toolbar panel
CANVAS_X = TOOLBAR_W        # canvas starts after the toolbar
CANVAS_W = WIDTH - TOOLBAR_W
CANVAS_H = HEIGHT

FPS = 60  # target frames per second

# Available drawing colors shown as swatches in the toolbar
COLORS = [
    (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 200, 0),
    (0, 0, 255), (255, 165, 0), (255, 255, 0), (128, 0, 128),
    (0, 200, 200), (139, 69, 19), (255, 182, 193), (128, 128, 128),
]

# Three stroke thickness levels: small, medium, large
BRUSH_SIZES = [2, 5, 10]

# All tools available to the user
TOOLS = [
    "pencil", "line", "rectangle", "circle",
    "fill", "text", "eraser",
    "square", "right_triangle", "eq_triangle", "rhombus",
]


# ---------------------------------------------------------------------------
# Shape drawing helpers
# ---------------------------------------------------------------------------

def draw_eq_triangle(surface, color, start, end, width):
    """Draw an equilateral triangle: base is start→end, third vertex computed
    by rotating the base vector 60° around its midpoint."""
    import math
    x1, y1 = start
    x2, y2 = end
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length == 0:
        return
    # Third vertex: perpendicular offset of height = side * sqrt(3)/2
    x3 = x1 + dx / 2 - dy * (3 ** 0.5) / 2
    y3 = y1 + dy / 2 + dx * (3 ** 0.5) / 2
    pygame.draw.polygon(surface, color, [(x1, y1), (x2, y2), (x3, y3)], width)


def draw_rhombus(surface, color, start, end, width):
    """Draw a rhombus (diamond) whose bounding box is start→end.
    The four vertices are the midpoints of each bounding-box side."""
    x1, y1 = start
    x2, y2 = end
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2  # center of bounding box
    pts = [(cx, y1), (x2, cy), (cx, y2), (x1, cy)]
    pygame.draw.polygon(surface, color, pts, width)


def draw_right_triangle(surface, color, start, end, width):
    """Draw a right triangle with the right angle at the top-right corner.
    Vertices: start (top-left), (x2, y1) (top-right/right angle), end (bottom-right)."""
    x1, y1 = start
    x2, y2 = end
    pygame.draw.polygon(surface, color, [(x1, y1), (x2, y1), (x2, y2)], width)


# ---------------------------------------------------------------------------
# Reusable toolbar button widget
# ---------------------------------------------------------------------------

class Button:
    def __init__(self, rect, label, color=(200, 200, 200)):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.color = color

    def draw(self, surface, font, active=False):
        # Highlight active tool with a blue tint
        col = (150, 200, 255) if active else self.color
        pygame.draw.rect(surface, col, self.rect, border_radius=4)
        pygame.draw.rect(surface, (80, 80, 80), self.rect, 1, border_radius=4)
        txt = font.render(self.label, True, (0, 0, 0))
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def hit(self, pos):
        return self.rect.collidepoint(pos)


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Paint")
    clock = pygame.time.Clock()

    # Set application window icon from the assets folder
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "aint.png")
    if os.path.exists(icon_path):
        icon = pygame.image.load(icon_path)
        icon = pygame.transform.scale(icon, (32, 32))
        pygame.display.set_icon(icon)

    # Fonts for toolbar labels and text tool
    font_sm   = pygame.font.SysFont("Arial", 12)
    font_md   = pygame.font.SysFont("Arial", 14)
    font_text = pygame.font.SysFont("Arial", 20)  # used for text-tool rendering

    # The canvas is a separate surface so we can save it independently
    canvas = pygame.Surface((CANVAS_W, CANVAS_H))
    canvas.fill((255, 255, 255))  # white background

    current_tool  = "pencil"
    current_color = (0, 0, 0)
    brush_idx     = 1  # default: medium (index into BRUSH_SIZES)

    drawing   = False   # True while left mouse button is held
    last_pos  = None    # previous mouse position for pencil/eraser
    line_start = None   # anchor point for shapes drawn by drag

    # Text tool state: activated on click, committed on Enter
    text_mode   = False
    text_pos    = None
    text_buffer = ""

    # Snapshot of the canvas taken at mouse-down, used to redraw live previews
    preview = None

    # Build toolbar tool buttons (stacked vertically)
    tool_buttons = []
    labels = {
        "pencil": "Pencil", "line": "Line", "rectangle": "Rect",
        "circle": "Circle", "fill": "Fill", "text": "Text", "eraser": "Eraser",
        "square": "Square", "right_triangle": "R.Tri",
        "eq_triangle": "Eq.Tri", "rhombus": "Rhombus",
    }
    by = 10
    for t in TOOLS:
        tool_buttons.append(Button((5, by, TOOLBAR_W - 10, 24), labels[t]))
        by += 28

    # Brush size buttons: S / M / L mapped to keys 1 / 2 / 3
    size_buttons = [
        Button((5,   by + 10, 55, 22), "S (1)"),
        Button((65,  by + 10, 55, 22), "M (2)"),
        Button((125, by + 10, 55, 22), "L (3)"),
    ]
    by += 40

    # Y position where the color swatch grid starts
    color_swatch_y = by + 10

    def brush_size():
        """Return the current stroke width in pixels."""
        return BRUSH_SIZES[brush_idx]

    def canvas_pos(pos):
        """Convert screen coordinates to canvas-local coordinates."""
        return (pos[0] - CANVAS_X, pos[1])

    def in_canvas(pos):
        """Check whether a screen position is inside the drawing canvas."""
        return pos[0] >= CANVAS_X

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # ---- Keyboard shortcuts ----
            elif event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()

                # Ctrl+S: save canvas as a timestamped PNG file
                if event.key == pygame.K_s and (mods & pygame.KMOD_CTRL):
                    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
                    path = f"canvas_{ts}.png"
                    pygame.image.save(canvas, path)
                    print(f"Saved: {path}")
                    continue

                # Keys 1/2/3 switch brush size
                if event.key == pygame.K_1:
                    brush_idx = 0
                elif event.key == pygame.K_2:
                    brush_idx = 1
                elif event.key == pygame.K_3:
                    brush_idx = 2

                # Text-tool keyboard input while in typing mode
                if text_mode:
                    if event.key == pygame.K_RETURN:
                        # Commit: render typed text permanently onto the canvas
                        if text_buffer:
                            surf = font_text.render(text_buffer, True, current_color)
                            canvas.blit(surf, text_pos)
                        text_mode   = False
                        text_buffer = ""
                        text_pos    = None
                    elif event.key == pygame.K_ESCAPE:
                        # Cancel: discard without drawing
                        text_mode   = False
                        text_buffer = ""
                        text_pos    = None
                    elif event.key == pygame.K_BACKSPACE:
                        text_buffer = text_buffer[:-1]
                    else:
                        if event.unicode and event.unicode.isprintable():
                            text_buffer += event.unicode

            # ---- Mouse button pressed ----
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos

                # Check tool buttons in the toolbar
                for i, btn in enumerate(tool_buttons):
                    if btn.hit(pos):
                        current_tool = TOOLS[i]
                        text_mode = False  # cancel any active text input
                        break

                # Check brush-size buttons
                for i, btn in enumerate(size_buttons):
                    if btn.hit(pos):
                        brush_idx = i
                        break

                # Check color swatches (4-column grid)
                for i, col in enumerate(COLORS):
                    sx = 5 + (i % 4) * 45
                    sy = color_swatch_y + (i // 4) * 30
                    r  = pygame.Rect(sx, sy, 38, 24)
                    if r.collidepoint(pos):
                        current_color = col
                        break

                # Actions on the canvas area
                if in_canvas(pos):
                    cp = canvas_pos(pos)
                    if current_tool == "fill":
                        # Flood-fill the clicked region with the current color
                        flood_fill(canvas, cp[0], cp[1], current_color)
                    elif current_tool == "text":
                        # Enter text-input mode at the clicked position
                        text_mode   = True
                        text_pos    = cp
                        text_buffer = ""
                    elif current_tool in ("line", "rectangle", "circle",
                                         "square", "right_triangle", "eq_triangle", "rhombus"):
                        # Save a snapshot so live preview can be redrawn each frame
                        drawing    = True
                        line_start = cp
                        preview    = canvas.copy()
                    else:
                        # Pencil / eraser: start continuous drawing
                        drawing  = True
                        last_pos = cp

            # ---- Mouse dragged ----
            elif event.type == pygame.MOUSEMOTION:
                if drawing and in_canvas(event.pos):
                    cp = canvas_pos(event.pos)
                    bs = brush_size()

                    if current_tool == "pencil":
                        # Connect previous and current positions for smooth strokes
                        if last_pos:
                            pygame.draw.line(canvas, current_color, last_pos, cp, bs)
                        last_pos = cp

                    elif current_tool == "eraser":
                        # Eraser draws in white with a wider stroke
                        if last_pos:
                            pygame.draw.line(canvas, (255, 255, 255), last_pos, cp, bs * 3)
                        last_pos = cp

                    elif current_tool in ("line", "rectangle", "circle",
                                         "square", "right_triangle", "eq_triangle", "rhombus"):
                        # Restore the snapshot, then draw the live preview on top
                        canvas.blit(preview, (0, 0))
                        _draw_shape(canvas, current_tool, current_color, line_start, cp, bs)

            # ---- Mouse button released ----
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drawing and in_canvas(event.pos):
                    cp = canvas_pos(event.pos)
                    bs = brush_size()
                    if current_tool in ("line", "rectangle", "circle",
                                        "square", "right_triangle", "eq_triangle", "rhombus"):
                        # Restore snapshot and commit the final shape
                        canvas.blit(preview, (0, 0))
                        _draw_shape(canvas, current_tool, current_color, line_start, cp, bs)
                # Reset drag state
                drawing    = False
                last_pos   = None
                line_start = None
                preview    = None

        # ---- Render frame ----
        screen.fill((230, 230, 230))  # window background

        # Draw the canvas on the right side of the window
        screen.blit(canvas, (CANVAS_X, 0))

        # Show live text-cursor preview while typing
        if text_mode and text_pos:
            preview_surf = font_text.render(text_buffer + "|", True, current_color)
            screen.blit(preview_surf, (CANVAS_X + text_pos[0], text_pos[1]))

        # Toolbar panel background
        pygame.draw.rect(screen, (210, 210, 210), (0, 0, TOOLBAR_W, HEIGHT))

        # Draw tool buttons (highlight the active one)
        for i, btn in enumerate(tool_buttons):
            btn.draw(screen, font_sm, active=(TOOLS[i] == current_tool))

        # Draw brush-size buttons (highlight the selected size)
        for i, btn in enumerate(size_buttons):
            btn.draw(screen, font_sm, active=(i == brush_idx))

        # Draw color swatches in a 4-column grid
        for i, col in enumerate(COLORS):
            sx = 5 + (i % 4) * 45
            sy = color_swatch_y + (i // 4) * 30
            r  = pygame.Rect(sx, sy, 38, 24)
            pygame.draw.rect(screen, col, r)
            # Thick border on the currently selected color
            pygame.draw.rect(screen, (0, 0, 0), r, 2 if col == current_color else 1)

        # Show the active color as a solid rectangle below the swatches
        swatch_bottom = color_swatch_y + ((len(COLORS) - 1) // 4 + 1) * 30 + 10
        pygame.draw.rect(screen, current_color, (5, swatch_bottom, TOOLBAR_W - 10, 20))
        pygame.draw.rect(screen, (0, 0, 0),     (5, swatch_bottom, TOOLBAR_W - 10, 20), 1)

        # Keyboard hint at the bottom of the toolbar
        hint = font_sm.render("Ctrl+S = save", True, (80, 80, 80))
        screen.blit(hint, (5, HEIGHT - 20))

        pygame.display.flip()

    pygame.quit()


def _draw_shape(surface, tool, color, start, end, width):
    """Dispatch to the correct drawing function based on the selected tool."""
    x1, y1 = start
    x2, y2 = end

    if tool == "line":
        pygame.draw.line(surface, color, start, end, width)

    elif tool == "rectangle":
        # Normalise so dragging in any direction works correctly
        r = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        pygame.draw.rect(surface, color, r, width)

    elif tool == "circle":
        # Use bounding box centre; radius is the larger half-dimension
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        r = max(abs(x2 - x1) // 2, abs(y2 - y1) // 2)
        pygame.draw.circle(surface, color, (cx, cy), r, width)

    elif tool == "square":
        # Force equal sides by taking the larger of width/height
        side = max(abs(x2 - x1), abs(y2 - y1))
        r = pygame.Rect(x1, y1, side, side)
        pygame.draw.rect(surface, color, r, width)

    elif tool == "right_triangle":
        draw_right_triangle(surface, color, start, end, width)

    elif tool == "eq_triangle":
        draw_eq_triangle(surface, color, start, end, width)

    elif tool == "rhombus":
        draw_rhombus(surface, color, start, end, width)


if __name__ == "__main__":
    main()
