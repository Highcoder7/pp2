import csv
from pathlib import Path
from typing import List, Tuple

from connect import get_cursor

ROOT = Path(__file__).parent


def setup_table():
    with get_cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                username VARCHAR(255) PRIMARY KEY,
                phone VARCHAR(32) NOT NULL
            )
        """)


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


def bulk_insert_from_csv(csv_file: Path):
    usernames, phones = read_contacts_csv(csv_file)
    if not usernames:
        print("CSV is empty.")
        return
    with get_cursor() as cur:
        for username, phone in zip(usernames, phones):
            cur.execute(
                "INSERT INTO contacts(username, phone) VALUES (%s, %s) "
                "ON CONFLICT (username) DO UPDATE SET phone = EXCLUDED.phone",
                (username, phone),
            )
    print(f"Imported {len(usernames)} contacts.")


def list_all():
    with get_cursor() as cur:
        cur.execute("SELECT username, phone FROM contacts ORDER BY username")
        rows = cur.fetchall()
    print(f"All contacts ({len(rows)}):")
    for username, phone in rows:
        print(f"  {username}: {phone}")


def search(pattern: str):
    with get_cursor() as cur:
        cur.execute(
            "SELECT username, phone FROM contacts "
            "WHERE username ILIKE %s OR phone ILIKE %s ORDER BY username",
            (f"%{pattern}%", f"%{pattern}%"),
        )
        rows = cur.fetchall()
    print(f"Search '{pattern}': {len(rows)} result(s)")
    for username, phone in rows:
        print(f"  {username}: {phone}")


def add_contact(username: str, phone: str):
    with get_cursor() as cur:
        cur.execute(
            "INSERT INTO contacts(username, phone) VALUES (%s, %s) "
            "ON CONFLICT (username) DO UPDATE SET phone = EXCLUDED.phone",
            (username, phone),
        )
    print(f"Saved: {username} -> {phone}")


def delete_contact(username: str):
    with get_cursor() as cur:
        cur.execute("DELETE FROM contacts WHERE username = %s", (username,))
    print(f"Deleted: {username}")


if __name__ == "__main__":
    setup_table()
    csv_file = ROOT / "contacts.csv"

    bulk_insert_from_csv(csv_file)
    list_all()
    search("Aru")
    add_contact("Bekzat", "+77012345678")
    delete_contact("Madi")
    list_all()
