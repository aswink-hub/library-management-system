"""Unit tests for the Library Management System (run: python -m unittest -v)."""
import unittest
from datetime import date

from lms import books, loans, members
from lms.database import get_connection
from lms.validators import (ValidationError, validate_email, validate_isbn,
                            validate_phone)


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.conn = get_connection(":memory:")
        self.book_id = books.add_book(self.conn, "Clean Code", "Robert Martin",
                                      "9780132350884", 2)
        self.member_id = members.add_member(self.conn, "Asha", "asha@example.com",
                                            "9876543210")

    def tearDown(self):
        self.conn.close()


class ValidatorTests(unittest.TestCase):
    def test_isbn_accepts_hyphens(self):
        self.assertEqual(validate_isbn("978-0-13-235088-4"), "9780132350884")

    def test_isbn_rejects_letters(self):
        with self.assertRaises(ValidationError):
            validate_isbn("12345abcde")

    def test_email_invalid(self):
        with self.assertRaises(ValidationError):
            validate_email("not-an-email")

    def test_phone_must_be_10_digits(self):
        with self.assertRaises(ValidationError):
            validate_phone("12345")


class BookTests(BaseTest):
    def test_add_and_list(self):
        self.assertEqual(len(books.list_books(self.conn)), 1)

    def test_duplicate_isbn_rejected(self):
        with self.assertRaises(ValidationError):
            books.add_book(self.conn, "Other", "Someone", "9780132350884", 1)

    def test_invalid_copies(self):
        with self.assertRaises(ValidationError):
            books.add_book(self.conn, "T", "A", "1234567890", 0)

    def test_search_case_insensitive(self):
        self.assertEqual(len(books.search_books(self.conn, "CLEAN")), 1)
        self.assertEqual(len(books.search_books(self.conn, "martin")), 1)
        self.assertEqual(len(books.search_books(self.conn, "zzz")), 0)

    def test_remove_book(self):
        books.remove_book(self.conn, self.book_id)
        self.assertEqual(books.list_books(self.conn), [])

    def test_cannot_remove_issued_book(self):
        loans.issue_book(self.conn, self.book_id, self.member_id)
        with self.assertRaises(ValidationError):
            books.remove_book(self.conn, self.book_id)


class MemberTests(BaseTest):
    def test_duplicate_email_rejected(self):
        with self.assertRaises(ValidationError):
            members.add_member(self.conn, "Ravi", "ASHA@example.com", "9123456780")

    def test_unknown_member(self):
        with self.assertRaises(ValidationError):
            members.get_member(self.conn, 999)


class LoanTests(BaseTest):
    def test_issue_reduces_availability(self):
        loans.issue_book(self.conn, self.book_id, self.member_id)
        self.assertEqual(books.get_book(self.conn, self.book_id)["available"], 1)

    def test_same_book_twice_rejected(self):
        loans.issue_book(self.conn, self.book_id, self.member_id)
        with self.assertRaises(ValidationError):
            loans.issue_book(self.conn, self.book_id, self.member_id)

    def test_no_copies_left(self):
        m2 = members.add_member(self.conn, "Ravi", "ravi@example.com", "9123456780")
        m3 = members.add_member(self.conn, "Mina", "mina@example.com", "9123456781")
        loans.issue_book(self.conn, self.book_id, self.member_id)
        loans.issue_book(self.conn, self.book_id, m2)
        with self.assertRaises(ValidationError):
            loans.issue_book(self.conn, self.book_id, m3)

    def test_loan_limit(self):
        ids = [books.add_book(self.conn, f"B{i}", "Auth", f"123456789{i}", 1)
               for i in range(4)]
        for b in ids[:3]:
            loans.issue_book(self.conn, b, self.member_id)
        with self.assertRaises(ValidationError):
            loans.issue_book(self.conn, ids[3], self.member_id)

    def test_return_on_time_no_fine(self):
        lid = loans.issue_book(self.conn, self.book_id, self.member_id,
                               today=date(2026, 11, 1))
        self.assertEqual(loans.return_book(self.conn, lid, today=date(2026, 11, 15)), 0)
        self.assertEqual(books.get_book(self.conn, self.book_id)["available"], 2)

    def test_late_return_fine(self):
        lid = loans.issue_book(self.conn, self.book_id, self.member_id,
                               today=date(2026, 11, 1))
        # due 15 Nov; returned 20 Nov -> 5 days late * Rs.2
        self.assertEqual(loans.return_book(self.conn, lid, today=date(2026, 11, 20)), 10.0)

    def test_double_return_rejected(self):
        lid = loans.issue_book(self.conn, self.book_id, self.member_id)
        loans.return_book(self.conn, lid)
        with self.assertRaises(ValidationError):
            loans.return_book(self.conn, lid)

    def test_overdue_listing(self):
        loans.issue_book(self.conn, self.book_id, self.member_id,
                         today=date(2026, 10, 1))
        self.assertEqual(len(loans.overdue_loans(self.conn, today=date(2026, 11, 14))), 1)
        self.assertEqual(len(loans.overdue_loans(self.conn, today=date(2026, 10, 5))), 0)


if __name__ == "__main__":
    unittest.main()
