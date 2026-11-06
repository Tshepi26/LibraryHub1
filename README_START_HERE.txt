LIBRARYHUB - START HERE
=======================

1. Extract this zip (right-click > Extract All).
2. Make sure MySQL is installed and running.
3. Double-click  setup_database.bat   (creates the database with 116 sample books; asks for your MySQL password).
   All database files are also in the database folder (see database\README_DATABASE.txt).
4. Double-click  run_app.bat          (installs libraries, starts the system, opens the browser).
5. Sign in:
      Admin      admin / admin123
      Librarian  librarian / lib123
      Learner    STU-2026-001 / STU-2026-001
   Change these passwords from "Change password" after your first sign-in.

Add more books
  - Books page > "Load sample catalogue" (admin only): adds about 100 sample copies in 10 subjects in one click.
  - Books page > "Add many books at once": upload your own CSV (columns: isbn,title,author,shelf,subject,copies).
    An example file is linked on that page. In Excel use Save As > CSV UTF-8.
  - Or add them one by one by scanning the barcode on the back cover.

Test the barcode scanner
  - Open test_books_sheet.html, print it at 100% scale.
  - Sign in as librarian > Borrow > Start camera scanner > hold a printed barcode ~20 cm from the camera.
  - Learner for testing: STU-2026-901.

If the .bat files do not work
  - Open MySQL Workbench > File > Open SQL Script > create_database.sql > click the lightning bolt.
  - In a terminal in this folder:  pip install -r requirements.txt   then   python app.py
    (set LIBRARY_DB_PASSWORD=your MySQL password first)

Files: app.py (starts the system), blueprints/ (one file per module), templates/ (pages), static/ (style and scanner),
create_database.sql (all tables + starter data), schema_*.sql (only for upgrading an OLD database - not needed with a new one).
