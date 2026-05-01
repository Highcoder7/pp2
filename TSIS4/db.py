"""
Database module with automatic fallback.

Priority:
  1. PostgreSQL via psycopg2   – full persistent leaderboard
  2. Local JSON file           – works without a running PostgreSQL server

The rest of the game uses the same function signatures regardless of which
backend is active, so nothing else needs to change.
"""

import json
import os

# --------------------------------------------------------------------------
# JSON fallback storage path (lives next to this file)
# --------------------------------------------------------------------------

_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "leaderboard_local.json")


def _json_load():
    if os.path.exists(_JSON_PATH):
        with open(_JSON_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"players": {}, "sessions": []}


def _json_save(data):
    with open(_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# --------------------------------------------------------------------------
# PostgreSQL probe (runs once at import time)
# --------------------------------------------------------------------------

_USE_DB = False

try:
    import psycopg2
    from config import DB_CONFIG

    # Force ASCII error messages so Cyrillic locale does not break decoding
    os.environ["PGCLIENTENCODING"] = "UTF8"

    def _get_conn():
        return psycopg2.connect(
            **DB_CONFIG,
            options="-c lc_messages=C -c client_encoding=UTF8"
        )

    # Quick connectivity test
    _probe = _get_conn()
    _probe.close()
    _USE_DB = True
    print("DB: PostgreSQL connected.")

except Exception as _err:
    print(f"DB: PostgreSQL unavailable ({_err}). Using local JSON storage.")
    _USE_DB = False


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------

def init_db():
    """Create tables (PostgreSQL) or ensure the JSON file exists."""
    if _USE_DB:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id       SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS game_sessions (
                id            SERIAL PRIMARY KEY,
                player_id     INTEGER REFERENCES players(id),
                score         INTEGER   NOT NULL,
                level_reached INTEGER   NOT NULL,
                played_at     TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
    else:
        # Touch the JSON file so it exists
        if not os.path.exists(_JSON_PATH):
            _json_save({"players": {}, "sessions": []})


def get_or_create_player(username):
    """Return a player identifier (int for PostgreSQL, str for JSON)."""
    if _USE_DB:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id FROM players WHERE username=%s", (username,))
        row = cur.fetchone()
        if row:
            pid = row[0]
        else:
            cur.execute(
                "INSERT INTO players (username) VALUES (%s) RETURNING id",
                (username,)
            )
            pid = cur.fetchone()[0]
            conn.commit()
        cur.close()
        conn.close()
        return pid
    else:
        # In JSON mode the username IS the identifier
        data = _json_load()
        if username not in data["players"]:
            data["players"][username] = username
            _json_save(data)
        return username


def save_session(player_id, score, level):
    """Persist a game result.  Safe to call when player_id is None."""
    if player_id is None:
        return
    if _USE_DB:
        try:
            conn = _get_conn()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO game_sessions (player_id, score, level_reached)"
                " VALUES (%s,%s,%s)",
                (player_id, score, level),
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"DB: save_session failed ({e}), trying JSON fallback.")
            _json_append_session(str(player_id), score, level)
    else:
        _json_append_session(str(player_id), score, level)


def _json_append_session(username, score, level):
    data = _json_load()
    data["sessions"].append({
        "username": username,
        "score": score,
        "level": level,
    })
    _json_save(data)


def get_personal_best(player_id):
    """Return the player's highest score ever, or 0 if none."""
    if player_id is None:
        return 0
    if _USE_DB:
        try:
            conn = _get_conn()
            cur = conn.cursor()
            cur.execute(
                "SELECT MAX(score) FROM game_sessions WHERE player_id=%s",
                (player_id,)
            )
            row = cur.fetchone()
            cur.close()
            conn.close()
            return row[0] or 0
        except Exception:
            pass
    # JSON fallback
    data = _json_load()
    scores = [s["score"] for s in data["sessions"]
              if s["username"] == str(player_id)]
    return max(scores, default=0)


def get_top10():
    """Return top-10 rows as (username, score, level, date_str)."""
    if _USE_DB:
        try:
            conn = _get_conn()
            cur = conn.cursor()
            cur.execute("""
                SELECT p.username, gs.score, gs.level_reached,
                       TO_CHAR(gs.played_at, 'YYYY-MM-DD')
                FROM game_sessions gs
                JOIN players p ON p.id = gs.player_id
                ORDER BY gs.score DESC
                LIMIT 10
            """)
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return rows
        except Exception:
            pass
    # JSON fallback
    data = _json_load()
    sessions = sorted(data["sessions"], key=lambda s: s["score"], reverse=True)
    return [
        (s["username"], s["score"], s["level"], "local")
        for s in sessions[:10]
    ]
