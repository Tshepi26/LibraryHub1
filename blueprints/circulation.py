from flask import Blueprint, flash, redirect, render_template, request, session, url_for

import services
from db import db
from security import staff_required
from validators import normalise_code, valid_student_id

bp = Blueprint("circulation", __name__)
CONDITIONS = ["Good", "Fair", "Damaged"]
BAD_CODE = ("That is not a valid book code. Scan the barcode on the back cover, or type the "
            "13-digit ISBN (or an ACC-0001 copy number).")


@bp.route("/borrow", methods=["GET", "POST"])
@staff_required
def borrow():
    if request.method == "POST":
        sid = request.form.get("studentID", "").strip().upper()
        code = normalise_code(request.form.get("code", ""))
        if not valid_student_id(sid):
            flash(f"Student ID must look like STU-2026-001 (you entered: {sid or 'nothing'}).", "error")
        elif not code:
            flash(BAD_CODE, "error")
        else:
            with db() as cur:
                ok, msg, _ = services.borrow_book(cur, sid, code, session["userID"])
            flash(msg, "success" if ok else "error")
            if ok:
                return redirect(url_for("circulation.borrow"))
    return render_template("borrow.html")


@bp.route("/return", methods=["GET", "POST"])
@staff_required
def return_book():
    if request.method == "POST":
        code = normalise_code(request.form.get("code", ""))
        sid = request.form.get("studentID", "").strip().upper()
        cond = request.form.get("condition", "Good")
        if not code:
            flash(BAD_CODE, "error")
        elif sid and not valid_student_id(sid):
            flash(f"Student ID must look like STU-2026-001 (you entered: {sid}).", "error")
        elif cond not in CONDITIONS:
            flash("Choose the book's condition from the list.", "error")
        else:
            with db() as cur:
                ok, msg = services.return_book(cur, code, cond, sid or None)
            flash(msg, "success" if ok else "error")
            if ok:
                return redirect(url_for("circulation.return_book"))
    return render_template("return.html", conditions=CONDITIONS)
