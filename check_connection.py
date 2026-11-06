"""Checks the connection between LibraryHub and MySQL and says, in plain English, what is wrong.
Run it in the project folder:   python check_connection.py"""
import getpass
import os
import sys

try:
    import mysql.connector
except ImportError:
    print("The MySQL connector is not installed. Run:  python -m pip install -r requirements.txt")
    sys.exit(1)

EXPECTED = {
    "tbl_users": ["userID", "username", "password", "role", "fullName"],
    "tbl_students": ["studentID", "fullName", "grade", "section", "contactNumber", "dateRegistered", "password"],
    "tbl_category": ["categoryID", "categoryName"],
    "tbl_books": ["bookID", "accessionNumber", "title", "author", "barcode", "isbn",
                  "availabilityStatus", "shelfLocation", "categoryID"],
    "tbl_borrow": ["transactionID", "studentID", "bookID", "userID", "borrowDate", "dueDate", "returnStatus"],
    "tbl_return": ["transactionID", "returnDate", "fineAmount", "condition"],
    "tbl_notifications": ["message", "studentID", "bookID", "isRead", "dateCreated"],
}

HINTS = {
    1045: "WRONG PASSWORD (or username). Use the same password you type to open the connection in MySQL Workbench.",
    2003: "MySQL IS NOT RUNNING. Press Win+R, type services.msc, find MySQL80, right-click it and choose Start.",
    2002: "MySQL IS NOT RUNNING. Press Win+R, type services.msc, find MySQL80, right-click it and choose Start.",
    1049: "THE DATABASE DOES NOT EXIST on this server. Run create_database.sql in MySQL Workbench.",
    2059: "LOGIN METHOD NOT SUPPORTED. Run:  python -m pip install --upgrade mysql-connector-python",
}


def fail(prefix, e):
    print(f"\nPROBLEM: {prefix}")
    print("  ->", HINTS.get(getattr(e, "errno", None), "Unexpected error. Send this line to your helper: " + str(e)))
    sys.exit(1)


host = os.environ.get("LIBRARY_DB_HOST", "localhost")
dbname = os.environ.get("LIBRARY_DB_NAME", "library_management_db")
user = os.environ.get("LIBRARY_DB_USER") or input("MySQL username [press Enter for root]: ").strip() or "root"
pw = os.environ.get("LIBRARY_DB_PASSWORD")
if pw is None:
    pw = getpass.getpass("MySQL password (nothing shows while you type): ")

print(f"\n1. Connecting to MySQL on {host} as '{user}' ...")
try:
    server = mysql.connector.connect(host=host, user=user, password=pw)
except mysql.connector.Error as e:
    fail("could not log in to MySQL.", e)
print("   OK - MySQL accepted the login.")

print(f"2. Looking for the database '{dbname}' ...")
cur = server.cursor()
cur.execute("SHOW DATABASES")
names = [r[0] for r in cur.fetchall()]
if dbname not in names:
    print(f"\nPROBLEM: '{dbname}' is not on this server. Databases found: {', '.join(names)}")
    print("  -> Run create_database.sql in MySQL Workbench (File > New Query Tab, paste it, click the lightning bolt).")
    sys.exit(1)
print("   OK - the database exists.")

print("3. Checking the tables and columns the system needs ...")
cur.execute("SELECT TABLE_NAME, COLUMN_NAME, CHARACTER_MAXIMUM_LENGTH FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA=%s", (dbname,))
have, widths = {}, {}
for t, c, w in cur.fetchall():
    have.setdefault(t.lower(), set()).add(c.lower())
    widths[(t.lower(), c.lower())] = w
problems = []
for table, cols in EXPECTED.items():
    if table not in have:
        problems.append(f"table {table} is missing")
        continue
    for col in cols:
        if col.lower() not in have[table]:
            problems.append(f"table {table} is missing column '{col}'")
for table in ("tbl_users", "tbl_students"):
    w = widths.get((table, "password"))
    if w is not None and w < 100:
        problems.append(f"{table}.password is only {w} characters wide (needs 255)")
if problems:
    print("\nPROBLEMS FOUND:")
    for p in problems:
        print("  -", p)
    print("  -> Easiest fix: run create_database.sql in MySQL Workbench. It only adds what is missing.")
    print("     For the isbn column only:  ALTER TABLE tbl_books ADD COLUMN isbn VARCHAR(13) NULL AFTER barcode;")
    print("     For narrow password columns:  ALTER TABLE tbl_users MODIFY password VARCHAR(255) NOT NULL;")
    print("                                   ALTER TABLE tbl_students MODIFY password VARCHAR(255) NOT NULL;")
    sys.exit(1)
print("   OK - all tables and columns are present.")

cur.execute(f"SELECT (SELECT COUNT(*) FROM `{dbname}`.tbl_users), (SELECT COUNT(*) FROM `{dbname}`.tbl_books), "
            f"(SELECT COUNT(*) FROM `{dbname}`.tbl_students)")
u, b, s = cur.fetchone()
print(f"\nALL GOOD. The database has {u} staff account(s), {b} book copies and {s} learner(s).")
print("Start the system in THIS window so it uses the same password, for example:")
print('   $env:LIBRARY_DB_USER = "%s"' % user)
print('   $env:LIBRARY_DB_PASSWORD = "your-password"')
print("   python app.py")
