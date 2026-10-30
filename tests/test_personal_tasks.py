"""Personal task persistence, old database upgrades and ownership checks."""

from contextlib import closing

import pytest


@pytest.fixture()
def task_users(db):
    result = []
    for name in ("Alex", "Sam"):
        employee_id = db.add_employee(
            name, "Smith", f"{name.lower()}@makeitall.com", name.lower(), "Password1!"
        )
        result.append({
            "id": employee_id, "role": "employee", "permissions": {"tasks.manage_own"}
        })
    return result


def test_old_tasks_survive_the_upgrade_and_repeated_loads(db, task_users):
    user = task_users[0]
    with closing(db.get_database_connection()) as connection:
        connection.executescript("""
            CREATE TABLE personal_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0 CHECK (completed IN (0, 1))
            );
        """)
        connection.executemany(
            "INSERT INTO personal_tasks (employee_id, title, completed) VALUES (?, ?, ?)",
            [(user["id"], "Keep this task", 0), (user["id"], "Already done", 1)],
        )
        connection.commit()
    expected = [(1, "Keep this task", 0, "normal", None),
                (2, "Already done", 1, "normal", None)]
    assert db.personal_task_data(user, "load") == expected
    assert db.personal_task_data(user, "load") == expected


def test_task_changes_keep_priority_and_date_until_explicitly_edited(db, task_users):
    user = task_users[0]
    db.personal_task_data(user, "add", title="  Prepare report  ", priority="high", due_date="2026-11-01")
    task_id = db.personal_task_data(user, "load")[0][0]
    db.personal_task_data(user, "complete", task_id=task_id, completed=True)
    assert db.personal_task_data(user, "load") == [(task_id, "Prepare report", 1, "high", "2026-11-01")]
    db.personal_task_data(user, "complete", task_id=task_id, completed=False)
    assert db.personal_task_data(user, "load")[0][2:] == (0, "high", "2026-11-01")
    db.personal_task_data(user, "edit", task_id=task_id, title="Updated report", priority="low", due_date=None)
    assert db.personal_task_data(user, "load") == [(task_id, "Updated report", 0, "low", None)]
    db.personal_task_data(user, "delete", task_id=task_id)
    assert db.personal_task_data(user, "load") == []


@pytest.mark.parametrize("action", ["edit", "complete", "delete"])
def test_another_employee_cannot_change_a_task(db, task_users, action):
    owner, other = task_users
    db.personal_task_data(owner, "add", title="Private task")
    original = db.personal_task_data(owner, "load")
    assert db.personal_task_data(other, "load") == []
    with pytest.raises(ValueError, match="no longer available"):
        db.personal_task_data(other, action, task_id=original[0][0], title="Changed", completed=True)
    assert db.personal_task_data(owner, "load") == original


@pytest.mark.parametrize("values", [
    {"title": " "}, {"title": "x" * 201},
    {"priority": "urgent"}, {"due_date": "2026-02-30"},
    {"due_date": "30/10/2026"}, {"due_date": "20261030"},
])
def test_invalid_details_do_not_change_a_saved_task(db, task_users, values):
    user = task_users[0]
    db.personal_task_data(user, "add", title="Original")
    original = db.personal_task_data(user, "load")
    details = {"title": "Edited", **values}
    with pytest.raises(ValueError):
        db.personal_task_data(user, "edit", task_id=original[0][0], **details)
    assert db.personal_task_data(user, "load") == original


@pytest.mark.parametrize("user", [None, {"id": 1, "permissions": set()},
                                 {"permissions": {"tasks.manage_own"}}])
def test_missing_permission_or_account_is_rejected(db, user):
    with pytest.raises(PermissionError):
        db.personal_task_data(user, "load")
