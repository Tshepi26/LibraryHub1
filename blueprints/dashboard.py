from flask import Blueprint, flash, redirect, render_template, session, url_for

from db import db, scalar
from security import staff_required

bp = Blueprint("dashboard", __name__)


@bp.route("/dashboard")
@staff_required
def index():
    with db() as cur:
        total = scalar(cur, "SELECT COUNT(*) FROM tbl_books")
        borrowed = scalar(cur, "SELECT COUNT(*) FROM tbl_books WHERE availabilityStatus='Borrowed'")
        overdue = scalar(cur, "SELECT COUNT(*) FROM tbl_borrow WHERE returnStatus='Borrowed' AND dueDate < CURDATE()")
        students = scalar(cur, "SELECT COUNT(*) FROM tbl_students")
        notif_count = scalar(cur, "SELECT COUNT(*) FROM tbl_notifications WHERE isRead=0")
        cur.execute("SELECT * FROM tbl_notifications WHERE isRead=0 ORDER BY dateCreated DESC LIMIT 5")
        notifs = cur.fetchall()
        cur.execute("SELECT s.fullName, b.title, br.borrowDate FROM tbl_borrow br "
                    "JOIN tbl_students s ON br.studentID=s.studentID JOIN tbl_books b ON br.bookID=b.bookID "
                    "ORDER BY br.borrowDate DESC, br.transactionID DESC LIMIT 5")
        recent = cur.fetchall()
        cur.execute("SELECT c.categoryName, COUNT(b.bookID) AS total FROM tbl_category c "
                    "LEFT JOIN tbl_books b ON c.categoryID=b.categoryID "
                    "GROUP BY c.categoryName ORDER BY c.categoryName")
        subjects = cur.fetchall()
        staff_count = overdue_list = None
        if session["role"] == "Admin":
            staff_count = scalar(cur, "SELECT COUNT(*) FROM tbl_users")
        else:
            cur.execute("SELECT s.fullName, s.studentID, b.title, br.dueDate, "
                        "DATEDIFF(CURDATE(), br.dueDate) AS daysOver "
                        "FROM tbl_borrow br JOIN tbl_students s ON br.studentID=s.studentID "
                        "JOIN tbl_books b ON br.bookID=b.bookID "
                        "WHERE br.returnStatus='Borrowed' AND br.dueDate < CURDATE() "
                        "ORDER BY br.dueDate LIMIT 5")
            overdue_list = cur.fetchall()
    last_backup = None
    if session["role"] == "Admin":
        from blueprints.admin import _list_backups
        found = _list_backups()
        last_backup = found[0]["when"] if found else None
    return render_template("dashboard.html", total=total, borrowed=borrowed, overdue=overdue,
                           students=students, notifs=notifs, notif_count=notif_count,
                           recent=recent, subjects=subjects, staff_count=staff_count,
                           overdue_list=overdue_list, last_backup=last_backup,
                           welcome=session.pop("welcome", None))


@bp.route("/notifications/read", methods=["POST"])
@staff_required
def mark_read():
    with db() as cur:
        cur.execute("UPDATE tbl_notifications SET isRead=1")
    flash("All notifications marked as read.", "success")
    return redirect(url_for("dashboard.index"))
