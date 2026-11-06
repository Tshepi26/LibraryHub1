from flask import (Blueprint, abort, flash, redirect, render_template,
                   request, url_for)
from werkzeug.security import generate_password_hash

from db import db
from security import staff_required
from validators import (GRADES, valid_grade, valid_name, valid_phone,
                        valid_student_id)

bp = Blueprint("students", __name__)


@bp.route("/students", methods=["GET", "POST"])
@staff_required
def index():
    q = request.args.get("q", "").strip()
    with db() as cur:
        if request.method == "POST":
            sid = request.form.get("studentID", "").strip().upper()
            name = request.form.get("fullName", "").strip()
            grade = request.form.get("grade", "").strip()
            contact = request.form.get("contact", "").strip()
            err = None
            if not valid_student_id(sid):
                err = f"Student ID must look like STU-2026-001 (you entered: {sid or 'nothing'})."
            elif not valid_name(name):
                err = "Full name must be letters only (spaces, hyphens and apostrophes are allowed), 3 to 50 characters."
            elif not valid_grade(grade):
                err = "Choose a grade from the list."
            elif not valid_phone(contact):
                err = "Contact must be 10 digits starting with 0, e.g. 0712345678."
            else:
                cur.execute("SELECT 1 FROM tbl_students WHERE studentID=%s", (sid,))
                if cur.fetchone():
                    err = f"Learner {sid} is already registered."
            if err:
                flash(err, "error")
            else:
                # The first password is the Student ID. It is stored hashed.
                cur.execute(
                    "INSERT INTO tbl_students(studentID,fullName,grade,section,contactNumber,dateRegistered,password) "
                    "VALUES(%s,%s,%s,'A',%s,CURDATE(),%s)",
                    (sid, name, grade, contact, generate_password_hash(sid)))
                flash(f"Learner {sid} registered. Their first password is their Student ID.", "success")
                return redirect(url_for("students.index"))

        if q:
            cur.execute("SELECT * FROM tbl_students WHERE studentID LIKE %s OR fullName LIKE %s ORDER BY studentID",
                        (f"%{q}%", f"%{q}%"))
        else:
            cur.execute("SELECT * FROM tbl_students ORDER BY studentID")
        rows = cur.fetchall()
    return render_template("students.html", students=rows, grades=GRADES, q=q)


@bp.route("/students/<sid>/reset-password", methods=["POST"])
@staff_required
def reset_password(sid):
    sid = sid.upper()
    if not valid_student_id(sid):
        abort(404)
    with db() as cur:
        cur.execute("UPDATE tbl_students SET password=%s WHERE studentID=%s",
                    (generate_password_hash(sid), sid))
    flash(f"Password for {sid} was reset to the Student ID.", "success")
    return redirect(url_for("students.index"))
