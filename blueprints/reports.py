import io
from datetime import date
from decimal import Decimal

import pandas as pd
from flask import (Blueprint, abort, current_app, render_template, request,
                   send_file)
from fpdf import FPDF

from db import db
from security import staff_required

bp = Blueprint("reports", __name__)

TITLES = {
    "daily": ("Daily Borrowing Report", "Daily_Borrowing_Report",
              "Every book borrowed on the chosen day."),
    "overdue": ("Overdue Report", "Overdue_Report",
                "Books that are past their due date and still not returned. Needs follow-up."),
    "subjects": ("Subject-Wise Inventory Report", "Inventory_Report",
                 "How many books each subject has, and how many are in or out."),
}


def _run_report(cur, kind, day):
    fine = current_app.config["FINE_PER_DAY"]
    if kind == "daily":
        cur.execute(
            "SELECT s.fullName AS Learner, s.studentID AS StudentID, b.title AS BookTitle, "
            "c.categoryName AS Subject, b.isbn AS ISBN, b.accessionNumber AS Copy, "
            "br.borrowDate AS BorrowDate, br.dueDate AS DueDate "
            "FROM tbl_borrow br JOIN tbl_students s ON br.studentID=s.studentID "
            "JOIN tbl_books b ON br.bookID=b.bookID JOIN tbl_category c ON b.categoryID=c.categoryID "
            "WHERE br.borrowDate=%s ORDER BY br.transactionID DESC", (day,))
    elif kind == "overdue":
        cur.execute(
            "SELECT s.fullName AS Learner, s.studentID AS StudentID, b.title AS BookTitle, "
            "c.categoryName AS Subject, br.dueDate AS DueDate, "
            "DATEDIFF(CURDATE(), br.dueDate) AS DaysOver, DATEDIFF(CURDATE(), br.dueDate)*%s AS Fine "
            "FROM tbl_borrow br JOIN tbl_students s ON br.studentID=s.studentID "
            "JOIN tbl_books b ON br.bookID=b.bookID JOIN tbl_category c ON b.categoryID=c.categoryID "
            "WHERE br.returnStatus='Borrowed' AND br.dueDate < CURDATE() ORDER BY br.dueDate", (fine,))
    else:
        cur.execute(
            "SELECT c.categoryName AS Subject, COUNT(b.bookID) AS TotalBooks, "
            "COALESCE(SUM(b.availabilityStatus='Available'),0) AS Available, "
            "COALESCE(SUM(b.availabilityStatus='Borrowed'),0) AS Borrowed "
            "FROM tbl_category c LEFT JOIN tbl_books b ON c.categoryID=b.categoryID "
            "GROUP BY c.categoryName ORDER BY c.categoryName")
    rows = cur.fetchall()
    for r in rows:
        for k, v in r.items():
            if isinstance(v, Decimal):
                r[k] = int(v)
    return list(cur.column_names), rows


def _context(kind):
    if kind not in TITLES:
        abort(404)
    day = date.today()
    if kind == "daily" and request.args.get("date"):
        try:
            day = date.fromisoformat(request.args["date"])
        except ValueError:
            abort(400, "Date must look like 2026-11-04.")
    title, filename, desc = TITLES[kind]
    if kind == "daily":
        title = f"{title} - {day}"
    with db() as cur:
        columns, rows = _run_report(cur, kind, day)
    return dict(kind=kind, title=title, filename=filename, desc=desc, day=day,
                columns=columns, rows=rows)


@bp.route("/reports/<kind>")
@staff_required
def view(kind):
    return render_template("reports.html", **_context(kind))


@bp.route("/reports/<kind>/download/<filetype>")
@staff_required
def download(kind, filetype):
    ctx = _context(kind)
    df = pd.DataFrame(ctx["rows"], columns=ctx["columns"])
    name = f"{ctx['filename']}_{date.today()}"

    if filetype == "excel":
        out = io.BytesIO()
        df.to_excel(out, index=False, engine="openpyxl")
        out.seek(0)
        return send_file(out, download_name=f"{name}.xlsx", as_attachment=True,
                         mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    if filetype == "pdf":
        def txt(v, n=None):
            s = str(v).encode("latin-1", "replace").decode("latin-1")
            return s[:n] if n else s

        pdf = FPDF(orientation="L")
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, txt(ctx["title"]) + " - LibraryHub", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(0, 6, f"Generated on {date.today()} | High School Library System",
                 new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(4)
        usable = pdf.w - pdf.l_margin - pdf.r_margin
        w = usable / max(len(df.columns), 1)
        limit = max(int(w / 1.7), 6)
        pdf.set_font("Helvetica", "B", 8)
        for col in df.columns:
            pdf.cell(w, 8, txt(col, limit), border=1, align="C")
        pdf.ln()
        pdf.set_font("Helvetica", "", 8)
        for _, row in df.iterrows():
            for val in row:
                pdf.cell(w, 7, txt(val, limit), border=1)
            pdf.ln()
        if df.empty:
            pdf.cell(0, 10, "No records for this report.", align="C")
        out = io.BytesIO(bytes(pdf.output()))
        return send_file(out, download_name=f"{name}.pdf", as_attachment=True, mimetype="application/pdf")

    abort(404)
