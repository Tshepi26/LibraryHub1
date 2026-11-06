import re

_A = re.ASCII
_ACC = re.compile(r"ACC-\d{4}", _A)
_STU = re.compile(r"STU-\d{4}-\d{3}", _A)
_NAME = re.compile(r"[A-Za-z][A-Za-z .'\-]{2,49}", _A)
_PHONE = re.compile(r"0\d{9}", _A)
_SHELF = re.compile(r"[A-Z0-9][A-Z0-9\-]{1,14}", _A)

GRADES = ["Grade 8", "Grade 9", "Grade 10", "Grade 11", "Grade 12"]


def valid_accession(v):   return bool(_ACC.fullmatch(v or ""))
def valid_student_id(v):  return bool(_STU.fullmatch(v or ""))
def valid_name(v):        return bool(_NAME.fullmatch(v or ""))
def valid_phone(v):       return bool(_PHONE.fullmatch(v or ""))
def valid_shelf(v):       return bool(_SHELF.fullmatch(v or ""))
def valid_title(v):       return 3 <= len(v or "") <= 100
def valid_grade(v):       return v in GRADES
def valid_password(v):    return len(v or "") >= 8


# --- ISBN support -----------------------------------------------------------
def valid_isbn13(v):
    """13 digits starting 978/979 with a correct check digit."""
    if not re.fullmatch(r"97[89]\d{10}", v or "", _A):
        return False
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(v))
    return total % 10 == 0


def isbn10_to_13(v):
    """Older books carry a 10-character ISBN. Convert it, or return None if it is invalid."""
    if not re.fullmatch(r"\d{9}[\dX]", v or "", _A):
        return None
    total = sum((10 - i) * (10 if c == "X" else int(c)) for i, c in enumerate(v))
    if total % 11 != 0:
        return None
    core = "978" + v[:9]
    check = (10 - sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(core)) % 10) % 10
    return core + str(check)


def normalise_code(raw):
    """Turns whatever was scanned or typed into ('isbn', 13digits) or ('acc', 'ACC-0001').
    Returns None if it is neither."""
    s = (raw or "").strip().upper()
    if valid_accession(s):
        return ("acc", s)
    digits = re.sub(r"[\s-]", "", s)
    if len(digits) == 10:
        digits = isbn10_to_13(digits) or ""
    if valid_isbn13(digits):
        return ("isbn", digits)
    return None
