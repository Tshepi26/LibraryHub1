LIBRARYHUB DATABASE FILES
=========================
Database name: library_management_db   (tables: tbl_users, tbl_students, tbl_category, tbl_books,
                                          tbl_borrow, tbl_return, tbl_notifications)

02_COMPLETE_database_with_sample_data.sql   <-- USE THIS ONE
    Everything: all 7 tables with the links between them, 2 staff accounts, 10 subjects, 2 learners and
    116 book copies (110 sample + 6 test copies for the barcode scanner).

01_structure_and_starter_data.sql
    Only the tables, 2 staff accounts, 6 subjects, 2 learners and 6 test books. Use it if you want to start small.

HOW TO LOAD IT (MySQL Workbench)
  1. Open Workbench and double-click your connection (enter your MySQL password).
  2. File > Open SQL Script > pick 02_COMPLETE_database_with_sample_data.sql   (or File > New Query Tab, then
     open the file in Notepad, copy everything and paste it).
  3. Click the lightning bolt.  The last result should show: subjects 10, book_copies 116, learners 2, staff 2.
  4. Click the refresh arrow in the Schemas tab: library_management_db appears.

WITHOUT WORKBENCH: double-click setup_database.bat in the main folder (it loads the complete file).

Safe to run twice: nothing is deleted or overwritten.
Logins: admin / admin123, librarian / lib123, learner STU-2026-001 / STU-2026-001 (change after first sign-in).
Your real learner data should never go on GitHub; keep database exports on a USB drive or private OneDrive.
