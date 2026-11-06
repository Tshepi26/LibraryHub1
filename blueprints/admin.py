"""Backup and restore (Admin only). Uses MySQL's own mysqldump / mysql tools."""
import os
import re
import subprocess
import tempfile
from datetime import datetime

from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, request, send_from_directory, url_for)

from security import admin_required

bp = Blueprint("admin", __name__, url_prefix="/admin")
_NAME = re.compile(r"library_backup_\d{8}_\d{6}\.sql", re.ASCII)


class BackupError(Exception):
    pass


def _env():
    env = os.environ.copy()
    env["MYSQL_PWD"] = current_app.config["DB_PASSWORD"]   # keeps the password off the command line
    return env


def _run(cmd, **kw):
    try:
        return subprocess.run(cmd, env=_env(), stderr=subprocess.PIPE, timeout=300, **kw)
    except FileNotFoundError:
        raise BackupError(f"Could not find '{cmd[0]}'. Set MYSQLDUMP_PATH / MYSQL_PATH to the full "
                          "path of the MySQL tools (see README).")
    except subprocess.TimeoutExpired:
        raise BackupError("The operation took too long and was stopped.")


def create_backup():
    c = current_app.config
    os.makedirs(c["BACKUP_DIR"], exist_ok=True)
    name = datetime.now().strftime("library_backup_%Y%m%d_%H%M%S.sql")
    path = os.path.join(c["BACKUP_DIR"], name)
    cmd = [c["MYSQLDUMP_PATH"], "-h", c["DB_HOST"], "-u", c["DB_USER"],
           "--single-transaction", "--routines", "--triggers", c["DB_NAME"]]
    with open(path, "wb") as out:
        try:
            r = _run(cmd, stdout=out)
        except BackupError:
            out.close()
            os.remove(path)
            raise
    if r.returncode != 0:
        os.remove(path)
        raise BackupError("mysqldump failed: " + r.stderr.decode(errors="replace")[:300])
    return name


def restore_file(path):
    c = current_app.config
    with open(path, "rb") as f:
        r = _run([c["MYSQL_PATH"], "-h", c["DB_HOST"], "-u", c["DB_USER"], c["DB_NAME"]],
                 stdin=f, stdout=subprocess.DEVNULL)
    if r.returncode != 0:
        raise BackupError("Restore failed: " + r.stderr.decode(errors="replace")[:300])


def _list_backups():
    d = current_app.config["BACKUP_DIR"]
    os.makedirs(d, exist_ok=True)
    items = []
    for n in sorted(os.listdir(d), reverse=True):
        if _NAME.fullmatch(n):
            st = os.stat(os.path.join(d, n))
            items.append(dict(name=n, kb=max(st.st_size // 1024, 1),
                              when=datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")))
    return items


@bp.route("/backup")
@admin_required
def backup():
    return render_template("backup.html", backups=_list_backups())


@bp.route("/backup/create", methods=["POST"])
@admin_required
def backup_create():
    try:
        flash(f"Backup created: {create_backup()}", "success")
    except BackupError as e:
        flash(str(e), "error")
    return redirect(url_for("admin.backup"))


@bp.route("/backup/download/<name>")
@admin_required
def backup_download(name):
    if not _NAME.fullmatch(name):
        abort(404)
    return send_from_directory(current_app.config["BACKUP_DIR"], name, as_attachment=True)


@bp.route("/backup/restore", methods=["POST"])
@admin_required
def backup_restore():
    if request.form.get("confirm", "").strip() != "RESTORE":
        flash("Type RESTORE in the box to confirm. Nothing was changed.", "error")
        return redirect(url_for("admin.backup"))
    tmp = None
    try:
        safety = create_backup()          # always keep a copy of the current data first
        upload = request.files.get("file")
        if upload and upload.filename:
            if not upload.filename.lower().endswith(".sql"):
                raise BackupError("Only .sql backup files can be restored.")
            fd, tmp = tempfile.mkstemp(suffix=".sql")
            os.close(fd)
            upload.save(tmp)
            restore_file(tmp)
            source = upload.filename
        else:
            name = request.form.get("name", "")
            if not _NAME.fullmatch(name):
                raise BackupError("Choose a backup from the list or upload a .sql file.")
            restore_file(os.path.join(current_app.config["BACKUP_DIR"], name))
            source = name
        flash(f"Database restored from {source}. A safety copy of the previous data was saved as {safety}.", "success")
    except BackupError as e:
        flash(str(e), "error")
    finally:
        if tmp and os.path.exists(tmp):
            os.remove(tmp)
    return redirect(url_for("admin.backup"))
