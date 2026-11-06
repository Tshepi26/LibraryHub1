"""Borrow / return rules shared by the librarian screens and the student portal.
A 'code' is the pair returned by validators.normalise_code: ('isbn', '978...') or ('acc', 'ACC-0001')."""
from datetime import date, timedelta

from flask import current_app


def _label(code):
    return ("ISBN " if code[0] == "isbn" else "copy ") + code[1]


def borrow_book(cur, sid, code, user_id):
    """Returns (ok, message, book_row)."""
    cfg = current_app.config
    kind, value = code
    cur.execute("SELECT studentID, fullName FROM tbl_students WHERE studentID=%s", (sid,))
    if not cur.fetchone():
        return False, f"Learner {sid} does not exist.", None

    cur.execute("SELECT COUNT(*) AS c FROM tbl_borrow WHERE studentID=%s AND returnStatus='Borrowed' "
                "AND dueDate < CURDATE()", (sid,))
    if cur.fetchone()["c"]:
        return False, (f"{sid} has an overdue book. Return it first "
                       f"(fine R{cfg['FINE_PER_DAY']} per day)."), None

    cur.execute("SELECT COUNT(*) AS c FROM tbl_borrow WHERE studentID=%s AND returnStatus='Borrowed'", (sid,))
    if cur.fetchone()["c"] >= cfg["MAX_LOANS"]:
        return False, f"{sid} already has {cfg['MAX_LOANS']} books out, the maximum allowed.", None

    if kind == "acc":
        cur.execute("SELECT bookID, title, isbn, accessionNumber, availabilityStatus FROM tbl_books "
                    "WHERE accessionNumber=%s OR barcode=%s LIMIT 1", (value, value))
    else:
        # Several copies can share an ISBN. Prefer a copy that is on the shelf.
        cur.execute("SELECT bookID, title, isbn, accessionNumber, availabilityStatus FROM tbl_books "
                    "WHERE isbn=%s ORDER BY (availabilityStatus='Available') DESC, accessionNumber LIMIT 1",
                    (value,))
    book = cur.fetchone()
    if not book:
        return False, f"No book with {_label(code)} is registered. Add it on the Books page first.", None

    if book["isbn"]:
        cur.execute("SELECT 1 FROM tbl_borrow br JOIN tbl_books b ON br.bookID=b.bookID "
                    "WHERE br.studentID=%s AND br.returnStatus='Borrowed' AND b.isbn=%s", (sid, book["isbn"]))
        if cur.fetchone():
            return False, f"{sid} already has a copy of {book['title']}.", None

    if book["availabilityStatus"] != "Available":
        if kind == "isbn":
            return False, f"All copies of {book['title']} are out right now.", None
        return False, f"Copy {book['accessionNumber']} of {book['title']} is out right now.", None

    # Only one request can win this update, so two people can't borrow the same copy.
    cur.execute("UPDATE tbl_books SET availabilityStatus='Borrowed' "
                "WHERE bookID=%s AND availabilityStatus='Available'", (book["bookID"],))
    if cur.rowcount != 1:
        return False, f"{book['title']} was just borrowed by someone else.", None

    bd = date.today()
    dd = bd + timedelta(days=cfg["LOAN_DAYS"])
    cur.execute("INSERT INTO tbl_borrow(studentID,bookID,userID,borrowDate,dueDate,returnStatus) "
                "VALUES(%s,%s,%s,%s,%s,'Borrowed')", (sid, book["bookID"], user_id, bd, dd))
    return True, f"Success! {book['title']} (copy {book['accessionNumber']}) borrowed by {sid}. Due back {dd}.", book


def return_book(cur, code, condition, sid=None):
    """Returns (ok, message)."""
    cfg = current_app.config
    kind, value = code
    sql = ("SELECT br.transactionID, br.dueDate, br.bookID, br.studentID, bk.title, bk.accessionNumber "
           "FROM tbl_borrow br JOIN tbl_books bk ON br.bookID=bk.bookID WHERE br.returnStatus='Borrowed' AND ")
    if kind == "acc":
        sql += "(bk.accessionNumber=%s OR bk.barcode=%s)"
        params = [value, value]
    else:
        sql += "bk.isbn=%s"
        params = [value]
    if sid:
        sql += " AND br.studentID=%s"
        params.append(sid)
    cur.execute(sql + " ORDER BY br.borrowDate, br.transactionID", params)
    rows = cur.fetchall()
    if not rows:
        return False, f"No active borrowing found for {_label(code)}" + (f" and learner {sid}." if sid else ".")
    if kind == "isbn" and not sid and len({r["studentID"] for r in rows}) > 1:
        return False, ("Several copies of this title are out with different learners. "
                       "Enter the learner's Student ID as well, then confirm again.")
    rec = rows[0]
    days_late = (date.today() - rec["dueDate"]).days
    fine = days_late * cfg["FINE_PER_DAY"] if days_late > 0 else 0
    cur.execute("INSERT INTO tbl_return(transactionID,returnDate,fineAmount,`condition`) "
                "VALUES(%s,CURDATE(),%s,%s)", (rec["transactionID"], fine, condition))
    cur.execute("UPDATE tbl_books SET availabilityStatus='Available' WHERE bookID=%s", (rec["bookID"],))
    cur.execute("UPDATE tbl_borrow SET returnStatus='Returned' WHERE transactionID=%s", (rec["transactionID"],))
    late = f" ({days_late} day(s) late)" if days_late > 0 else ""
    return True, f"Returned: {rec['title']} (copy {rec['accessionNumber']}) from {rec['studentID']}{late}. Fine: R{fine}."
