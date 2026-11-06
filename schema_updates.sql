-- Run ONCE in MySQL Workbench / the mysql client before starting the new app.
-- Hashed passwords are about 160 characters long, so the columns must be wide enough.
USE library_management_db;

ALTER TABLE tbl_users    MODIFY password VARCHAR(255) NOT NULL;
ALTER TABLE tbl_students MODIFY password VARCHAR(255) NOT NULL;

-- Existing plain-text passwords keep working: each one is converted to a secure
-- hash automatically the first time that person signs in.

-- Optional speed-ups (skip any line that errors with "Duplicate key name"):
CREATE INDEX idx_borrow_student_status ON tbl_borrow (studentID, returnStatus);
CREATE INDEX idx_borrow_due            ON tbl_borrow (dueDate);
CREATE INDEX idx_books_status          ON tbl_books (availabilityStatus);
