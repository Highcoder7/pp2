DB_CONFIG = {
    "dbname": "snake_game",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432,
}

CELL = 20
COLS = 30
ROWS = 28
W = COLS * CELL
H = ROWS * CELL + 60   # 60px HUD at bottom
FPS = 10
