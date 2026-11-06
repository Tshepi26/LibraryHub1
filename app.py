import os

import mysql.connector
from flask import Flask, render_template, request

from blueprints import admin, auth, books, circulation, dashboard, portal, reports, staff, students
from config import Config
from security import init_csrf


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    init_csrf(app)

    for module in (auth, dashboard, books, students, circulation, portal, reports, admin, staff):
        app.register_blueprint(module.bp)

    @app.after_request
    def headers(resp):
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "same-origin"
        if not request.path.startswith("/static"):
            resp.headers["Cache-Control"] = "no-store"   # back button won't show pages after logout
        return resp

    def error_page(code, title, message):
        return render_template("error.html", code=code, title=title, message=message), code

    @app.errorhandler(400)
    def bad_request(e):
        return error_page(400, "Request not accepted", e.description)

    @app.errorhandler(403)
    def forbidden(e):
        return error_page(403, "Not allowed", "Your account does not have permission to open this page.")

    @app.errorhandler(404)
    def not_found(e):
        return error_page(404, "Page not found", "That page does not exist.")

    @app.errorhandler(413)
    def too_big(e):
        return error_page(413, "File too large", "That file is bigger than the system accepts.")

    DB_HINTS = {
        1045: "MySQL refused the username or password. The LIBRARY_DB_PASSWORD you started the system with is wrong.",
        2003: "The system cannot reach MySQL. Start the MySQL80 service (Win+R, services.msc), then refresh.",
        2002: "The system cannot reach MySQL. Start the MySQL80 service (Win+R, services.msc), then refresh.",
        1049: "The database library_management_db does not exist on this MySQL server. Run create_database.sql in Workbench.",
        1146: "A table is missing. Run create_database.sql in Workbench.",
        1054: "A column is missing from a table (for example isbn). Run python check_connection.py to see which one.",
        2059: "MySQL's login method is not supported by the installed connector. Run: python -m pip install --upgrade mysql-connector-python",
    }

    @app.errorhandler(mysql.connector.Error)
    def db_error(e):
        app.logger.exception(e)          # the full detail is printed in the terminal window
        hint = DB_HINTS.get(getattr(e, "errno", None),
                            "The system could not complete that action. Look at the terminal window for the last red line, "
                            "or run: python check_connection.py")
        return error_page(500, "Database problem", hint)

    @app.errorhandler(500)
    def server_error(e):
        return error_page(500, "Something went wrong", "An unexpected error happened. Nothing was lost.")

    return app


app = create_app()

if __name__ == "__main__":
    # Set FLASK_DEBUG=1 while developing. Never run with debug on in real use.
    app.run(host="127.0.0.1", debug=os.environ.get("FLASK_DEBUG") == "1")
