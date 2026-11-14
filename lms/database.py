"""SQLite database connection and schema setup."""
import sqlite3

DEFAULT_DB = "library.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS books (
    book_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    title     TEXT NOT NULL,
    author    TEXT NOT NULL,
    isbn      TEXT NOT NULL UNIQUE,
    copies    INTEGER NOT NULL CHECK (copies >= 0),
    available INTEGER NOT NULL CHECK (available >= 0)
);

CREATE TABLE IF NOT EXISTS members (
    member_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT NOT NULL,
    email     TEXT NOT NULL UNIQUE,
    phone     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS loans (
    loan_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id     INTEGER NOT NULL REFERENCES books(book_id),
    member_id   INTEGER NOT NULL REFERENCES members(member_id),
    issue_date  TEXT NOT NULL,
    due_date    TEXT NOT NULL,
    return_date TEXT,
    fine        REAL NOT NULL DEFAULT 0
);
"""


def get_connection(path=DEFAULT_DB):
    """Open a connection (use ':memory:' for tests) and make sure tables exist."""
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    conn.commit()
    return conn
