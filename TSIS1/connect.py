import psycopg2
from config import DB_CONFIG


def get_connection():
    return psycopg2.connect(**DB_CONFIG, options="-c lc_messages=C -c client_encoding=UTF8")
