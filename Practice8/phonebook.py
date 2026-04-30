import csv
from pathlib import Path
from typing import List, Tuple

from connect import get_cursor

ROOT = Path(__file__).parent


def install_sql():
    functions_sql = (ROOT / "functions.sql").read_text(encoding="utf-8")
    procedures_sql = (ROOT / "procedures.sql").read_text(encoding="utf-8")
    with get_cursor() as cur:
        cur.execute(functions_sql)
        cur.execute(procedures_sql)


def read_contacts_csv(csv_path: Path) -> Tuple[List[str], List[str]]:
    usernames: List[str] = []
    phones: List[str] = []
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            username = (row.get("username") or "").strip()
            phone = (row.get("phone") or "").strip()
            if not username and not phone:
                continue
            usernames.append(username)
            phones.append(phone)
    return usernames, phones


def bulk_upsert_from_csv(csv_file: Path):
    usernames, phones = read_contacts_csv(csv_file)
    if not usernames:
        print("CSV пустой или не содержит данных.")
        return
    with get_cursor() as cur:
        cur.execute("CALL upsert_many_contacts(%s, %s)", (usernames, phones))
    print(f"Импортировано {len(usernames)} записей (см. invalid_import_rows для ошибок).")


def search(pattern: str):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM get_contacts_by_pattern(%s)", (pattern,))
        rows = cur.fetchall()
    print(f"Поиск по шаблону '{pattern}': {len(rows)} записей")
    for r in rows:
        print(f"- {r[0]}: {r[1]}")


def paginate(limit: int, offset: int):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit, offset))
        rows = cur.fetchall()
    if rows:
        total = rows[0][2]
    else:
        total = 0
    print(f"Пагинация: limit={limit}, offset={offset}, total={total}, returned={len(rows)}")
    for r in rows:
        print(f"- {r[0]}: {r[1]}")


def upsert_one(username: str, phone: str):
    with get_cursor() as cur:
        cur.execute("CALL upsert_contact(%s, %s)", (username, phone))
    print(f"Upsert выполнен: {username} -> {phone}")


def delete_by(username: str = None, phone: str = None):
    with get_cursor() as cur:
        cur.execute("CALL delete_contact(%s, %s)", (username, phone))
    crit = f"username={username}" if username else f"phone={phone}"
    print(f"Удаление по критерию: {crit}")


def show_invalid_imports():
    with get_cursor() as cur:
        cur.execute("SELECT username, phone, reason, reported_at FROM invalid_import_rows ORDER BY id DESC")
        rows = cur.fetchall()
    if not rows:
        print("Ошибок импорта не обнаружено.")
        return
    print("Ошибочные строки импорта:")
    for u, p, reason, ts in rows:
        print(f"- {u} | {p} | {reason} | {ts}")


if __name__ == "__main__":
    install_sql()
    csv_file = ROOT / "contacts.csv"

    # 1) Bulk import
    bulk_upsert_from_csv(csv_file)

    # 2) Поиск по шаблону
    search("Aru")
    search("+7707")

    # 3) Пагинация
    paginate(2, 0)
    paginate(2, 2)

    # 4) Upsert одного контакта
    upsert_one("Aruzhan", "+77070000000")

    # 5) Удаление по username, затем по номеру
    delete_by(username="Madi")
    delete_by(phone="+77071112233")

    # 6) Посмотреть ошибки импорта
    show_invalid_imports()

