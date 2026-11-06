from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, session, url_for)

import services
from db import db
from security import student_required
from validators import normalise_code

bp = Blueprint("portal", __name__)


@bp.route("/student/dashboard")
@student_required
def dashboard():
    sid = session["studentID"]
    with db() as cur:
        cur.execute(
            "SELECT b.title, b.accessionNumber, br.borrowDate, br.dueDate, c.categoryName, "
            "DATEDIFF(br.dueDate, CURDATE()) AS daysLeft "
            "FROM tbl_borrow br JOIN tbl_books b ON br.bookID=b.bookID "
            "JOIN tbl_category c ON b.categoryID=c.categoryID "
            "WHERE br.studentID=%s AND br.returnStatus='Borrowed' ORDER BY br.dueDate", (sid,))
        mybooks = cur.fetchall()
        cur.execute(
            "SELECT b.title, b.author, b.accessionNumber, b.isbn, c.categoryName FROM tbl_books b "
            "JOIN tbl_category c ON b.categoryID=c.categoryID "
            "WHERE b.availabilityStatus='Available' ORDER BY b.title LIMIT 12")
        available = cur.fetchall()
    return render_template("student_dashboard.html", mybooks=mybooks, available=available,
                           welcome=session.pop("welcome", None),
                           fine=current_app.config["FINE_PER_DAY"])


@bp.route("/student/borrow", methods=["POST"])
@student_required
def borrow():
    sid = session["studentID"]
    code = normalise_code(request.form.get("code", ""))
    if not code:
        flash("That is not a valid book code. Scan the barcode on the back cover, or type the 13-digit ISBN.", "error")
        return redirect(url_for("portal.dashboard"))
    with db() as cur:
        ok, msg, book = services.borrow_book(cur, sid, code, current_app.config["SELF_SERVICE_USER_ID"])
        if ok:
            cur.execute("INSERT INTO tbl_notifications(message,studentID,bookID) VALUES(%s,%s,%s)",
                        (f"{session['name']} borrowed {book['title']} ({book['accessionNumber']}) using the scanner",
                         sid, book["bookID"]))
    flash(msg, "success" if ok else "error")
    return redirect(url_for("portal.dashboard"))
