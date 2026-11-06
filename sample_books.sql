-- OPTIONAL test data: 6 test books (with valid ISBN-13 barcodes) and 1 test learner.
-- Run after schema_update_isbn.sql. Print test_books_sheet.html and scan the barcodes.
-- Safe to run twice: nothing is inserted if it already exists. Delete these rows when you finish testing.
USE library_management_db;

SET @cat := (SELECT MIN(categoryID) FROM tbl_category);

INSERT INTO tbl_books (accessionNumber, title, author, barcode, isbn, availabilityStatus, shelfLocation, categoryID)
SELECT 'ACC-9001', 'Mathematics Grade 10 (Test Copy)', 'Test Author', 'ACC-9001', '9781999900014', 'Available', 'MATH-T1', @cat
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM tbl_books WHERE accessionNumber = 'ACC-9001');

INSERT INTO tbl_books (accessionNumber, title, author, barcode, isbn, availabilityStatus, shelfLocation, categoryID)
SELECT 'ACC-9002', 'Physical Sciences Grade 11 (Test Copy)', 'Test Author', 'ACC-9002', '9781999900021', 'Available', 'PHYS-T1', @cat
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM tbl_books WHERE accessionNumber = 'ACC-9002');

INSERT INTO tbl_books (accessionNumber, title, author, barcode, isbn, availabilityStatus, shelfLocation, categoryID)
SELECT 'ACC-9003', 'Information Technology Grade 12 (Test Copy)', 'Test Author', 'ACC-9003', '9781999900038', 'Available', 'INFO-T1', @cat
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM tbl_books WHERE accessionNumber = 'ACC-9003');

INSERT INTO tbl_books (accessionNumber, title, author, barcode, isbn, availabilityStatus, shelfLocation, categoryID)
SELECT 'ACC-9004', 'Life Sciences Grade 10 (Test Copy)', 'Test Author', 'ACC-9004', '9781999900045', 'Available', 'LIFE-T1', @cat
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM tbl_books WHERE accessionNumber = 'ACC-9004');

INSERT INTO tbl_books (accessionNumber, title, author, barcode, isbn, availabilityStatus, shelfLocation, categoryID)
SELECT 'ACC-9005', 'Accounting Grade 11 (Test Copy)', 'Test Author', 'ACC-9005', '9781999900052', 'Available', 'ACCT-T1', @cat
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM tbl_books WHERE accessionNumber = 'ACC-9005');

INSERT INTO tbl_books (accessionNumber, title, author, barcode, isbn, availabilityStatus, shelfLocation, categoryID)
SELECT 'ACC-9006', 'English Home Language Grade 12 (Test Copy)', 'Test Author', 'ACC-9006', '9781999900069', 'Available', 'ENGL-T1', @cat
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM tbl_books WHERE accessionNumber = 'ACC-9006');

-- Test learner. The first password is the Student ID (it is converted to a secure hash at first sign-in).
INSERT INTO tbl_students (studentID, fullName, grade, section, contactNumber, dateRegistered, password)
SELECT 'STU-2026-901', 'Test Learner', 'Grade 10', 'A', '0710000000', CURDATE(), 'STU-2026-901'
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM tbl_students WHERE studentID = 'STU-2026-901');
