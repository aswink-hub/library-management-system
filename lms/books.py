"""Book management: add, search, list and remove books."""
import sqlite3

from .validators import (ValidationError, require_text, validate_copies,
                         validate_id, validate_isbn)


def add_book(conn, title, author, isbn, copies):
    """Add a new book. Returns the new book_id."""
    title = require_text(title, "Title", 150)
    author = require_text(author, "Author", 100)
    isbn = validate_isbn(isbn)
    copies = validate_copies(copies)
    try:
        cur = conn.execute(
            "INSERT INTO books (title, author, isbn, copies, available) "
            "VALUES (?, ?, ?, ?, ?)",
            (title, author, isbn, copies, copies),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValidationError(f"A book with ISBN {isbn} already exists.")
    return cur.lastrowid


def list_books(conn):
    return conn.execute("SELECT * FROM books ORDER BY book_id").fetchall()


def search_books(conn, keyword):
    """Case-insensitive search on title or author."""
    keyword = require_text(keyword, "Search keyword", 100)
    like = f"%{keyword}%"
    return conn.execute(
        "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? ORDER BY title",
        (like, like),
    ).fetchall()


def get_book(conn, book_id):
    book_id = validate_id(book_id, "Book ID")
    row = conn.execute("SELECT * FROM books WHERE book_id = ?", (book_id,)).fetchone()
    if row is None:
        raise ValidationError(f"No book found with ID {book_id}.")
    return row


def remove_book(conn, book_id):
    """Delete a book that has no active loans."""
    book = get_book(conn, book_id)
    active = conn.execute(
        "SELECT COUNT(*) FROM loans WHERE book_id = ? AND return_date IS NULL",
        (book["book_id"],),
    ).fetchone()[0]
    if active:
        raise ValidationError("Cannot remove a book that is currently issued.")
    conn.execute("DELETE FROM loans WHERE book_id = ?", (book["book_id"],))
    conn.execute("DELETE FROM books WHERE book_id = ?", (book["book_id"],))
    conn.commit()
