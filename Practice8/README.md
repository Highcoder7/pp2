# Practice 8 - PhoneBook with PostgreSQL Functions & Procedures

Extended phonebook that uses PostgreSQL stored functions and procedures.

## Features

- Bulk import with validation via stored procedure
- Search using a PostgreSQL function
- Paginated listing via PostgreSQL function
- Upsert and delete via stored procedures
- Invalid row logging to `invalid_import_rows` table

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

- `phonebook.py` — Python application (calls stored functions/procedures)
- `functions.sql` — PostgreSQL functions (search, pagination, phone validation)
- `procedures.sql` — PostgreSQL stored procedures (upsert, bulk upsert, delete)
- `connect.py` — PostgreSQL connection helper
- `config.py` — Database credentials
