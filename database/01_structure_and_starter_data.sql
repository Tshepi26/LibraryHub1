-- LibraryHub: creates the WHOLE database from scratch (tables, links between tables, starter data).
-- Safe to run more than once: it never deletes anything that already exists.
-- Open it in MySQL Workbench (File > Open SQL Script) and click the lightning bolt.
-- It already includes the password and ISBN changes, so schema_updates.sql and schema_update_isbn.sql are NOT needed after this.

CREATE DATABASE IF NOT EXISTS library_management_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE library_management_db;

CREATE TABLE IF NOT EXISTS tbl_users (
  userID    INT AUTO_INCREMENT PRIMARY KEY,
  username  VARCHAR(50)  NOT NULL UNIQUE,
  password  VARCHAR(255) NOT NULL,
  role      VARCHAR(20)  NOT NULL,           -- 'Admin' or 'Librarian'
  fullName  VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tbl_category (
  categoryID   INT AUTO_INCREMENT PRIMARY KEY,
  categoryName VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tbl_students (
  studentID      VARCHAR(20)  PRIMARY KEY,   -- e.g. STU-2026-001
  fullName       VARCHAR(100) NOT NULL,
  grade          VARCHAR(20)  NOT NULL,
  section        VARCHAR(10)  NOT NULL DEFAULT 'A',
  contactNumber  VARCHAR(15)  NOT NULL,
  dateRegistered DATE         NOT NULL,
  password       VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tbl_books (
  bookID             INT AUTO_INCREMENT PRIMARY KEY,
  accessionNumber    VARCHAR(20)  NOT NULL UNIQUE,   -- copy number, e.g. ACC-0001
  title              VARCHAR(150) NOT NULL,
  author             VARCHAR(100) NOT NULL,
  barcode            VARCHAR(30)  NULL,
  isbn               VARCHAR(13)  NULL,              -- shared by all copies of a title
  availabilityStatus VARCHAR(20)  NOT NULL DEFAULT 'Available',
  shelfLocation      VARCHAR(30)  NOT NULL,
  categoryID         INT          NOT NULL,
  INDEX idx_books_isbn (isbn),
  INDEX idx_books_status (availabilityStatus),
  CONSTRAINT fk_books_category FOREIGN KEY (categoryID) REFERENCES tbl_category (categoryID)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tbl_borrow (
  transactionID INT AUTO_INCREMENT PRIMARY KEY,
  studentID     VARCHAR(20) NOT NULL,
  bookID        INT         NOT NULL,
  userID        INT         NOT NULL,                -- who lent it (user 1 = self-service)
  borrowDate    DATE        NOT NULL,
  dueDate       DATE        NOT NULL,
  returnStatus  VARCHAR(20) NOT NULL DEFAULT 'Borrowed',
  INDEX idx_borrow_student_status (studentID, returnStatus),
  INDEX idx_borrow_due (dueDate),
  CONSTRAINT fk_borrow_student FOREIGN KEY (studentID) REFERENCES tbl_students (studentID),
  CONSTRAINT fk_borrow_book    FOREIGN KEY (bookID)    REFERENCES tbl_books (bookID),
  CONSTRAINT fk_borrow_user    FOREIGN KEY (userID)    REFERENCES tbl_users (userID)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tbl_return (
  returnID      INT AUTO_INCREMENT PRIMARY KEY,
  transactionID INT           NOT NULL,
  returnDate    DATE          NOT NULL,
  fineAmount    DECIMAL(8,2)  NOT NULL DEFAULT 0,
  `condition`   VARCHAR(20)   NOT NULL DEFAULT 'Good',
  CONSTRAINT fk_return_borrow FOREIGN KEY (transactionID) REFERENCES tbl_borrow (transactionID)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tbl_notifications (
  notificationID INT AUTO_INCREMENT PRIMARY KEY,
  message        VARCHAR(255) NOT NULL,
  studentID      VARCHAR(20)  NULL,
  bookID         INT          NULL,
  isRead         TINYINT(1)   NOT NULL DEFAULT 0,
  dateCreated    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_notif_student FOREIGN KEY (studentID) REFERENCES tbl_students (studentID),
  CONSTRAINT fk_notif_book    FOREIGN KEY (bookID)    REFERENCES tbl_books (bookID)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------- starter data
-- Staff passwords below are plain text on purpose: the app turns each one into a secure hash the
-- first time that person signs in. Change them from "Change password" after your first login.
INSERT IGNORE INTO tbl_users (userID, username, password, role, fullName) VALUES
  (1, 'admin',     'admin123', 'Admin',     'System Administrator'),
  (2, 'librarian', 'lib123',   'Librarian', 'School Librarian');

INSERT IGNORE INTO tbl_category (categoryName) VALUES
  ('Mathematics'), ('Physical Sciences'), ('Information Technology'),
  ('Life Sciences'), ('Accounting'), ('English');

-- Test learner (first password = the Student ID) and the demo learner from your login page.
INSERT IGNORE INTO tbl_students (studentID, fullName, grade, section, contactNumber, dateRegistered, password) VALUES
  ('STU-2026-001', 'Thabo Mokoena', 'Grade 10', 'A', '0712345678', CURDATE(), 'STU-2026-001'),
  ('STU-2026-901', 'Test Learner',  'Grade 10', 'A', '0710000000', CURDATE(), 'STU-2026-901');

-- Six test books with valid ISBN-13 barcodes (print test_books_sheet.html to scan them).
INSERT IGNORE INTO tbl_books (accessionNumber, title, author, barcode, isbn, availabilityStatus, shelfLocation, categoryID)
  SELECT 'ACC-9001', 'Mathematics Grade 10 (Test Copy)', 'Test Author', 'ACC-9001', '9781999900014', 'Available', 'MATH-T1', categoryID
  FROM tbl_category WHERE categoryName = 'Mathematics';
INSERT IGNORE INTO tbl_books (accessionNumber, title, author, barcode, isbn, availabilityStatus, shelfLocation, categoryID)
  SELECT 'ACC-9002', 'Physical Sciences Grade 11 (Test Copy)', 'Test Author', 'ACC-9002', '9781999900021', 'Available', 'PHYS-T1', categoryID
  FROM tbl_category WHERE categoryName = 'Physical Sciences';
INSERT IGNORE INTO tbl_books (accessionNumber, title, author, barcode, isbn, availabilityStatus, shelfLocation, categoryID)
  SELECT 'ACC-9003', 'Information Technology Grade 12 (Test Copy)', 'Test Author', 'ACC-9003', '9781999900038', 'Available', 'INFO-T1', categoryID
  FROM tbl_category WHERE categoryName = 'Information Technology';
INSERT IGNORE INTO tbl_books (accessionNumber, title, author, barcode, isbn, availabilityStatus, shelfLocation, categoryID)
  SELECT 'ACC-9004', 'Life Sciences Grade 10 (Test Copy)', 'Test Author', 'ACC-9004', '9781999900045', 'Available', 'LIFE-T1', categoryID
  FROM tbl_category WHERE categoryName = 'Life Sciences';
INSERT IGNORE INTO tbl_books (accessionNumber, title, author, barcode, isbn, availabilityStatus, shelfLocation, categoryID)
  SELECT 'ACC-9005', 'Accounting Grade 11 (Test Copy)', 'Test Author', 'ACC-9005', '9781999900052', 'Available', 'ACCT-T1', categoryID
  FROM tbl_category WHERE categoryName = 'Accounting';
INSERT IGNORE INTO tbl_books (accessionNumber, title, author, barcode, isbn, availabilityStatus, shelfLocation, categoryID)
  SELECT 'ACC-9006', 'English Home Language Grade 12 (Test Copy)', 'Test Author', 'ACC-9006', '9781999900069', 'Available', 'ENGL-T1', categoryID
  FROM tbl_category WHERE categoryName = 'English';

-- Quick check: this should list 7 tables and the starter rows.
SHOW TABLES;
SELECT COUNT(*) AS books FROM tbl_books;
