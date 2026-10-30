"""Shared test setup.

The `db` fixture gives every test its own empty database in a temporary
folder, so tests never touch database/database.db.
"""

from datetime import date, timedelta

import pytest

import database.database as database_module


@pytest.fixture(scope="session")
def qt_application():
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])

PASSWORD = "Password1!"  # meets check_strong_password()


@pytest.fixture()
def db(tmp_path, monkeypatch):
    """A fresh database with roles and permissions seeded, in a temp folder."""
    monkeypatch.setattr(database_module, "database_connection", str(tmp_path / "test.db"))
    database_module.create_tables()

    # create_tables() doesn't create the projects tables yet (task F1), but the
    # dashboards read them. Create them here. Harmless once F1 is done.
    connection = database_module.get_database_connection()
    connection.executescript("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            description TEXT,
            manager_id INTEGER,
            status TEXT
        );
        CREATE TABLE IF NOT EXISTS project_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            employee_id INTEGER
        );
    """)
    connection.close()
    return database_module


@pytest.fixture()
def accounts(db):
    """One account per role plus a sample project.

    Returns {role: (email, password)}.
    """
    people = [
        ("Alex", "Smith", "alex.smith@makeitall.com", "alex_smith", "employee"),
        ("John", "Paul", "john.paul@makeitall.com", "john_paul", "team leader"),
        ("Sarah", "Jones", "sarah.jones@makeitall.com", "sarah_jones", "manager"),
        ("Admin", "One", "admin@makeitall.com", "admin", "administrator"),
    ]
    ids = {}
    result = {}
    for first, second, email, username, role in people:
        ids[role] = db.add_employee(first, second, email, username, PASSWORD, role=role)
        result[role] = (email, PASSWORD)

    connection = db.get_database_connection()
    today = date.today()
    cursor = connection.execute(
        "INSERT INTO projects (project_name, description, manager_id, status, start_date, deadline) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("Website", "Rebuild the company website", ids["manager"], "in progress",
         today.isoformat(), (today + timedelta(days=30)).isoformat()),
    )
    connection.execute(
        "INSERT INTO project_members (project_id, employee_id) VALUES (?, ?)",
        (cursor.lastrowid, ids["employee"]),
    )
    connection.commit()
    connection.close()
    return result
