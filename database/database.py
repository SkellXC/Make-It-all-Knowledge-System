import sqlite3
from authentication.authentication import password_hash
from authentication.permissions import (
    ADMIN_ROLE,
    DEFAULT_ROLE_PERMISSIONS,
    PERMISSIONS,
    ROLES,
    can,
)

database_connection = "database/database.db"

def get_database_connection():
    connection = sqlite3.connect(database_connection)
    # SQLite ignores FOREIGN KEY constraints unless this is switched on,
    # and it has to be done on every new connection.
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

EMPLOYEES_TABLE = """
    CREATE TABLE {name} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    second_name TEXT NOT NULL,
    email TEXT NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    role_id INTEGER NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles(id)
    )
"""

def create_tables():
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    icon TEXT NOT NULL,
    is_locked INTEGER NOT NULL DEFAULT 0
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS role_permissions (
    role_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id),
    FOREIGN KEY (permission_id) REFERENCES permissions(id)
    )
    """)
    seed_roles(cursor)
    sync_permissions(cursor)
    connection.commit()

    # Upgrades an older database (employee_type text) before the
    # CREATE TABLE below, which only creates employees if it's missing.
    migrate_employees_to_role_id(connection)

    cursor.execute(EMPLOYEES_TABLE.format(name="IF NOT EXISTS employees"))



   
    connection.commit()
    connection.close()

def seed_roles(cursor):
    """Make sure the four roles exist with the icons/locks defined in code."""
    for name, icon, is_locked in ROLES:
        cursor.execute("""
        INSERT INTO roles (name, icon, is_locked) VALUES (?,?,?)
        ON CONFLICT(name) DO UPDATE SET
            icon = excluded.icon, is_locked = excluded.is_locked
        """, (name, icon, int(is_locked)))


def sync_permissions(cursor):
    """Make the permissions table match PERMISSIONS in code.

    New permission  -> inserted, and given to the roles in DEFAULT_ROLE_PERMISSIONS.
    Existing        -> description refreshed, role assignments left alone.
    Removed in code -> deleted, along with any role assignments.
    """
    for key, description in PERMISSIONS.items():
        exists = cursor.execute(
            "SELECT 1 FROM permissions WHERE key = ?", (key,)
        ).fetchone()
        if exists:
            cursor.execute(
                "UPDATE permissions SET description = ? WHERE key = ?",
                (description, key))
            continue
        cursor.execute(
            "INSERT INTO permissions (key, description) VALUES (?,?)",
            (key, description))
        for role_name, keys in DEFAULT_ROLE_PERMISSIONS.items():
            if key in keys:
                cursor.execute("""
                INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
                SELECT r.id, p.id FROM roles r, permissions p
                WHERE r.name = ? AND p.key = ?
                """, (role_name, key))

    marks = ",".join("?" * len(PERMISSIONS))
    keys = tuple(PERMISSIONS)
    cursor.execute(f"""
    DELETE FROM role_permissions WHERE permission_id IN
        (SELECT id FROM permissions WHERE key NOT IN ({marks}))
    """, keys)
    cursor.execute(f"DELETE FROM permissions WHERE key NOT IN ({marks})", keys)


def migrate_employees_to_role_id(connection):
    """Rebuild an old employees table (employee_type TEXT) to use role_id.

    SQLite can't alter a CHECK constraint, so the table is rebuilt: create the
    new one, copy rows across, drop the old one, rename. Does nothing if
    employees doesn't exist yet or has already been migrated.
    """
    columns = [row[1] for row in connection.execute("PRAGMA table_info(employees)")]
    if not columns or "role_id" in columns:
        return

    connection.execute("PRAGMA foreign_keys = OFF")  # needed to drop a referenced table
    connection.execute("DROP TABLE IF EXISTS employees_new")
    connection.execute(EMPLOYEES_TABLE.format(name="employees_new"))
    connection.execute("""
    INSERT INTO employees_new
        (id, first_name, second_name, email, username, password, role_id)
    SELECT e.id, e.first_name, e.second_name, e.email, e.username, e.password, r.id
    FROM employees e JOIN roles r ON r.name = e.employee_type
    """)
    connection.execute("DROP TABLE employees")
    connection.execute("ALTER TABLE employees_new RENAME TO employees")
    connection.commit()
    connection.execute("PRAGMA foreign_keys = ON")


def get_all_roles():
    """[(id, name, icon, is_locked), ...] - for the admin screen."""
    connection = get_database_connection()
    rows = connection.execute(
        "SELECT id, name, icon, is_locked FROM roles ORDER BY id"
    ).fetchall()
    connection.close()
    return rows


def get_all_permissions():
    """[(key, description), ...] - for the admin screen."""
    connection = get_database_connection()
    rows = connection.execute(
        "SELECT key, description FROM permissions ORDER BY key"
    ).fetchall()
    connection.close()
    return rows


def get_permissions_for_role(role_name):
    """Set of permission keys for a role. Administrator always gets everything."""
    if role_name == ADMIN_ROLE:
        return set(PERMISSIONS)
    connection = get_database_connection()
    rows = connection.execute("""
    SELECT p.key FROM permissions p
    JOIN role_permissions rp ON rp.permission_id = p.id
    JOIN roles r ON r.id = rp.role_id
    WHERE r.name = ?
    """, (role_name,)).fetchall()
    connection.close()
    return {row[0] for row in rows}


def set_role_permission(acting_user, role_name, permission_key, enabled):
    """Turn one permission on or off for a role. This is the only write path.

    The checks live here, not in the UI, so they can't be bypassed.
    """
    if not can(acting_user, "roles.manage"):
        raise PermissionError("You do not have permission to change roles.")

    connection = get_database_connection()
    try:
        role = connection.execute(
            "SELECT id, is_locked FROM roles WHERE name = ?", (role_name,)
        ).fetchone()
        if role is None:
            raise ValueError(f"Unknown role: {role_name}")
        if role[1] or role_name == ADMIN_ROLE:
            raise PermissionError("This role is locked and cannot be changed.")

        permission = connection.execute(
            "SELECT id FROM permissions WHERE key = ?", (permission_key,)
        ).fetchone()
        if permission is None:
            raise ValueError(f"Unknown permission: {permission_key}")

        if enabled:
            connection.execute(
                "INSERT OR IGNORE INTO role_permissions (role_id, permission_id) VALUES (?,?)",
                (role[0], permission[0]))
        else:
            connection.execute(
                "DELETE FROM role_permissions WHERE role_id = ? AND permission_id = ?",
                (role[0], permission[0]))
        connection.commit()
    finally:
        connection.close()




def get_employee_by_email(email):
    """Returns (id, first, second, email, username, password, role_name, role_icon)."""
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT e.id, e.first_name, e.second_name, e.email, e.username,
           e.password, r.name, r.icon
    FROM employees e
    JOIN roles r ON r.id = e.role_id
    WHERE e.email = ?
    """,
    (email,))
    employee = cursor.fetchone()

    connection.close()

    return employee

def get_projects_for_manager(manager_id):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT * FROM projects WHERE manager_id = ?
    """,(manager_id,))

    projects = cursor.fetchall()

    connection.close()

    return projects 
def get_projects_for_employee(employee_id):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT projects.*
    FROM projects
    JOIN project_members
        ON projects.id = project_members.project_id
    WHERE project_members.employee_id = ?
    """, (employee_id,))

    projects = cursor.fetchall()
    connection.close()

    return projects










###Basis to provide test data for the database for testing purposes
def add_simulated_data_to_db():
    connection = get_database_connection()
    cursor = connection.cursor()
    people = [
        ("Alex", "Smith", "alex.smith@makeitall.com", "alex_smith", "Employee1?", "employee"),
        ("John", "Paul", "john.paul@makeitall.com", "john_paul", "TeamLeader1?", "team leader"),
        ("Sarah", "Jones", "sarah.jones@makeitall.com", "sarah_jones", "Manager1?", "manager"),
        ("Admin", "1", "admin@makeitall.com", "admin", "Administrator1?", "administrator"),
    ]
    for first, second, email, username, password, role in people:
        cursor.execute("""
        INSERT INTO employees (first_name, second_name, email,
        username, password, role_id)
        VALUES (?,?,?,?,?,(SELECT id FROM roles WHERE name = ?))""",
        (first, second, email, username, password_hash(password), role))
    connection.commit()
    connection.close()




create_tables()
"""
Added the simulated once (23.10.2026 15:10 ANORBS), now commented out
employees simulated data
employee - Alex, Smith,Email -  alex.smith@makeitall.com,Username -  alex_smith,Password - Employee1?,Role - employee
teamleader - John, Paul,Email -  john.paul@makeitall.com,Username -  john_paul,Password - TeamLeader1?,Role - team leader
manager - Sarah, Jones, Email - sarah.jones@makeitall.com,Username - sarah_jones,Passowrd - Manager1?,Role - manager
admin - admin, 1, Email - admin@makeitall.com,Username - admin,Password - Administrator1?, Role - administrator
add_simulated_data_to_db() - No need for method to be ran again
projects table data also has been simulated
project members table also been simulated
install db viewer extension to view db
"""
def select_all_data():
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
    SELECT * FROM project_members
    """)
    data = cursor.fetchall()
    return data


