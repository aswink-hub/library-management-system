"""Issue and return books, with due dates and late-fine calculation."""
from datetime import date, timedelta

from .books import get_book
from .members import get_member
from .validators import ValidationError, validate_id

LOAN_DAYS = 14
FINE_PER_DAY = 2.0   # rupees per day late
MAX_ACTIVE_LOANS = 3


def issue_book(conn, book_id, member_id, today=None):
    """Issue a book to a member. Returns the new loan_id."""
    today = today or date.today()
    book = get_book(conn, book_id)
    member = get_member(conn, member_id)

    if book["available"] < 1:
        raise ValidationError(f"No copies of '{book['title']}' are available.")

    active = conn.execute(
        "SELECT COUNT(*) FROM loans WHERE member_id = ? AND return_date IS NULL",
        (member["member_id"],),
    ).fetchone()[0]
    if active >= MAX_ACTIVE_LOANS:
        raise ValidationError(
            f"{member['name']} already has {MAX_ACTIVE_LOANS} books issued (limit reached)."
        )

    already = conn.execute(
        "SELECT 1 FROM loans WHERE book_id = ? AND member_id = ? AND return_date IS NULL",
        (book["book_id"], member["member_id"]),
    ).fetchone()
    if already:
        raise ValidationError("This member already has this book issued.")

    due = today + timedelta(days=LOAN_DAYS)
    cur = conn.execute(
        "INSERT INTO loans (book_id, member_id, issue_date, due_date) VALUES (?, ?, ?, ?)",
        (book["book_id"], member["member_id"], today.isoformat(), due.isoformat()),
    )
    conn.execute(
        "UPDATE books SET available = available - 1 WHERE book_id = ?",
        (book["book_id"],),
    )
    conn.commit()
    return cur.lastrowid


def calculate_fine(due_date, return_date):
    """Fine = FINE_PER_DAY for every day returned after the due date."""
    late_days = (return_date - due_date).days
    return max(0, late_days) * FINE_PER_DAY


def return_book(conn, loan_id, today=None):
    """Return a loan. Returns the fine amount (0 if on time)."""
    today = today or date.today()
    loan_id = validate_id(loan_id, "Loan ID")
    loan = conn.execute("SELECT * FROM loans WHERE loan_id = ?", (loan_id,)).fetchone()
    if loan is None:
        raise ValidationError(f"No loan found with ID {loan_id}.")
    if loan["return_date"] is not None:
        raise ValidationError("This loan has already been returned.")

    fine = calculate_fine(date.fromisoformat(loan["due_date"]), today)
    conn.execute(
        "UPDATE loans SET return_date = ?, fine = ? WHERE loan_id = ?",
        (today.isoformat(), fine, loan_id),
    )
    conn.execute(
        "UPDATE books SET available = available + 1 WHERE book_id = ?",
        (loan["book_id"],),
    )
    conn.commit()
    return fine


def active_loans(conn):
    return conn.execute(
        "SELECT l.loan_id, b.title, m.name, l.issue_date, l.due_date "
        "FROM loans l JOIN books b ON b.book_id = l.book_id "
        "JOIN members m ON m.member_id = l.member_id "
        "WHERE l.return_date IS NULL ORDER BY l.due_date"
    ).fetchall()


def overdue_loans(conn, today=None):
    today = (today or date.today()).isoformat()
    return conn.execute(
        "SELECT l.loan_id, b.title, m.name, l.due_date "
        "FROM loans l JOIN books b ON b.book_id = l.book_id "
        "JOIN members m ON m.member_id = l.member_id "
        "WHERE l.return_date IS NULL AND l.due_date < ? ORDER BY l.due_date",
        (today,),
    ).fetchall()
