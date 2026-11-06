# LibraryHub v2 - ISBN barcode edition

## What changed in v2
Books are now identified the way real books are: by the **ISBN-13 barcode (EAN-13)** on the back cover.
- Scan a book's barcode to ADD it (Books page), BORROW it or RETURN it.
- Several copies of one title share an ISBN; each copy still has its own ACC-0001 copy number.
- 10-digit ISBNs on older books are converted automatically.
- Labels page prints a barcode (and a QR code) for every book. QR is easier for laptop webcams.

## Setup (in this order)
1. MySQL: run `schema_updates.sql` once (wider password columns), then `schema_update_isbn.sql` once (ISBN column).
2. `pip install -r requirements.txt`
3. `python app.py`  then open http://localhost:5000

## Test with a physical book
1. MySQL: run `sample_books.sql` (adds 6 test books and test learner STU-2026-901).
2. Open `test_books_sheet.html` in a browser and print it at 100% scale.
3. Sign in as librarian/admin, open Borrow, press "Start camera scanner", hold a printed barcode ~20 cm away.
4. Enter STU-2026-901 and confirm. Scan the same barcode on the Return page to bring it back.
Tips: good light, no glare, print large, keep the barcode flat. If a webcam struggles, use the QR code from
Books > Print labels, or type the 13 digits.
The camera needs http://localhost or https. Delete the test rows when you have finished testing.

## Optional environment variables
LIBRARY_SECRET_KEY, LIBRARY_DB_HOST, LIBRARY_DB_USER, LIBRARY_DB_PASSWORD, LIBRARY_DB_NAME, MYSQLDUMP_PATH, MYSQL_PATH

## Modules
blueprints/: auth | dashboard | books | students | circulation | portal | reports | admin (backup) | staff
Shared: config.py, db.py, security.py, validators.py (ISBN checks), barcode.py (EAN-13 drawing), services.py
