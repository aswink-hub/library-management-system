# Library Management System

**Student:** K. Aswin | **Register No.:** 2503917720521013 | **Course:** B.Tech | **Subject:** Software Engineering

A command-line Library Management System built with **Python 3** and **SQLite**. It lets a librarian manage books and members, issue and return books, track due dates and calculate late fines.

## Problem Statement and Objectives

**Problem:** Small libraries often track books and borrowers on paper or in spreadsheets, which leads to lost records, double-issued books and unmanaged late returns.

**Objectives**
- Store books and members in a persistent database.
- Issue and return books while keeping copy counts accurate.
- Enforce rules automatically (loan limit, no duplicate issue, due dates, fines).
- Validate all user input and handle errors without crashing.

## Features / Modules Implemented

| Module | File | Description |
|---|---|---|
| Database | `lms/database.py` | SQLite schema (books, members, loans) |
| Validation | `lms/validators.py` | ISBN, email, phone, copies, ID and text checks |
| Books | `lms/books.py` | Add, list, search (title/author), remove |
| Members | `lms/members.py` | Register, list, look up |
| Loans | `lms/loans.py` | Issue, return, fine calculation, active and overdue lists |
| CLI | `main.py` | Interactive menu |
| Tests | `tests/test_lms.py` | 20 unit tests |

**Business rules:** 14-day loan period, fine of Rs. 2 per late day, maximum 3 active loans per member, a member cannot hold two copies of the same book.

## Technology Stack and Tools

- Python 3.10+ (standard library only: `sqlite3`, `unittest`, `datetime`, `re`)
- SQLite 3 (file-based database)
- Git and GitHub for version control

## Prerequisites and Installation

1. Install Python 3.10 or newer: https://www.python.org/downloads/
2. Install Git: https://git-scm.com/
3. Clone the repository:
   ```
   git clone https://github.com/<your-username>/library-management-system.git
   cd library-management-system
   ```
No third-party packages are required, so there is nothing else to install.

## Running the Application

```
python main.py
```
A `library.db` file is created automatically on first run (it is git-ignored). Choose options from the numbered menu; enter `0` to exit.

## Sample Inputs and Outputs

```
Enter choice: 1
Title: Clean Code
Author: Robert Martin
ISBN (10/13 digits): 978-0-13-235088-4
Copies: 3
Book added with ID 1.

Enter choice: 7
Book ID: 1
Member ID: 1
Book issued. Loan ID 1. Due in 14 days.

Enter choice: 5
Name: Ravi
Email: bad-email
Phone (10 digits): 123
Error: Email address is not valid.
```

## Testing Performed and Results

Run the automated tests with:
```
python -m unittest -v
```
**Result: 20 tests run, 20 passed, 0 failed.**

| Area | Cases tested |
|---|---|
| Validators | ISBN with hyphens, ISBN with letters, invalid email, short phone |
| Books | add/list, duplicate ISBN, invalid copies, case-insensitive search, remove, block removal of issued book |
| Members | duplicate email, unknown member ID |
| Loans | availability decreases, duplicate issue, no copies left, 3-loan limit, on-time return, late fine (5 days = Rs. 10), double return, overdue listing |

Manual testing of the CLI menu with valid and invalid input was also performed.

## Team Member Details and Contributions

| Name | Register No. | Contribution |
|---|---|---|
| K. Aswin | 2503917720521013 | Complete design, implementation, testing, Git workflow and documentation (individual project) |

## Known Limitations and Future Enhancements

**Limitations**
- Command-line interface only; single user at a time.
- No authentication or librarian login.
- Fine is calculated but payment is not tracked.

**Future enhancements**
- Web or GUI front end (Flask / Tkinter).
- Librarian login with roles.
- Book reservations and email reminders for due dates.
- Export of reports to CSV/PDF.

## Acknowledgements

Built using only the Python standard library. SQLite documentation (https://www.sqlite.org/docs.html) and the Python documentation were used as references.
