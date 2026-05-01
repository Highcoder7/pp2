import csv
import json
import os
from datetime import datetime

import psycopg2

from connect import get_connection


# ---------------------------------------------------------------------------
# Schema helpers
# ---------------------------------------------------------------------------

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    schema = open(os.path.join(os.path.dirname(__file__), "schema.sql")).read()
    cur.execute(schema)
    procs = open(os.path.join(os.path.dirname(__file__), "procedures.sql")).read()
    cur.execute(procs)
    conn.commit()
    cur.close()
    conn.close()


# ---------------------------------------------------------------------------
# Core CRUD
# ---------------------------------------------------------------------------

def add_contact(name, email=None, birthday=None, group_name=None):
    conn = get_connection()
    cur = conn.cursor()
    group_id = _resolve_group(cur, group_name)
    cur.execute(
        "INSERT INTO contacts (name, email, birthday, group_id) VALUES (%s,%s,%s,%s) RETURNING id",
        (name, email, birthday, group_id),
    )
    contact_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return contact_id


def _resolve_group(cur, group_name):
    if not group_name:
        return None
    cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (group_name,))
    return cur.fetchone()[0]


def add_phone_to_contact(contact_name, phone, phone_type="mobile"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CALL add_phone(%s, %s, %s)", (contact_name, phone, phone_type))
    conn.commit()
    cur.close()
    conn.close()


def update_contact(contact_id, name=None, email=None, birthday=None):
    conn = get_connection()
    cur = conn.cursor()
    if name:
        cur.execute("UPDATE contacts SET name=%s WHERE id=%s", (name, contact_id))
    if email:
        cur.execute("UPDATE contacts SET email=%s WHERE id=%s", (email, contact_id))
    if birthday:
        cur.execute("UPDATE contacts SET birthday=%s WHERE id=%s", (birthday, contact_id))
    conn.commit()
    cur.close()
    conn.close()


def delete_contact(contact_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM contacts WHERE id=%s", (contact_id,))
    conn.commit()
    cur.close()
    conn.close()


# ---------------------------------------------------------------------------
# Search / filter
# ---------------------------------------------------------------------------

def search_contacts(query):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM search_contacts(%s)", (query,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def filter_by_group(group_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT c.id, c.name, c.email, c.birthday, g.name
           FROM contacts c
           LEFT JOIN groups g ON g.id = c.group_id
           WHERE g.name = %s ORDER BY c.name""",
        (group_name,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def search_by_email(fragment):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT c.id, c.name, c.email, c.birthday, g.name
           FROM contacts c
           LEFT JOIN groups g ON g.id = c.group_id
           WHERE c.email ILIKE %s ORDER BY c.name""",
        (f"%{fragment}%",),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def list_contacts(sort_by="name"):
    valid = {"name": "c.name", "birthday": "c.birthday", "date": "c.created_at"}
    order = valid.get(sort_by, "c.name")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        f"""SELECT c.id, c.name, c.email, c.birthday, g.name
            FROM contacts c LEFT JOIN groups g ON g.id = c.group_id
            ORDER BY {order}"""
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_phones(contact_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT phone, type FROM phones WHERE contact_id=%s", (contact_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------

def get_page(limit=5, offset=0):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM get_contacts_page(%s, %s)", (limit, offset))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def count_contacts():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM contacts")
    n = cur.fetchone()[0]
    cur.close()
    conn.close()
    return n


# ---------------------------------------------------------------------------
# Import / Export
# ---------------------------------------------------------------------------

def export_json(filepath="contacts_export.json"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT c.id, c.name, c.email,
                  TO_CHAR(c.birthday,'YYYY-MM-DD'), g.name
           FROM contacts c LEFT JOIN groups g ON g.id = c.group_id
           ORDER BY c.name"""
    )
    contacts = []
    for cid, name, email, bday, grp in cur.fetchall():
        cur2 = conn.cursor()
        cur2.execute("SELECT phone, type FROM phones WHERE contact_id=%s", (cid,))
        phones = [{"phone": p, "type": t} for p, t in cur2.fetchall()]
        cur2.close()
        contacts.append(
            {"name": name, "email": email, "birthday": bday, "group": grp, "phones": phones}
        )
    cur.close()
    conn.close()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)
    print(f"Exported {len(contacts)} contacts to {filepath}")


def import_json(filepath="contacts_export.json"):
    with open(filepath, encoding="utf-8") as f:
        contacts = json.load(f)
    conn = get_connection()
    cur = conn.cursor()
    for c in contacts:
        cur.execute("SELECT id FROM contacts WHERE name=%s", (c["name"],))
        existing = cur.fetchone()
        if existing:
            choice = input(f'Duplicate: "{c["name"]}". Skip or overwrite? [s/o]: ').strip().lower()
            if choice != "o":
                continue
            cur.execute("DELETE FROM contacts WHERE id=%s", (existing[0],))
        group_id = _resolve_group(cur, c.get("group"))
        cur.execute(
            "INSERT INTO contacts (name, email, birthday, group_id) VALUES (%s,%s,%s,%s) RETURNING id",
            (c["name"], c.get("email"), c.get("birthday"), group_id),
        )
        cid = cur.fetchone()[0]
        for ph in c.get("phones", []):
            cur.execute(
                "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                (cid, ph["phone"], ph.get("type", "mobile")),
            )
    conn.commit()
    cur.close()
    conn.close()
    print(f"Imported {len(contacts)} contacts from {filepath}")


def import_csv(filepath="contacts.csv"):
    conn = get_connection()
    cur = conn.cursor()
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            cur.execute("SELECT id FROM contacts WHERE name = %s AND email IS NOT DISTINCT FROM %s LIMIT 1",
                        (row["name"], row.get("email")))
            existing = cur.fetchone()
            if existing:
                continue
            group_id = _resolve_group(cur, row.get("group"))
            cur.execute(
                """INSERT INTO contacts (name, email, birthday, group_id)
                   VALUES (%s,%s,%s,%s) RETURNING id""",
                (row["name"], row.get("email"), row.get("birthday") or None, group_id),
            )
            result = cur.fetchone()
            if result and row.get("phone"):
                cur.execute(
                    "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                    (result[0], row["phone"], row.get("phone_type", "mobile")),
                )
                count += 1
    conn.commit()
    cur.close()
    conn.close()
    print(f"CSV import done: {count} new contacts")


# ---------------------------------------------------------------------------
# Console UI
# ---------------------------------------------------------------------------

def print_contacts(rows):
    if not rows:
        print("  (no results)")
        return
    print(f"{'ID':<5} {'Name':<20} {'Email':<25} {'Birthday':<12} {'Group':<10}")
    print("-" * 75)
    for row in rows:
        cid, name, email, bday, grp = row
        print(f"{cid:<5} {str(name):<20} {str(email or ''):<25} {str(bday or ''):<12} {str(grp or ''):<10}")


def paginated_view():
    page_size = 5
    offset = 0
    total = count_contacts()
    while True:
        rows = get_page(page_size, offset)
        print(f"\n--- Page {offset // page_size + 1} (contacts {offset+1}-{min(offset+page_size, total)} of {total}) ---")
        print_contacts(rows)
        cmd = input("[ next | prev | quit ]: ").strip().lower()
        if cmd == "next":
            if offset + page_size < total:
                offset += page_size
            else:
                print("Already on last page.")
        elif cmd == "prev":
            if offset - page_size >= 0:
                offset -= page_size
            else:
                print("Already on first page.")
        elif cmd == "quit":
            break


def menu():
    init_db()
    print("=== PhoneBook ===")
    while True:
        print("""
1. Add contact
2. Add phone to contact
3. Search (name/email/phone)
4. Filter by group
5. Search by email
6. List all (sort by name/birthday/date)
7. Paginated view
8. Update contact
9. Delete contact
10. Export to JSON
11. Import from JSON
12. Import from CSV
13. Move contact to group
0. Exit
""")
        choice = input("Choose: ").strip()

        if choice == "1":
            name = input("Name: ").strip()
            email = input("Email (optional): ").strip() or None
            bday = input("Birthday YYYY-MM-DD (optional): ").strip() or None
            grp = input("Group (Family/Work/Friend/Other): ").strip() or None
            cid = add_contact(name, email, bday, grp)
            phone = input("Phone (optional): ").strip()
            if phone:
                ptype = (input("Type (home/work/mobile): ").strip() or "mobile").lower()
                add_phone_to_contact(name, phone, ptype)
            print(f"Added contact ID={cid}")

        elif choice == "2":
            name = input("Contact name: ").strip()
            phone = input("Phone: ").strip()
            ptype = (input("Type (home/work/mobile): ").strip() or "mobile").lower()
            add_phone_to_contact(name, phone, ptype)
            print("Phone added.")

        elif choice == "3":
            q = input("Search query: ").strip()
            print_contacts(search_contacts(q))

        elif choice == "4":
            grp = input("Group name: ").strip()
            print_contacts(filter_by_group(grp))

        elif choice == "5":
            fragment = input("Email fragment: ").strip()
            print_contacts(search_by_email(fragment))

        elif choice == "6":
            sort = input("Sort by (name/birthday/date): ").strip() or "name"
            print_contacts(list_contacts(sort))

        elif choice == "7":
            paginated_view()

        elif choice == "8":
            cid = int(input("Contact ID: ").strip())
            name = input("New name (blank=skip): ").strip() or None
            email = input("New email (blank=skip): ").strip() or None
            bday = input("New birthday YYYY-MM-DD (blank=skip): ").strip() or None
            update_contact(cid, name, email, bday)
            print("Updated.")

        elif choice == "9":
            cid = int(input("Contact ID to delete: ").strip())
            delete_contact(cid)
            print("Deleted.")

        elif choice == "10":
            path = input("Export file path [contacts_export.json]: ").strip() or "contacts_export.json"
            export_json(path)

        elif choice == "11":
            path = input("Import JSON file path [contacts_export.json]: ").strip() or "contacts_export.json"
            import_json(path)

        elif choice == "12":
            path = input("CSV file path [contacts.csv]: ").strip() or "contacts.csv"
            import_csv(path)

        elif choice == "13":
            name = input("Contact name: ").strip()
            grp = input("Group name: ").strip()
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("CALL move_to_group(%s, %s)", (name, grp))
            conn.commit()
            cur.close()
            conn.close()
            print("Moved.")

        elif choice == "0":
            break


if __name__ == "__main__":
    menu()
