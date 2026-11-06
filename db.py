from contextlib import contextmanager

import mysql.connector
from flask import current_app


def get_conn():
    c = current_app.config
    return mysql.connector.connect(
        host=c["DB_HOST"], user=c["DB_USER"],
        password=c["DB_PASSWORD"], database=c["DB_NAME"],
    )


@contextmanager
def db():
    """Usage:  with db() as cur: cur.execute(...)
    Commits on success, rolls back on error, always closes the connection."""
    conn = get_conn()
    cur = conn.cursor(dictionary=True, buffered=True)
    try:
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def scalar(cur, sql, params=()):
    cur.execute(sql, params)
    row = cur.fetchone()
    return list(row.values())[0] if row else None
