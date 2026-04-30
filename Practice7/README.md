# Practice 7 - PhoneBook with PostgreSQL

A command-line phonebook application backed by a PostgreSQL database.

## Features

- Import contacts from CSV
- Search contacts by name or phone number
- Add and delete individual contacts
- List all contacts

## Setup

1. Install dependencies:
   ```bash
   pip install psycopg2-binary
   ```

2. Configure your database connection in `config.py`.

3. Run:
   ```bash
   python phonebook.py
   ```

## Files

- `phonebook.py` — Main application logic (CRUD operations)
- `connect.py` — PostgreSQL connection helper
- `config.py` — Database credentials
- `contacts.csv` — Sample contacts data
