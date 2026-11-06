import csv
import io
import os

from flask import (Blueprint, abort, current_app, flash, redirect, render_template,
                   request, send_file, url_for)
from markupsafe import Markup

from barcode import ean13_svg
from db import db
from security import admin_required, staff_required
from validators import (normalise_code, valid_accession, valid_name,
                        valid_shelf, valid_title)

try:                      # QR images are optional; the EAN-13 barcodes need no library
    import qrcode
except ImportError:       # pragma: no cover
    qrcode = None

bp = Blueprint("books", __name__)


def _check_book(form, valid_cats):
    """Returns (data, error). data = (accession or None, isbn, title, author, shelf, category)."""
    parsed = normalise_code(form.get("isbn", ""))
    acc = form.get("accession", "").strip().upper()
    title = form.get("title", "").strip()
    author = form.get("author", "").strip()
    shelf = form.get("shelf", "").strip().upper()
    category = form.get("category", "").strip()
    if not parsed or parsed[0] != "isbn":
        return None, ("ISBN must be a valid 13-digit ISBN (the number under the barcode on the back cover, "
                      "starting 978 or 979). Older 10-digit ISBNs are converted automatically.")
    if acc and not valid_accession(acc):
        return None, f"Accession must look like ACC-0001, or leave it empty to number it automatically (you entered: {acc})."
    if not valid_title(title):
        return None, "Title must be between 3 and 100 characters."
    if not valid_name(author):
        return None, "Author must be letters only (spaces, full stops, hyphens and apostrophes are allowed), 3 to 50 characters."
    if not valid_shelf(shelf):
        return None, "Shelf must look like MATH-A2 (letters, numbers and hyphens)."
    if category not in valid_cats:
        return None, "Choose a subject category from the list."
    return (acc or None, parsed[1], title, author, shelf, int(category)), None


def _next_accession(cur):
    # ACC-9xxx numbers are reserved for the test copies, so automatic numbering skips them.
    cur.execute("SELECT accessionNumber FROM tbl_books WHERE accessionNumber REGEXP '^ACC-[0-9]{4}$' "
                "AND accessionNumber < 'ACC-9000' ORDER BY accessionNumber DESC LIMIT 1")
    row = cur.fetchone()
    n = int(row["accessionNumber"][4:]) + 1 if row else 1
    return f"ACC-{n:04d}" if n < 9000 else None


@bp.route("/books", methods=["GET", "POST"])
@staff_required
def index():
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "")
    with db() as cur:
        cur.execute("SELECT categoryID, categoryName FROM tbl_category ORDER BY categoryName")
        cats = cur.fetchall()
        if request.method == "POST":
            valid_cats = {str(c["categoryID"]) for c in cats}
            data, err = _check_book(request.form, valid_cats)
            if not err:
                acc, isbn, title, author, shelf, cat = data
                acc = acc or _next_accession(cur)
                cur.execute("SELECT title FROM tbl_books WHERE isbn=%s LIMIT 1", (isbn,))
                same = cur.fetchone()
                if not acc:
                    err = "No automatic accession numbers are left. Type one yourself."
                elif same and same["title"].strip().lower() != title.lower():
                    err = f"ISBN {isbn} is already registered as '{same['title']}'. Check the ISBN or use the same title."
                else:
                    cur.execute("SELECT 1 FROM tbl_books WHERE accessionNumber=%s OR barcode=%s", (acc, acc))
                    if cur.fetchone():
                        err = f"Accession {acc} already exists."
            if err:
                flash(err, "error")
            else:
                cur.execute(
                    "INSERT INTO tbl_books(accessionNumber,title,author,barcode,isbn,availabilityStatus,"
                    "shelfLocation,categoryID) VALUES(%s,%s,%s,%s,%s,'Available',%s,%s)",
                    (acc, title, author, acc, isbn, shelf, cat))
                flash(f"Book added as {acc} (ISBN {isbn}). Print its label from 'Print labels'.", "success")
                return redirect(url_for("books.index"))

        sql = ("SELECT b.*, c.categoryName FROM tbl_books b "
               "JOIN tbl_category c ON b.categoryID=c.categoryID WHERE 1=1")
        params = []
        if q:
            sql += " AND (b.accessionNumber LIKE %s OR b.title LIKE %s OR b.author LIKE %s OR b.isbn LIKE %s)"
            params += [f"%{q}%"] * 4
        if status in ("Available", "Borrowed"):
            sql += " AND b.availabilityStatus=%s"
            params.append(status)
        cur.execute(sql + " ORDER BY b.accessionNumber", params)
        rows = cur.fetchall()
    return render_template("books.html", books=rows, cats=cats, q=q, status=status)


@bp.route("/books/<acc>/isbn", methods=["POST"])
@staff_required
def set_isbn(acc):
    acc = acc.upper()
    if not valid_accession(acc):
        abort(404)
    parsed = normalise_code(request.form.get("isbn", ""))
    if not parsed or parsed[0] != "isbn":
        flash("That is not a valid ISBN. Use the 13 digits under the barcode on the back cover.", "error")
    else:
        with db() as cur:
            cur.execute("UPDATE tbl_books SET isbn=%s WHERE accessionNumber=%s", (parsed[1], acc))
        flash(f"ISBN {parsed[1]} saved for {acc}.", "success")
    return redirect(url_for("books.index"))


@bp.route("/qr/<code>")
@staff_required
def qr_image(code):
    parsed = normalise_code(code)
    if not parsed or qrcode is None:
        abort(404)
    buf = io.BytesIO()
    qrcode.make(parsed[1]).save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")


@bp.route("/books/labels")
@staff_required
def labels():
    q = request.args.get("q", "").strip()
    with db() as cur:
        sql = "SELECT accessionNumber, title, author, isbn FROM tbl_books"
        params = []
        if q:
            sql += " WHERE accessionNumber LIKE %s OR title LIKE %s OR isbn LIKE %s"
            params = [f"%{q}%"] * 3
        cur.execute(sql + " ORDER BY accessionNumber", params)
        rows = cur.fetchall()
    items = [dict(r, svg=Markup(ean13_svg(r["isbn"])) if r["isbn"] else None) for r in rows]
    return render_template("labels.html", books=items, has_qr=qrcode is not None, q=q)


# --- Bulk import ---------------------------------------------------------------
MAX_IMPORT_ROWS = 2000
REQUIRED_COLUMNS = ("isbn", "title", "author", "shelf", "subject")


def import_rows(cur, rows):
    """Adds every valid row (one book copy per 'copies'). Returns (titles_added, copies_added, errors)."""
    errors, titles, copies_total = [], 0, 0
    cur.execute("SELECT categoryID, categoryName FROM tbl_category")
    cats = {c["categoryName"].strip().lower(): c["categoryID"] for c in cur.fetchall()}
    cur.execute("SELECT DISTINCT isbn, title FROM tbl_books WHERE isbn IS NOT NULL")
    known = {r["isbn"]: r["title"].strip().lower() for r in cur.fetchall()}
    cur.execute("SELECT accessionNumber FROM tbl_books WHERE accessionNumber REGEXP '^ACC-[0-9]{4}$' "
                "AND accessionNumber < 'ACC-9000' ORDER BY accessionNumber DESC LIMIT 1")
    last = cur.fetchone()
    counter = int(last["accessionNumber"][4:]) if last else 0

    for line, r in enumerate(rows, start=2):                      # line 1 is the header
        parsed = normalise_code(r.get("isbn", ""))
        title = (r.get("title") or "").strip()
        author = (r.get("author") or "").strip()
        shelf = (r.get("shelf") or "").strip().upper()
        subject = (r.get("subject") or "").strip()
        try:
            copies = int((r.get("copies") or "1").strip() or 1)
        except ValueError:
            copies = 0
        if not parsed or parsed[0] != "isbn":
            errors.append(f"Row {line}: '{r.get('isbn', '')}' is not a valid ISBN."); continue
        isbn = parsed[1]
        if not valid_title(title):
            errors.append(f"Row {line}: title must be 3 to 100 characters."); continue
        if not valid_name(author):
            errors.append(f"Row {line}: author '{author}' must be letters only (3 to 50 characters)."); continue
        if not valid_shelf(shelf):
            errors.append(f"Row {line}: shelf '{shelf}' must look like MATH-A2."); continue
        if not subject or len(subject) > 100:
            errors.append(f"Row {line}: subject is missing or too long."); continue
        if not 1 <= copies <= 20:
            errors.append(f"Row {line}: copies must be a number from 1 to 20."); continue
        if isbn in known and known[isbn] != title.lower():
            errors.append(f"Row {line}: ISBN {isbn} is already registered under a different title."); continue
        if counter + copies >= 9000:
            errors.append(f"Row {line}: no automatic copy numbers left."); break

        cat_id = cats.get(subject.lower())
        if cat_id is None:
            cur.execute("INSERT INTO tbl_category(categoryName) VALUES(%s)", (subject,))
            cat_id = cur.lastrowid
            cats[subject.lower()] = cat_id
        for _ in range(copies):
            counter += 1
            acc = f"ACC-{counter:04d}"
            cur.execute(
                "INSERT INTO tbl_books(accessionNumber,title,author,barcode,isbn,availabilityStatus,"
                "shelfLocation,categoryID) VALUES(%s,%s,%s,%s,%s,'Available',%s,%s)",
                (acc, title, author, acc, isbn, shelf, cat_id))
        known[isbn] = title.lower()
        titles += 1
        copies_total += copies
    return titles, copies_total, errors


def _report_import(titles, copies, errors):
    if titles:
        flash(f"Imported {titles} title(s), {copies} copies in total. Print their labels from 'Print labels'.", "success")
    for e in errors[:6]:
        flash(e, "error")
    if len(errors) > 6:
        flash(f"...and {len(errors) - 6} more row(s) with problems were skipped.", "error")
    if not titles and not errors:
        flash("The file had no books in it.", "error")


@bp.route("/books/import", methods=["POST"])
@staff_required
def import_csv():
    upload = request.files.get("file")
    if not upload or not upload.filename.lower().endswith(".csv"):
        flash("Choose a .csv file to import.", "error")
        return redirect(url_for("books.index"))
    try:
        text = upload.read().decode("utf-8-sig")
    except UnicodeDecodeError:
        flash("Could not read the file. In Excel choose Save As > CSV UTF-8, then try again.", "error")
        return redirect(url_for("books.index"))
    reader = csv.DictReader(io.StringIO(text))
    reader.fieldnames = [(h or "").strip().lower() for h in (reader.fieldnames or [])]
    missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
    if missing:
        flash("The file is missing these columns: " + ", ".join(missing) +
              ". The first row must be: isbn,title,author,shelf,subject,copies", "error")
        return redirect(url_for("books.index"))
    rows = list(reader)
    if len(rows) > MAX_IMPORT_ROWS:
        flash(f"That file has {len(rows)} rows. Import at most {MAX_IMPORT_ROWS} at a time.", "error")
        return redirect(url_for("books.index"))
    with db() as cur:
        result = import_rows(cur, rows)
    _report_import(*result)
    return redirect(url_for("books.index"))


@bp.route("/books/load-sample", methods=["POST"])
@admin_required
def load_sample():
    """One click: adds the bundled sample catalogue (10 subjects, about 100 copies)."""
    with db() as cur:
        cur.execute("SELECT COUNT(*) AS c FROM tbl_books WHERE isbn LIKE '9781999910%'")
        if cur.fetchone()["c"]:
            flash("The sample catalogue is already loaded.", "info")
            return redirect(url_for("books.index"))
        with open(os.path.join(current_app.root_path, "sample_catalogue.csv"), encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        result = import_rows(cur, rows)
    _report_import(*result)
    return redirect(url_for("books.index"))
