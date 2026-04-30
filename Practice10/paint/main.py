import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")

clock = pygame.time.Clock()
FPS = 60

# ── Layout constants ──────────────────────────────────────────────────────────

TOOLBAR_H   = 60    # height of the top toolbar
CANVAS_TOP  = TOOLBAR_H
CANVAS_RECT = pygame.Rect(0, CANVAS_TOP, WIDTH, HEIGHT - CANVAS_TOP)

# ── Color palette shown in toolbar ───────────────────────────────────────────

PALETTE = [
    (0,   0,   0),      # black
    (255, 255, 255),    # white
    (220, 50,  50),     # red
    (50,  150, 220),    # blue
    (50,  200, 50),     # green
    (255, 215, 0),      # yellow
    (200, 100, 20),     # orange
    (160, 60,  200),    # purple
    (0,   180, 180),    # cyan
    (180, 100, 60),     # brown
    (255, 150, 200),    # pink
    (100, 100, 100),    # gray
]

# Toolbar button dimensions
BTN_W, BTN_H    = 70, 40
SWATCH_SIZE     = 32
SWATCH_MARGIN   = 4
SWATCH_START_X  = 450   # x offset where colour swatches begin

# ── Tools ─────────────────────────────────────────────────────────────────────

TOOL_PEN       = "Pen"
TOOL_LINE      = "Line"
TOOL_RECT      = "Rect"
TOOL_CIRCLE    = "Circle"
TOOL_ERASER    = "Eraser"
TOOLS = [TOOL_PEN, TOOL_LINE, TOOL_RECT, TOOL_CIRCLE, TOOL_ERASER]

# Drawing sizes
PEN_SIZE    = 4
ERASER_SIZE = 24

# Colors
BG_COLOR      = (245, 245, 245)   # canvas background
TOOLBAR_COLOR = (50,  50,  50)
SELECTED_OUTLINE = (0, 200, 255)

font = pygame.font.SysFont("Arial", 16, bold=True)


# ── State ─────────────────────────────────────────────────────────────────────

canvas = pygame.Surface((WIDTH, HEIGHT - CANVAS_TOP))
canvas.fill(BG_COLOR)

current_tool  = TOOL_PEN
current_color = PALETTE[0]   # start with black
drawing       = False
start_pos     = None          # used for shapes that need a start and end point
last_pos      = None          # used for continuous pen/eraser strokes


# ── Helpers ───────────────────────────────────────────────────────────────────

def canvas_pos(screen_pos):
    """Convert a screen position to canvas-relative coordinates."""
    return (screen_pos[0], screen_pos[1] - CANVAS_TOP)


def tool_button_rect(index):
    """Return the Rect for tool button at given index in the toolbar."""
    x = 10 + index * (BTN_W + 6)
    y = (TOOLBAR_H - BTN_H) // 2
    return pygame.Rect(x, y, BTN_W, BTN_H)


def swatch_rect(index):
    """Return the Rect for colour swatch at given index."""
    x = SWATCH_START_X + index * (SWATCH_SIZE + SWATCH_MARGIN)
    y = (TOOLBAR_H - SWATCH_SIZE) // 2
    return pygame.Rect(x, y, SWATCH_SIZE, SWATCH_SIZE)


def draw_toolbar(surface):
    """Render the top toolbar with tool buttons and colour palette."""
    pygame.draw.rect(surface, TOOLBAR_COLOR, (0, 0, WIDTH, TOOLBAR_H))

    # Tool buttons
    for i, tool in enumerate(TOOLS):
        rect  = tool_button_rect(i)
        color = (80, 80, 80) if tool != current_tool else (30, 30, 180)
        pygame.draw.rect(surface, color, rect, border_radius=6)
        if tool == current_tool:
            pygame.draw.rect(surface, SELECTED_OUTLINE, rect, 2, border_radius=6)
        label = font.render(tool, True, (255, 255, 255))
        surface.blit(label, label.get_rect(center=rect.center))

    # Colour swatches
    for i, color in enumerate(PALETTE):
        rect = swatch_rect(i)
        pygame.draw.rect(surface, color, rect, border_radius=4)
        if color == current_color:
            pygame.draw.rect(surface, SELECTED_OUTLINE, rect, 3, border_radius=4)
        else:
            pygame.draw.rect(surface, (20, 20, 20), rect, 1, border_radius=4)

    # Show active colour preview
    preview_rect = pygame.Rect(SWATCH_START_X - 44, (TOOLBAR_H - SWATCH_SIZE) // 2,
                               SWATCH_SIZE, SWATCH_SIZE)
    pygame.draw.rect(surface, current_color, preview_rect, border_radius=4)
    pygame.draw.rect(surface, (200, 200, 200), preview_rect, 2, border_radius=4)


def draw_preview(surface, tool, start, end):
    """Draw a semi-transparent preview of the shape being dragged."""
    if start is None or end is None:
        return
    preview = pygame.Surface((WIDTH, HEIGHT - CANVAS_TOP), pygame.SRCALPHA)
    color_a  = (*current_color, 160)   # transparent

    if tool == TOOL_LINE:
        pygame.draw.line(preview, color_a, start, end, PEN_SIZE)

    elif tool == TOOL_RECT:
        x = min(start[0], end[0])
        y = min(start[1], end[1])
        w = abs(end[0] - start[0])
        h = abs(end[1] - start[1])
        pygame.draw.rect(preview, color_a, (x, y, w, h), 2)

    elif tool == TOOL_CIRCLE:
        cx = (start[0] + end[0]) // 2
        cy = (start[1] + end[1]) // 2
        rx = abs(end[0] - start[0]) // 2
        ry = abs(end[1] - start[1]) // 2
        if rx > 1 and ry > 1:
            # Draw ellipse inscribed in the bounding box
            rect = pygame.Rect(min(start[0], end[0]), min(start[1], end[1]),
                               rx * 2, ry * 2)
            pygame.draw.ellipse(preview, color_a, rect, 2)

    surface.blit(preview, (0, CANVAS_TOP))


# ── Main loop ─────────────────────────────────────────────────────────────────

def main():
    global current_tool, current_color, drawing, start_pos, last_pos

    running = True
    while running:
        clock.tick(FPS)

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # ── Toolbar clicks ────────────────────────────────────────────────
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                # Check tool buttons
                clicked_tool = False
                for i, tool in enumerate(TOOLS):
                    if tool_button_rect(i).collidepoint(mx, my):
                        current_tool  = tool
                        clicked_tool  = True
                        break

                # Check colour swatches
                if not clicked_tool:
                    for i, color in enumerate(PALETTE):
                        if swatch_rect(i).collidepoint(mx, my):
                            current_color = color
                            clicked_tool  = True
                            break

                # Start drawing on canvas
                if not clicked_tool and my > CANVAS_TOP:
                    drawing   = True
                    cp        = canvas_pos(event.pos)
                    start_pos = cp
                    last_pos  = cp

                    # Pen and eraser draw immediately on press
                    if current_tool == TOOL_PEN:
                        pygame.draw.circle(canvas, current_color, cp, PEN_SIZE // 2)
                    elif current_tool == TOOL_ERASER:
                        pygame.draw.circle(canvas, BG_COLOR, cp, ERASER_SIZE // 2)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drawing and start_pos is not None:
                    cp = canvas_pos(event.pos)

                    # Commit shape to canvas on mouse release
                    if current_tool == TOOL_LINE:
                        pygame.draw.line(canvas, current_color, start_pos, cp, PEN_SIZE)

                    elif current_tool == TOOL_RECT:
                        x = min(start_pos[0], cp[0])
                        y = min(start_pos[1], cp[1])
                        w = abs(cp[0] - start_pos[0])
                        h = abs(cp[1] - start_pos[1])
                        pygame.draw.rect(canvas, current_color, (x, y, w, h), 2)

                    elif current_tool == TOOL_CIRCLE:
                        rx = abs(cp[0] - start_pos[0]) // 2
                        ry = abs(cp[1] - start_pos[1]) // 2
                        if rx > 1 and ry > 1:
                            rect = pygame.Rect(min(start_pos[0], cp[0]),
                                               min(start_pos[1], cp[1]),
                                               rx * 2, ry * 2)
                            pygame.draw.ellipse(canvas, current_color, rect, 2)

                drawing   = False
                start_pos = None
                last_pos  = None

            elif event.type == pygame.MOUSEMOTION:
                if drawing:
                    cp = canvas_pos(event.pos)

                    # Continuous stroke for pen and eraser
                    if current_tool == TOOL_PEN and last_pos:
                        pygame.draw.line(canvas, current_color, last_pos, cp, PEN_SIZE)
                    elif current_tool == TOOL_ERASER and last_pos:
                        pygame.draw.line(canvas, BG_COLOR, last_pos, cp, ERASER_SIZE)

                    last_pos = cp

            # Keyboard shortcuts
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p: current_tool = TOOL_PEN
                if event.key == pygame.K_l: current_tool = TOOL_LINE
                if event.key == pygame.K_r: current_tool = TOOL_RECT
                if event.key == pygame.K_c: current_tool = TOOL_CIRCLE
                if event.key == pygame.K_e: current_tool = TOOL_ERASER
                if event.key == pygame.K_DELETE or event.key == pygame.K_n:
                    canvas.fill(BG_COLOR)   # clear canvas

        # ── Draw ──────────────────────────────────────────────────────────────
        screen.blit(canvas, (0, CANVAS_TOP))
        draw_toolbar(screen)

        # Show live preview for shape tools while dragging
        if drawing and current_tool in (TOOL_LINE, TOOL_RECT, TOOL_CIRCLE):
            draw_preview(screen, current_tool, start_pos, canvas_pos(pygame.mouse.get_pos()))

        # Eraser cursor indicator
        if current_tool == TOOL_ERASER:
            mx, my = pygame.mouse.get_pos()
            pygame.draw.circle(screen, (180, 180, 180), (mx, my), ERASER_SIZE // 2, 2)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
