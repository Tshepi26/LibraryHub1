-- ==========================================================================
-- LibraryHub - COMPLETE DATABASE: structure + starter users + 10 subjects + 2 learners
-- + 116 sample book copies (110 sample + 6 test copies for the barcode scanner).
-- Import it in MySQL Workbench: File > Open SQL Script > this file > lightning bolt.
-- Safe to run more than once. It never deletes or overwrites existing rows.
-- Staff and learner passwords here are plain text ON PURPOSE: the system turns each one into
-- a secure hash the first time that person signs in. Change them afterwards.
-- ==========================================================================

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


-- ------------------------------------------------------------ data
INSERT IGNORE INTO tbl_users (userID, username, password, role, fullName) VALUES
  (1, 'admin', 'admin123', 'Admin', 'System Administrator'),
  (2, 'librarian', 'lib123', 'Librarian', 'School Librarian');

INSERT IGNORE INTO tbl_category (categoryName) VALUES
  ('Mathematics'),
  ('Physical Sciences'),
  ('Information Technology'),
  ('Life Sciences'),
  ('Accounting'),
  ('English'),
  ('Geography'),
  ('History'),
  ('Business Studies'),
  ('Economics');

INSERT IGNORE INTO tbl_students (studentID, fullName, grade, section, contactNumber, dateRegistered, password) VALUES
  ('STU-2026-001', 'Thabo Mokoena', 'Grade 10', 'A', '0712345678', CURDATE(), 'STU-2026-001'),
  ('STU-2026-901', 'Test Learner', 'Grade 10', 'A', '0710000000', CURDATE(), 'STU-2026-901');

INSERT IGNORE INTO tbl_books (accessionNumber, title, author, barcode, isbn, availabilityStatus, shelfLocation, categoryID) VALUES
  ('ACC-0001', 'Mathematics Grade 10 Learner''s Book (Sample)', 'S. Naidoo', 'ACC-0001', '9781999910013', 'Available', 'MATH-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Mathematics')),
  ('ACC-0002', 'Mathematics Grade 10 Learner''s Book (Sample)', 'S. Naidoo', 'ACC-0002', '9781999910013', 'Available', 'MATH-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Mathematics')),
  ('ACC-0003', 'Mathematics Grade 10 Learner''s Book (Sample)', 'S. Naidoo', 'ACC-0003', '9781999910013', 'Available', 'MATH-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Mathematics')),
  ('ACC-0004', 'Mathematics Grade 11 Learner''s Book (Sample)', 'P. van der Merwe', 'ACC-0004', '9781999910020', 'Available', 'MATH-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Mathematics')),
  ('ACC-0005', 'Mathematics Grade 11 Learner''s Book (Sample)', 'P. van der Merwe', 'ACC-0005', '9781999910020', 'Available', 'MATH-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Mathematics')),
  ('ACC-0006', 'Mathematics Grade 11 Learner''s Book (Sample)', 'P. van der Merwe', 'ACC-0006', '9781999910020', 'Available', 'MATH-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Mathematics')),
  ('ACC-0007', 'Mathematics Grade 12 Learner''s Book (Sample)', 'L. Dlamini', 'ACC-0007', '9781999910037', 'Available', 'MATH-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Mathematics')),
  ('ACC-0008', 'Mathematics Grade 12 Learner''s Book (Sample)', 'L. Dlamini', 'ACC-0008', '9781999910037', 'Available', 'MATH-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Mathematics')),
  ('ACC-0009', 'Mathematics Grade 12 Learner''s Book (Sample)', 'L. Dlamini', 'ACC-0009', '9781999910037', 'Available', 'MATH-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Mathematics')),
  ('ACC-0010', 'Mathematics Grade 12 Study Guide (Sample)', 'A. Botha', 'ACC-0010', '9781999910044', 'Available', 'MATH-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Mathematics')),
  ('ACC-0011', 'Mathematics Grade 12 Study Guide (Sample)', 'A. Botha', 'ACC-0011', '9781999910044', 'Available', 'MATH-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Mathematics')),
  ('ACC-0012', 'Physical Sciences Grade 10 Learner''s Book (Sample)', 'N. Khumalo', 'ACC-0012', '9781999910051', 'Available', 'PHYS-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Physical Sciences')),
  ('ACC-0013', 'Physical Sciences Grade 10 Learner''s Book (Sample)', 'N. Khumalo', 'ACC-0013', '9781999910051', 'Available', 'PHYS-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Physical Sciences')),
  ('ACC-0014', 'Physical Sciences Grade 10 Learner''s Book (Sample)', 'N. Khumalo', 'ACC-0014', '9781999910051', 'Available', 'PHYS-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Physical Sciences')),
  ('ACC-0015', 'Physical Sciences Grade 11 Learner''s Book (Sample)', 'M. Pillay', 'ACC-0015', '9781999910068', 'Available', 'PHYS-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Physical Sciences')),
  ('ACC-0016', 'Physical Sciences Grade 11 Learner''s Book (Sample)', 'M. Pillay', 'ACC-0016', '9781999910068', 'Available', 'PHYS-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Physical Sciences')),
  ('ACC-0017', 'Physical Sciences Grade 11 Learner''s Book (Sample)', 'M. Pillay', 'ACC-0017', '9781999910068', 'Available', 'PHYS-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Physical Sciences')),
  ('ACC-0018', 'Physical Sciences Grade 12 Learner''s Book (Sample)', 'K. Sithole', 'ACC-0018', '9781999910075', 'Available', 'PHYS-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Physical Sciences')),
  ('ACC-0019', 'Physical Sciences Grade 12 Learner''s Book (Sample)', 'K. Sithole', 'ACC-0019', '9781999910075', 'Available', 'PHYS-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Physical Sciences')),
  ('ACC-0020', 'Physical Sciences Grade 12 Learner''s Book (Sample)', 'K. Sithole', 'ACC-0020', '9781999910075', 'Available', 'PHYS-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Physical Sciences')),
  ('ACC-0021', 'Physical Sciences Grade 12 Study Guide (Sample)', 'T. Mokoena', 'ACC-0021', '9781999910082', 'Available', 'PHYS-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Physical Sciences')),
  ('ACC-0022', 'Physical Sciences Grade 12 Study Guide (Sample)', 'T. Mokoena', 'ACC-0022', '9781999910082', 'Available', 'PHYS-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Physical Sciences')),
  ('ACC-0023', 'Information Technology Grade 10 Learner''s Book (Sample)', 'S. Naidoo', 'ACC-0023', '9781999910099', 'Available', 'INFO-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Information Technology')),
  ('ACC-0024', 'Information Technology Grade 10 Learner''s Book (Sample)', 'S. Naidoo', 'ACC-0024', '9781999910099', 'Available', 'INFO-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Information Technology')),
  ('ACC-0025', 'Information Technology Grade 10 Learner''s Book (Sample)', 'S. Naidoo', 'ACC-0025', '9781999910099', 'Available', 'INFO-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Information Technology')),
  ('ACC-0026', 'Information Technology Grade 11 Learner''s Book (Sample)', 'P. van der Merwe', 'ACC-0026', '9781999910105', 'Available', 'INFO-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Information Technology')),
  ('ACC-0027', 'Information Technology Grade 11 Learner''s Book (Sample)', 'P. van der Merwe', 'ACC-0027', '9781999910105', 'Available', 'INFO-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Information Technology')),
  ('ACC-0028', 'Information Technology Grade 11 Learner''s Book (Sample)', 'P. van der Merwe', 'ACC-0028', '9781999910105', 'Available', 'INFO-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Information Technology')),
  ('ACC-0029', 'Information Technology Grade 12 Learner''s Book (Sample)', 'L. Dlamini', 'ACC-0029', '9781999910112', 'Available', 'INFO-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Information Technology')),
  ('ACC-0030', 'Information Technology Grade 12 Learner''s Book (Sample)', 'L. Dlamini', 'ACC-0030', '9781999910112', 'Available', 'INFO-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Information Technology')),
  ('ACC-0031', 'Information Technology Grade 12 Learner''s Book (Sample)', 'L. Dlamini', 'ACC-0031', '9781999910112', 'Available', 'INFO-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Information Technology')),
  ('ACC-0032', 'Information Technology Grade 12 Study Guide (Sample)', 'A. Botha', 'ACC-0032', '9781999910129', 'Available', 'INFO-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Information Technology')),
  ('ACC-0033', 'Information Technology Grade 12 Study Guide (Sample)', 'A. Botha', 'ACC-0033', '9781999910129', 'Available', 'INFO-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Information Technology')),
  ('ACC-0034', 'Life Sciences Grade 10 Learner''s Book (Sample)', 'N. Khumalo', 'ACC-0034', '9781999910136', 'Available', 'LIFE-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Life Sciences')),
  ('ACC-0035', 'Life Sciences Grade 10 Learner''s Book (Sample)', 'N. Khumalo', 'ACC-0035', '9781999910136', 'Available', 'LIFE-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Life Sciences')),
  ('ACC-0036', 'Life Sciences Grade 10 Learner''s Book (Sample)', 'N. Khumalo', 'ACC-0036', '9781999910136', 'Available', 'LIFE-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Life Sciences')),
  ('ACC-0037', 'Life Sciences Grade 11 Learner''s Book (Sample)', 'M. Pillay', 'ACC-0037', '9781999910143', 'Available', 'LIFE-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Life Sciences')),
  ('ACC-0038', 'Life Sciences Grade 11 Learner''s Book (Sample)', 'M. Pillay', 'ACC-0038', '9781999910143', 'Available', 'LIFE-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Life Sciences')),
  ('ACC-0039', 'Life Sciences Grade 11 Learner''s Book (Sample)', 'M. Pillay', 'ACC-0039', '9781999910143', 'Available', 'LIFE-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Life Sciences')),
  ('ACC-0040', 'Life Sciences Grade 12 Learner''s Book (Sample)', 'K. Sithole', 'ACC-0040', '9781999910150', 'Available', 'LIFE-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Life Sciences')),
  ('ACC-0041', 'Life Sciences Grade 12 Learner''s Book (Sample)', 'K. Sithole', 'ACC-0041', '9781999910150', 'Available', 'LIFE-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Life Sciences')),
  ('ACC-0042', 'Life Sciences Grade 12 Learner''s Book (Sample)', 'K. Sithole', 'ACC-0042', '9781999910150', 'Available', 'LIFE-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Life Sciences')),
  ('ACC-0043', 'Life Sciences Grade 12 Study Guide (Sample)', 'T. Mokoena', 'ACC-0043', '9781999910167', 'Available', 'LIFE-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Life Sciences')),
  ('ACC-0044', 'Life Sciences Grade 12 Study Guide (Sample)', 'T. Mokoena', 'ACC-0044', '9781999910167', 'Available', 'LIFE-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Life Sciences')),
  ('ACC-0045', 'Accounting Grade 10 Learner''s Book (Sample)', 'S. Naidoo', 'ACC-0045', '9781999910174', 'Available', 'ACCT-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Accounting')),
  ('ACC-0046', 'Accounting Grade 10 Learner''s Book (Sample)', 'S. Naidoo', 'ACC-0046', '9781999910174', 'Available', 'ACCT-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Accounting')),
  ('ACC-0047', 'Accounting Grade 10 Learner''s Book (Sample)', 'S. Naidoo', 'ACC-0047', '9781999910174', 'Available', 'ACCT-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Accounting')),
  ('ACC-0048', 'Accounting Grade 11 Learner''s Book (Sample)', 'P. van der Merwe', 'ACC-0048', '9781999910181', 'Available', 'ACCT-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Accounting')),
  ('ACC-0049', 'Accounting Grade 11 Learner''s Book (Sample)', 'P. van der Merwe', 'ACC-0049', '9781999910181', 'Available', 'ACCT-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Accounting')),
  ('ACC-0050', 'Accounting Grade 11 Learner''s Book (Sample)', 'P. van der Merwe', 'ACC-0050', '9781999910181', 'Available', 'ACCT-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Accounting')),
  ('ACC-0051', 'Accounting Grade 12 Learner''s Book (Sample)', 'L. Dlamini', 'ACC-0051', '9781999910198', 'Available', 'ACCT-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Accounting')),
  ('ACC-0052', 'Accounting Grade 12 Learner''s Book (Sample)', 'L. Dlamini', 'ACC-0052', '9781999910198', 'Available', 'ACCT-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Accounting')),
  ('ACC-0053', 'Accounting Grade 12 Learner''s Book (Sample)', 'L. Dlamini', 'ACC-0053', '9781999910198', 'Available', 'ACCT-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Accounting')),
  ('ACC-0054', 'Accounting Grade 12 Study Guide (Sample)', 'A. Botha', 'ACC-0054', '9781999910204', 'Available', 'ACCT-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Accounting')),
  ('ACC-0055', 'Accounting Grade 12 Study Guide (Sample)', 'A. Botha', 'ACC-0055', '9781999910204', 'Available', 'ACCT-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Accounting')),
  ('ACC-0056', 'English Grade 10 Learner''s Book (Sample)', 'N. Khumalo', 'ACC-0056', '9781999910211', 'Available', 'ENGL-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'English')),
  ('ACC-0057', 'English Grade 10 Learner''s Book (Sample)', 'N. Khumalo', 'ACC-0057', '9781999910211', 'Available', 'ENGL-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'English')),
  ('ACC-0058', 'English Grade 10 Learner''s Book (Sample)', 'N. Khumalo', 'ACC-0058', '9781999910211', 'Available', 'ENGL-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'English')),
  ('ACC-0059', 'English Grade 11 Learner''s Book (Sample)', 'M. Pillay', 'ACC-0059', '9781999910228', 'Available', 'ENGL-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'English')),
  ('ACC-0060', 'English Grade 11 Learner''s Book (Sample)', 'M. Pillay', 'ACC-0060', '9781999910228', 'Available', 'ENGL-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'English')),
  ('ACC-0061', 'English Grade 11 Learner''s Book (Sample)', 'M. Pillay', 'ACC-0061', '9781999910228', 'Available', 'ENGL-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'English')),
  ('ACC-0062', 'English Grade 12 Learner''s Book (Sample)', 'K. Sithole', 'ACC-0062', '9781999910235', 'Available', 'ENGL-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'English')),
  ('ACC-0063', 'English Grade 12 Learner''s Book (Sample)', 'K. Sithole', 'ACC-0063', '9781999910235', 'Available', 'ENGL-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'English')),
  ('ACC-0064', 'English Grade 12 Learner''s Book (Sample)', 'K. Sithole', 'ACC-0064', '9781999910235', 'Available', 'ENGL-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'English')),
  ('ACC-0065', 'English Grade 12 Study Guide (Sample)', 'T. Mokoena', 'ACC-0065', '9781999910242', 'Available', 'ENGL-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'English')),
  ('ACC-0066', 'English Grade 12 Study Guide (Sample)', 'T. Mokoena', 'ACC-0066', '9781999910242', 'Available', 'ENGL-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'English')),
  ('ACC-0067', 'Geography Grade 10 Learner''s Book (Sample)', 'S. Naidoo', 'ACC-0067', '9781999910259', 'Available', 'GEOG-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Geography')),
  ('ACC-0068', 'Geography Grade 10 Learner''s Book (Sample)', 'S. Naidoo', 'ACC-0068', '9781999910259', 'Available', 'GEOG-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Geography')),
  ('ACC-0069', 'Geography Grade 10 Learner''s Book (Sample)', 'S. Naidoo', 'ACC-0069', '9781999910259', 'Available', 'GEOG-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Geography')),
  ('ACC-0070', 'Geography Grade 11 Learner''s Book (Sample)', 'P. van der Merwe', 'ACC-0070', '9781999910266', 'Available', 'GEOG-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Geography')),
  ('ACC-0071', 'Geography Grade 11 Learner''s Book (Sample)', 'P. van der Merwe', 'ACC-0071', '9781999910266', 'Available', 'GEOG-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Geography')),
  ('ACC-0072', 'Geography Grade 11 Learner''s Book (Sample)', 'P. van der Merwe', 'ACC-0072', '9781999910266', 'Available', 'GEOG-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Geography')),
  ('ACC-0073', 'Geography Grade 12 Learner''s Book (Sample)', 'L. Dlamini', 'ACC-0073', '9781999910273', 'Available', 'GEOG-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Geography')),
  ('ACC-0074', 'Geography Grade 12 Learner''s Book (Sample)', 'L. Dlamini', 'ACC-0074', '9781999910273', 'Available', 'GEOG-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Geography')),
  ('ACC-0075', 'Geography Grade 12 Learner''s Book (Sample)', 'L. Dlamini', 'ACC-0075', '9781999910273', 'Available', 'GEOG-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Geography')),
  ('ACC-0076', 'Geography Grade 12 Study Guide (Sample)', 'A. Botha', 'ACC-0076', '9781999910280', 'Available', 'GEOG-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Geography')),
  ('ACC-0077', 'Geography Grade 12 Study Guide (Sample)', 'A. Botha', 'ACC-0077', '9781999910280', 'Available', 'GEOG-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Geography')),
  ('ACC-0078', 'History Grade 10 Learner''s Book (Sample)', 'N. Khumalo', 'ACC-0078', '9781999910297', 'Available', 'HIST-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'History')),
  ('ACC-0079', 'History Grade 10 Learner''s Book (Sample)', 'N. Khumalo', 'ACC-0079', '9781999910297', 'Available', 'HIST-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'History')),
  ('ACC-0080', 'History Grade 10 Learner''s Book (Sample)', 'N. Khumalo', 'ACC-0080', '9781999910297', 'Available', 'HIST-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'History')),
  ('ACC-0081', 'History Grade 11 Learner''s Book (Sample)', 'M. Pillay', 'ACC-0081', '9781999910303', 'Available', 'HIST-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'History')),
  ('ACC-0082', 'History Grade 11 Learner''s Book (Sample)', 'M. Pillay', 'ACC-0082', '9781999910303', 'Available', 'HIST-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'History')),
  ('ACC-0083', 'History Grade 11 Learner''s Book (Sample)', 'M. Pillay', 'ACC-0083', '9781999910303', 'Available', 'HIST-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'History')),
  ('ACC-0084', 'History Grade 12 Learner''s Book (Sample)', 'K. Sithole', 'ACC-0084', '9781999910310', 'Available', 'HIST-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'History')),
  ('ACC-0085', 'History Grade 12 Learner''s Book (Sample)', 'K. Sithole', 'ACC-0085', '9781999910310', 'Available', 'HIST-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'History')),
  ('ACC-0086', 'History Grade 12 Learner''s Book (Sample)', 'K. Sithole', 'ACC-0086', '9781999910310', 'Available', 'HIST-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'History')),
  ('ACC-0087', 'History Grade 12 Study Guide (Sample)', 'T. Mokoena', 'ACC-0087', '9781999910327', 'Available', 'HIST-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'History')),
  ('ACC-0088', 'History Grade 12 Study Guide (Sample)', 'T. Mokoena', 'ACC-0088', '9781999910327', 'Available', 'HIST-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'History')),
  ('ACC-0089', 'Business Studies Grade 10 Learner''s Book (Sample)', 'S. Naidoo', 'ACC-0089', '9781999910334', 'Available', 'BUSI-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Business Studies')),
  ('ACC-0090', 'Business Studies Grade 10 Learner''s Book (Sample)', 'S. Naidoo', 'ACC-0090', '9781999910334', 'Available', 'BUSI-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Business Studies')),
  ('ACC-0091', 'Business Studies Grade 10 Learner''s Book (Sample)', 'S. Naidoo', 'ACC-0091', '9781999910334', 'Available', 'BUSI-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Business Studies')),
  ('ACC-0092', 'Business Studies Grade 11 Learner''s Book (Sample)', 'P. van der Merwe', 'ACC-0092', '9781999910341', 'Available', 'BUSI-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Business Studies')),
  ('ACC-0093', 'Business Studies Grade 11 Learner''s Book (Sample)', 'P. van der Merwe', 'ACC-0093', '9781999910341', 'Available', 'BUSI-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Business Studies')),
  ('ACC-0094', 'Business Studies Grade 11 Learner''s Book (Sample)', 'P. van der Merwe', 'ACC-0094', '9781999910341', 'Available', 'BUSI-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Business Studies')),
  ('ACC-0095', 'Business Studies Grade 12 Learner''s Book (Sample)', 'L. Dlamini', 'ACC-0095', '9781999910358', 'Available', 'BUSI-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Business Studies')),
  ('ACC-0096', 'Business Studies Grade 12 Learner''s Book (Sample)', 'L. Dlamini', 'ACC-0096', '9781999910358', 'Available', 'BUSI-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Business Studies')),
  ('ACC-0097', 'Business Studies Grade 12 Learner''s Book (Sample)', 'L. Dlamini', 'ACC-0097', '9781999910358', 'Available', 'BUSI-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Business Studies')),
  ('ACC-0098', 'Business Studies Grade 12 Study Guide (Sample)', 'A. Botha', 'ACC-0098', '9781999910365', 'Available', 'BUSI-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Business Studies')),
  ('ACC-0099', 'Business Studies Grade 12 Study Guide (Sample)', 'A. Botha', 'ACC-0099', '9781999910365', 'Available', 'BUSI-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Business Studies')),
  ('ACC-0100', 'Economics Grade 10 Learner''s Book (Sample)', 'N. Khumalo', 'ACC-0100', '9781999910372', 'Available', 'ECON-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Economics')),
  ('ACC-0101', 'Economics Grade 10 Learner''s Book (Sample)', 'N. Khumalo', 'ACC-0101', '9781999910372', 'Available', 'ECON-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Economics')),
  ('ACC-0102', 'Economics Grade 10 Learner''s Book (Sample)', 'N. Khumalo', 'ACC-0102', '9781999910372', 'Available', 'ECON-G10', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Economics')),
  ('ACC-0103', 'Economics Grade 11 Learner''s Book (Sample)', 'M. Pillay', 'ACC-0103', '9781999910389', 'Available', 'ECON-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Economics')),
  ('ACC-0104', 'Economics Grade 11 Learner''s Book (Sample)', 'M. Pillay', 'ACC-0104', '9781999910389', 'Available', 'ECON-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Economics')),
  ('ACC-0105', 'Economics Grade 11 Learner''s Book (Sample)', 'M. Pillay', 'ACC-0105', '9781999910389', 'Available', 'ECON-G11', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Economics')),
  ('ACC-0106', 'Economics Grade 12 Learner''s Book (Sample)', 'K. Sithole', 'ACC-0106', '9781999910396', 'Available', 'ECON-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Economics')),
  ('ACC-0107', 'Economics Grade 12 Learner''s Book (Sample)', 'K. Sithole', 'ACC-0107', '9781999910396', 'Available', 'ECON-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Economics')),
  ('ACC-0108', 'Economics Grade 12 Learner''s Book (Sample)', 'K. Sithole', 'ACC-0108', '9781999910396', 'Available', 'ECON-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Economics')),
  ('ACC-0109', 'Economics Grade 12 Study Guide (Sample)', 'T. Mokoena', 'ACC-0109', '9781999910402', 'Available', 'ECON-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Economics')),
  ('ACC-0110', 'Economics Grade 12 Study Guide (Sample)', 'T. Mokoena', 'ACC-0110', '9781999910402', 'Available', 'ECON-G12', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Economics')),
  ('ACC-9001', 'Mathematics Grade 10 (Test Copy)', 'Test Author', 'ACC-9001', '9781999900014', 'Available', 'MATH-T1', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Mathematics')),
  ('ACC-9002', 'Physical Sciences Grade 11 (Test Copy)', 'Test Author', 'ACC-9002', '9781999900021', 'Available', 'PHYS-T1', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Physical Sciences')),
  ('ACC-9003', 'Information Technology Grade 12 (Test Copy)', 'Test Author', 'ACC-9003', '9781999900038', 'Available', 'INFO-T1', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Information Technology')),
  ('ACC-9004', 'Life Sciences Grade 10 (Test Copy)', 'Test Author', 'ACC-9004', '9781999900045', 'Available', 'LIFE-T1', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Life Sciences')),
  ('ACC-9005', 'Accounting Grade 11 (Test Copy)', 'Test Author', 'ACC-9005', '9781999900052', 'Available', 'ACCT-T1', (SELECT categoryID FROM tbl_category WHERE categoryName = 'Accounting')),
  ('ACC-9006', 'English Home Language Grade 12 (Test Copy)', 'Test Author', 'ACC-9006', '9781999900069', 'Available', 'ENGL-T1', (SELECT categoryID FROM tbl_category WHERE categoryName = 'English'));

-- Check: expect 7 tables, 10 subjects and 116 book copies.
SHOW TABLES;
SELECT (SELECT COUNT(*) FROM tbl_category) AS subjects, (SELECT COUNT(*) FROM tbl_books) AS book_copies, (SELECT COUNT(*) FROM tbl_students) AS learners, (SELECT COUNT(*) FROM tbl_users) AS staff;
