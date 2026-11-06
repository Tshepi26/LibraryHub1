import time

import mysql.connector

from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, session, url_for)
from werkzeug.security import generate_password_hash

from db import db
from security import (home_for, login_required, safe_next, verify_password)
from validators import valid_password

bp = Blueprint("auth", __name__)


def _upgrade_hash(cur, table, id_col, ident, plain):
    """Replace an old plain-text password with a hash. If the column is too narrow
    the login must still succeed, so a failure here is only logged."""
    try:
        sql = {"tbl_users": "UPDATE tbl_users SET password=%s WHERE userID=%s",
               "tbl_students": "UPDATE tbl_students SET password=%s WHERE studentID=%s"}[table]
        cur.execute(sql, (generate_password_hash(plain), ident))
    except mysql.connector.Error as e:
        current_app.logger.warning("Could not upgrade password for %s %s: %s. "
                                   "Run schema_updates.sql to widen the password column.", table, ident, e)
_failed = {}  # "ip|username" -> (count, locked_until)


def _lock_seconds(key):
    count, until = _failed.get(key, (0, 0))
    if until and until > time.time():
        return int(until - time.time())
    if until:
        _failed.pop(key, None)
    return 0


def _register_failure(key):
    cfg = current_app.config
    count, _ = _failed.get(key, (0, 0))
    count += 1
    locked = time.time() + cfg["LOGIN_LOCK_SECONDS"] if count >= cfg["MAX_LOGIN_ATTEMPTS"] else 0
    _failed[key] = (count, locked)


def _start_session(key, user_id, role, name, welcome, student_id=None):
    _failed.pop(key, None)
    session.clear()
    session.permanent = True
    session.update(userID=user_id, role=role, name=name, welcome=welcome)
    if student_id:
        session["studentID"] = student_id
    return redirect(safe_next(request.args.get("next")) or home_for(role))


@bp.route("/", methods=["GET", "POST"])
def login():
    if session.get("role"):
        return redirect(home_for(session["role"]))
    if request.method == "POST":
        u = request.form.get("username", "").strip()
        p = request.form.get("password", "")
        key = f"{request.remote_addr}|{u.lower()}"
        wait = _lock_seconds(key)
        if wait:
            flash(f"Too many failed attempts. Try again in {wait // 60 + 1} minute(s).", "error")
            return render_template("login.html"), 429
        if not u or not p:
            flash("Enter your username (or Student ID) and your password.", "error")
            return render_template("login.html")

        user = st = None
        with db() as cur:
            cur.execute("SELECT userID, fullName, role, password FROM tbl_users WHERE username=%s", (u,))
            user = cur.fetchone()
            if user:
                ok, upgrade = verify_password(user["password"], p)
                if ok:
                    if upgrade:
                        _upgrade_hash(cur, "tbl_users", "userID", user["userID"], p)
                    return _start_session(
                        key, user["userID"], user["role"], user["fullName"],
                        f"Welcome back, {user['fullName']}! You are signed in as {user['role']}.")

            cur.execute("SELECT studentID, fullName, password FROM tbl_students WHERE studentID=%s", (u.upper(),))
            st = cur.fetchone()
            if st:
                ok, upgrade = verify_password(st["password"], p)
                if ok:
                    if upgrade:
                        _upgrade_hash(cur, "tbl_students", "studentID", st["studentID"], p)
                    return _start_session(
                        key, st["studentID"], "Student", st["fullName"],
                        f"Welcome, {st['fullName']}! Scan a textbook's barcode to borrow it.",
                        student_id=st["studentID"])

        _register_failure(key)
        current_app.logger.warning("Failed login for '%s': staff account %s, learner record %s.",
                                   u, "found" if user else "not found", "found" if st else "not found")
        flash("Invalid username or password.", "error")
        return render_template("login.html", username=u)
    return render_template("login.html")


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))


@bp.route("/account/password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        current = request.form.get("current", "")
        new = request.form.get("new", "")
        confirm = request.form.get("confirm", "")
        is_student = session["role"] == "Student"
        with db() as cur:
            if is_student:
                cur.execute("SELECT password FROM tbl_students WHERE studentID=%s", (session["studentID"],))
            else:
                cur.execute("SELECT password FROM tbl_users WHERE userID=%s", (session["userID"],))
            row = cur.fetchone()
            ok = bool(row) and verify_password(row["password"], current)[0]
            if not ok:
                flash("Your current password is not correct.", "error")
            elif not valid_password(new):
                flash("The new password must be at least 8 characters long.", "error")
            elif new != confirm:
                flash("The new password and the confirmation do not match.", "error")
            elif new == current:
                flash("Choose a password different from your current one.", "error")
            else:
                hashed = generate_password_hash(new)
                if is_student:
                    cur.execute("UPDATE tbl_students SET password=%s WHERE studentID=%s",
                                (hashed, session["studentID"]))
                else:
                    cur.execute("UPDATE tbl_users SET password=%s WHERE userID=%s",
                                (hashed, session["userID"]))
                flash("Password changed.", "success")
                return redirect(home_for(session["role"]))
    return render_template("change_password.html")
