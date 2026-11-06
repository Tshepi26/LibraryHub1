"""Staff accounts (Admin only): create librarians/admins and reset their passwords."""
import re

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash

from db import db
from security import admin_required
from validators import valid_name, valid_password

bp = Blueprint("staff", __name__, url_prefix="/admin")
_USERNAME = re.compile(r"[A-Za-z0-9_.]{3,30}", re.ASCII)
ROLES = ["Librarian", "Admin"]


@bp.route("/staff", methods=["GET", "POST"])
@admin_required
def index():
    with db() as cur:
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            name = request.form.get("fullName", "").strip()
            role = request.form.get("role", "")
            pw = request.form.get("password", "")
            err = None
            if not _USERNAME.fullmatch(username):
                err = "Username must be 3 to 30 letters, numbers, dots or underscores."
            elif not valid_name(name):
                err = "Full name must be letters only, 3 to 50 characters."
            elif role not in ROLES:
                err = "Choose a role from the list."
            elif not valid_password(pw):
                err = "The password must be at least 8 characters long."
            else:
                cur.execute("SELECT 1 FROM tbl_users WHERE username=%s", (username,))
                if cur.fetchone():
                    err = f"The username '{username}' is already taken."
            if err:
                flash(err, "error")
            else:
                cur.execute("INSERT INTO tbl_users(username,password,role,fullName) VALUES(%s,%s,%s,%s)",
                            (username, generate_password_hash(pw), role, name))
                flash(f"{role} account '{username}' created.", "success")
                return redirect(url_for("staff.index"))
        cur.execute("SELECT userID, username, fullName, role FROM tbl_users ORDER BY role, username")
        users = cur.fetchall()
    return render_template("staff.html", users=users, roles=ROLES)


@bp.route("/staff/<int:user_id>/reset", methods=["POST"])
@admin_required
def reset(user_id):
    pw = request.form.get("password", "")
    if not valid_password(pw):
        flash("The new password must be at least 8 characters long.", "error")
    else:
        with db() as cur:
            cur.execute("UPDATE tbl_users SET password=%s WHERE userID=%s", (generate_password_hash(pw), user_id))
        flash("Password updated.", "success")
    return redirect(url_for("staff.index"))
