"""Add realistic personal to-do examples for every existing employee account.

Run from anywhere: python seed_demo_tasks.py
Deadlines are anchored to the presentation date, 3 November 2026.
Existing tasks are kept. Use --refresh-dates to move only the named demo tasks'
deadlines to the selected date; their priorities and completion states are kept.
A verified SQLite backup is made before changes. Accounts are not changed.
"""

import argparse
import sqlite3
from contextlib import closing
from datetime import date, datetime, timedelta
from pathlib import Path

DEMO_DATE = date(2026, 11, 3)

# Each role has nine active reminders followed by three completed examples.
TASK_TITLES = {
    "employee": (
        "Finalise the outstanding customer quotation",
        "Submit last week's expense receipts",
        "Review today's priority client correspondence",
        "Update the weekly activity log",
        "Prepare notes for the team briefing",
        "Complete the product knowledge refresher",
        "Review the customer follow-up checklist",
        "Organise reference documents",
        "Suggest improvements to the enquiry process",
        "Confirm access to shared company resources",
        "Review the updated customer service guidelines",
        "Refresh the standard email signature",
    ),
    "team leader": (
        "Resolve outstanding team handover actions",
        "Review the weekly workload notes",
        "Confirm ownership of today's priority actions",
        "Update the team briefing agenda",
        "Prepare the next one-to-one meeting notes",
        "Review the team's delivery risks",
        "Refresh the new-starter checklist",
        "Organise team reference materials",
        "Record suggestions for the next retrospective",
        "Confirm the team's escalation contacts",
        "Review the previous handover summary",
        "Archive superseded meeting notes",
    ),
    "manager": (
        "Review the monthly delivery forecast",
        "Approve the outstanding resource requests",
        "Confirm priorities for the leadership briefing",
        "Review this week's staffing coverage",
        "Prepare the operations review agenda",
        "Resolve outstanding delivery risks",
        "Review the department improvement plan",
        "Update the quarterly planning notes",
        "Capture ideas for the next process review",
        "Confirm the department escalation contacts",
        "Review the previous reporting period",
        "Archive superseded planning notes",
    ),
    "administrator": (
        "Review outstanding account access requests",
        "Update the account administration checklist",
        "Review the access audit summary",
        "Confirm the latest backup verification",
        "Prepare the permissions review notes",
        "Review inactive account recommendations",
        "Update the internal support guide",
        "Organise administration reference notes",
        "Record improvements to the onboarding workflow",
        "Verify the standard employee role permissions",
        "Review the account recovery procedure",
        "Archive superseded administration notes",
    ),
}

# (priority, days from the chosen date, completed). None means no due date.
TASK_DETAILS = (
    ("high", -3, 0),
    ("normal", -1, 0),
    ("high", 0, 0),
    ("normal", 0, 0),
    ("normal", 1, 0),
    ("high", 3, 0),
    ("normal", 7, 0),
    ("low", 14, 0),
    ("low", None, 0),
    ("high", -5, 1),
    ("normal", -2, 1),
    ("low", None, 1),
)


def seed_demo_tasks(database_path, demo_date=DEMO_DATE, refresh_dates=False):
    """Return (added, dates_updated, accounts_found, backup_path)."""
    database_path = Path(database_path).resolve()
    if not database_path.is_file():
        raise FileNotFoundError(f"App database not found: {database_path}")

    # mode=rw prevents a mistyped path from silently creating an empty database.
    with closing(sqlite3.connect(database_path.as_uri() + "?mode=rw", uri=True)) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        columns = {row[1] for row in connection.execute("PRAGMA table_info(personal_tasks)")}
        required = {"id", "employee_id", "title", "completed", "priority", "due_date"}
        if not required <= columns:
            raise ValueError("Open the updated app and visit Personal To-do once before seeding demo tasks.")

        accounts = connection.execute("""
            SELECT e.id, r.name
            FROM employees e JOIN roles r ON r.id = e.role_id
            ORDER BY e.id
        """).fetchall()
        existing = {
            (employee_id, title): (task_id, due_date)
            for task_id, employee_id, title, due_date in connection.execute(
                "SELECT id, employee_id, title, due_date FROM personal_tasks"
            )
        }
        tasks = []
        date_updates = []
        for employee_id, role in accounts:
            titles = TASK_TITLES.get(role, TASK_TITLES["employee"])
            for title, (priority, offset, completed) in zip(titles, TASK_DETAILS, strict=True):
                due_date = (demo_date + timedelta(days=offset)).isoformat() if offset is not None else None
                saved_task = existing.get((employee_id, title))
                if saved_task is None:
                    tasks.append((employee_id, title, completed, priority, due_date))
                elif refresh_dates and saved_task[1] != due_date:
                    date_updates.append((due_date, saved_task[0], employee_id, title))

        if not tasks and not date_updates:
            return 0, 0, len(accounts), None

        backup_folder = database_path.parent / "backups"
        backup_folder.mkdir(exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup_path = backup_folder / f"before-demo-tasks-{stamp}.sqlite3"
        with closing(sqlite3.connect(backup_path)) as backup:
            connection.backup(backup)
            if backup.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                raise ValueError("Database backup verification failed; no tasks were changed.")

        added = 0
        updated = 0
        with connection:
            for employee_id, title, completed, priority, due_date in tasks:
                cursor = connection.execute("""
                    INSERT INTO personal_tasks (employee_id, title, completed, priority, due_date)
                    SELECT ?, ?, ?, ?, ?
                    WHERE NOT EXISTS (
                        SELECT 1 FROM personal_tasks WHERE employee_id = ? AND title = ?
                    )
                """, (employee_id, title, completed, priority, due_date, employee_id, title))
                added += cursor.rowcount
            for values in date_updates:
                cursor = connection.execute("""
                    UPDATE personal_tasks SET due_date = ?
                    WHERE id = ? AND employee_id = ? AND title = ?
                """, values)
                updated += cursor.rowcount
        return added, updated, len(accounts), backup_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path,
                        default=Path(__file__).resolve().parent / "database" / "database.db")
    parser.add_argument("--date", type=date.fromisoformat, default=DEMO_DATE,
                        help="Base date for deadlines, YYYY-MM-DD; defaults to 2026-11-03.")
    parser.add_argument("--refresh-dates", action="store_true",
                        help="Update deadlines of matching demo tasks; keep their other details.")
    args = parser.parse_args()
    try:
        added, updated, accounts, backup = seed_demo_tasks(args.database, args.date, args.refresh_dates)
    except (sqlite3.Error, OSError, ValueError) as error:
        parser.exit(1, f"Could not add demo tasks: {error}\n")
    print(f"Added {added} demo tasks and updated {updated} deadlines across {accounts} accounts.")
    print(f"Demo date: {args.date.isoformat()}")
    if backup:
        print(f"Database backup: {backup}")
    else:
        print("Matching examples already exist; no changes were needed. Use --refresh-dates to update their deadlines.")


if __name__ == "__main__":
    main()
