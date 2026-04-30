import psycopg2
from psycopg2.extras import execute_batch
from typing import Iterable, Sequence, Tuple, List
from contextlib import contextmanager

import config


def get_connection():
    return psycopg2.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
    )


@contextmanager
def get_cursor(autocommit: bool = True):
    conn = get_connection()
    try:
        conn.autocommit = autocommit
        with conn.cursor() as cur:
            yield cur
    finally:
        conn.close()

