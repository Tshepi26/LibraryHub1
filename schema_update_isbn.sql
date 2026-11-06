-- Run ONCE (after schema_updates.sql). Adds the ISBN column that the barcode scanner uses.
USE library_management_db;

ALTER TABLE tbl_books ADD COLUMN isbn VARCHAR(13) NULL AFTER barcode;
CREATE INDEX idx_books_isbn ON tbl_books (isbn);

-- Several copies of one title share an ISBN, so the index is deliberately not UNIQUE.
-- Existing books keep working by their ACC- copy number; add their ISBN from the Books page.
