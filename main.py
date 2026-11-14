"""Command-line menu for the Library Management System.

Run:  python main.py
"""
import sys

from lms import books, loans, members
from lms.database import get_connection
from lms.validators import ValidationError

MENU = """
========== LIBRARY MANAGEMENT SYSTEM ==========
 1. Add book              6. List members
 2. List books            7. Issue book
 3. Search books          8. Return book
 4. Remove book           9. Active loans
 5. Add member           10. Overdue loans
 0. Exit
===============================================
"""


def print_books(rows):
    if not rows:
        print("No books found.")
        return
    print(f"{'ID':<4}{'Title':<30}{'Author':<22}{'ISBN':<15}{'Avail/Total'}")
    for r in rows:
        print(f"{r['book_id']:<4}{r['title'][:28]:<30}{r['author'][:20]:<22}"
              f"{r['isbn']:<15}{r['available']}/{r['copies']}")


def print_members(rows):
    if not rows:
        print("No members registered.")
        return
    print(f"{'ID':<4}{'Name':<22}{'Email':<30}{'Phone'}")
    for r in rows:
        print(f"{r['member_id']:<4}{r['name'][:20]:<22}{r['email'][:28]:<30}{r['phone']}")


def print_loans(rows, overdue=False):
    if not rows:
        print("No overdue loans." if overdue else "No active loans.")
        return
    for r in rows:
        print(f"Loan #{r['loan_id']}: '{r['title']}' -> {r['name']} (due {r['due_date']})")


def handle(conn, choice):
    if choice == "1":
        book_id = books.add_book(conn, input("Title: "), input("Author: "),
                                 input("ISBN (10/13 digits): "), input("Copies: "))
        print(f"Book added with ID {book_id}.")
    elif choice == "2":
        print_books(books.list_books(conn))
    elif choice == "3":
        print_books(books.search_books(conn, input("Keyword (title/author): ")))
    elif choice == "4":
        books.remove_book(conn, input("Book ID to remove: "))
        print("Book removed.")
    elif choice == "5":
        member_id = members.add_member(conn, input("Name: "), input("Email: "),
                                       input("Phone (10 digits): "))
        print(f"Member registered with ID {member_id}.")
    elif choice == "6":
        print_members(members.list_members(conn))
    elif choice == "7":
        loan_id = loans.issue_book(conn, input("Book ID: "), input("Member ID: "))
        print(f"Book issued. Loan ID {loan_id}. Due in {loans.LOAN_DAYS} days.")
    elif choice == "8":
        fine = loans.return_book(conn, input("Loan ID: "))
        print("Book returned." + (f" Late fine: Rs. {fine:.2f}" if fine else " No fine."))
    elif choice == "9":
        print_loans(loans.active_loans(conn))
    elif choice == "10":
        print_loans(loans.overdue_loans(conn), overdue=True)
    else:
        print("Invalid choice. Please enter a number from the menu.")


def main():
    conn = get_connection()
    try:
        while True:
            print(MENU)
            choice = input("Enter choice: ").strip()
            if choice == "0":
                print("Goodbye!")
                break
            try:
                handle(conn, choice)
            except ValidationError as err:
                print(f"Error: {err}")
    except (EOFError, KeyboardInterrupt):
        print("\nExiting.")
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
