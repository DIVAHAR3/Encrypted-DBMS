# Encrypted Database Management System Using MySQL

A secure Flask-based database management system that encrypts customer data before storing it in MySQL and decrypts it only for authenticated and authorized users.

## Features
- User registration and login
- Password hashing with bcrypt
- Session-based authentication
- Role-based access control for ADMIN, MANAGER, and EMPLOYEE
- AES-256 encryption for customer name, email, phone, and address
- Customer add, view, edit, delete, and search flows
- Audit logging for login, data changes, and decryption activity
- Failed login tracking
- Security dashboard with totals and recent activity
- MySQL schema with stored procedures, triggers, views, and indexes

## Project Structure
- `app/` Flask application package
- `app/routes/` Blueprints for auth, dashboard, customer, and admin flows
- `app/templates/` Bootstrap templates
- `app/static/css/` Custom UI styling
- `sql/` Schema, queries, and database assets
- `docs/` Diagrams and backup/recovery notes
- `report/` IEEE-style report

## Setup
1. Create a MySQL database named `encrypted_dbms`.
2. Copy `.env.example` to `.env` and update the credentials.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create the schema:

```bash
mysql -u root -p < sql/schema.sql
```

5. Start the Flask app:

```bash
python run.py
```

## Environment Variables
- `SECRET_KEY`: Flask session secret
- `ENCRYPTION_SECRET`: Used to derive the AES-256 key
- `DATABASE_URL`: SQLAlchemy MySQL connection string
- `AUTO_CREATE_TABLES`: Set to `1` only for local demos

## Security Notes
- Customer data is encrypted with AES-GCM using a 256-bit key.
- Passwords are hashed with bcrypt and never stored in plaintext.
- MySQL triggers log inserts, updates, and deletes into the audit trail.
- Failed login attempts are stored separately for investigation.
- Search is performed after decryption for authorized users because randomized encryption does not support direct plaintext matching.

## Deliverables
- Complete MySQL schema: `sql/schema.sql`
- Additional SQL queries: `sql/queries.sql`
- ER / DFD / Use Case diagrams: `docs/diagrams.md`
- Backup and recovery notes: `docs/backup_recovery.md`
- IEEE report: `report/IEEE_Project_Report.md`
- PPT outline: `PPT_Content.md`

## Notes for Demo Use
The project is written to be MySQL-first. For quick local testing, set `AUTO_CREATE_TABLES=1`, but in a real deployment the schema should be applied explicitly using the SQL script.
