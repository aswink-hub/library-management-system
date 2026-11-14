"""Member management: register, list and look up library members."""
import sqlite3

from .validators import (ValidationError, require_text, validate_email,
                         validate_id, validate_phone)


def add_member(conn, name, email, phone):
    """Register a new member. Returns the new member_id."""
    name = require_text(name, "Name", 100)
    email = validate_email(email)
    phone = validate_phone(phone)
    try:
        cur = conn.execute(
            "INSERT INTO members (name, email, phone) VALUES (?, ?, ?)",
            (name, email, phone),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValidationError(f"A member with email {email} already exists.")
    return cur.lastrowid


def list_members(conn):
    return conn.execute("SELECT * FROM members ORDER BY member_id").fetchall()


def get_member(conn, member_id):
    member_id = validate_id(member_id, "Member ID")
    row = conn.execute(
        "SELECT * FROM members WHERE member_id = ?", (member_id,)
    ).fetchone()
    if row is None:
        raise ValidationError(f"No member found with ID {member_id}.")
    return row
