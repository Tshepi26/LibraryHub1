"""All settings in one place. Override any of them with environment variables
so passwords and secrets never have to live inside the code."""
import os
import secrets
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    # --- Security ---------------------------------------------------------
    # Set LIBRARY_SECRET_KEY to keep users logged in across server restarts.
    SECRET_KEY = os.environ.get("LIBRARY_SECRET_KEY") or secrets.token_hex(32)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)   # idle timeout
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024               # largest upload (restore file)
    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_LOCK_SECONDS = 300

    # --- Database ---------------------------------------------------------
    DB_HOST = os.environ.get("LIBRARY_DB_HOST", "localhost")
    DB_USER = os.environ.get("LIBRARY_DB_USER", "root")
    DB_PASSWORD = os.environ.get("LIBRARY_DB_PASSWORD", "change-me")
    DB_NAME = os.environ.get("LIBRARY_DB_NAME", "library_management_db")

    # --- Library rules ----------------------------------------------------
    LOAN_DAYS = 7
    FINE_PER_DAY = 2          # rand per day overdue
    MAX_LOANS = 3             # books one learner may hold at once
    SELF_SERVICE_USER_ID = 1  # tbl_users.userID recorded for QR self-borrowing

    # --- Backup -----------------------------------------------------------
    BACKUP_DIR = os.path.join(BASE_DIR, "backups")
    # If these are not on your PATH, set the full path, e.g.
    # C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe
    MYSQLDUMP_PATH = os.environ.get("MYSQLDUMP_PATH", "mysqldump")
    MYSQL_PATH = os.environ.get("MYSQL_PATH", "mysql")
