import secrets
from functools import wraps

from flask import abort, flash, redirect, request, session, url_for
from werkzeug.security import check_password_hash

STAFF_ROLES = ("Admin", "Librarian")
_HASH_PREFIXES = ("scrypt:", "pbkdf2:")


def home_for(role):
    return url_for("portal.dashboard") if role == "Student" else url_for("dashboard.index")


def roles_required(*roles):
    def deco(f):
        @wraps(f)
        def wrapper(*a, **k):
            if "role" not in session:
                flash("Please sign in to continue.", "error")
                return redirect(url_for("auth.login", next=request.path))
            if session["role"] not in roles:
                abort(403)
            return f(*a, **k)
        return wrapper
    return deco


login_required = roles_required("Admin", "Librarian", "Student")
staff_required = roles_required(*STAFF_ROLES)
admin_required = roles_required("Admin")
student_required = roles_required("Student")


def verify_password(stored, supplied):
    """Returns (ok, needs_upgrade). Old plain-text passwords still work once
    and are re-saved as hashes by the login route."""
    if not stored:
        return False, False
    if stored.startswith(_HASH_PREFIXES):
        return check_password_hash(stored, supplied), False
    return secrets.compare_digest(stored.encode(), supplied.encode()), True


def safe_next(target):
    if target and target.startswith("/") and not target.startswith("//"):
        return target
    return None


# --- CSRF protection: every POST form must carry the session's token -------
def csrf_token():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_hex(16)
    return session["_csrf"]


def init_csrf(app):
    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.before_request
    def _check_csrf():
        if request.method == "POST":
            sent = request.form.get("csrf_token", "")
            real = session.get("_csrf", "")
            if not sent or not real or not secrets.compare_digest(sent.encode(), real.encode()):
                abort(400, "Your page expired or the security token was missing. "
                           "Go back, refresh the page and try again.")
