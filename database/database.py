import sqlite3
from contextlib import closing
from datetime import date, timedelta

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

    # Projects, project members and project tasks (upgrades the old projects table).
    create_project_tables(connection)



   
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


def get_employee_by_id(employee_id):
    """Returns (id, first, second, email, username, password, role_name, role_icon) for an employee id."""
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT e.id, e.first_name, e.second_name, e.email, e.username,
           e.password, r.name, r.icon
    FROM employees e
    JOIN roles r ON r.id = e.role_id
    WHERE e.id = ?
    """, (employee_id,))
    employee = cursor.fetchone()

    connection.close()

    return employee


def get_employee(identifier):
    """Gets an employee by ID (int) or email (str).
    
    Returns (id, first, second, email, username, password, role_name, role_icon) or None.
    """
    if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
        return get_employee_by_id(int(identifier))
    return get_employee_by_email(str(identifier))


def get_all_employees():
    """Returns all employees: [(id, first, second, email, username, password, role_name, role_icon), ...]"""
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT e.id, e.first_name, e.second_name, e.email, e.username,
           e.password, r.name, r.icon
    FROM employees e
    JOIN roles r ON r.id = e.role_id
    ORDER BY e.id
    """)
    employees = cursor.fetchall()

    connection.close()

    return employees


def set_employee(first_name, second_name, email, username, password, role="employee", employee_id=None):
    """Adds a new employee or updates an existing employee if employee_id is provided.

    :param first_name: Employee's first name
    :param second_name: Employee's second name (last name)
    :param email: Employee's company email
    :param username: Employee's username
    :param password: Password (plaintext or already hashed)
    :param role: Role name (str, e.g. 'employee', 'manager') or role_id (int)
    :param employee_id: Optional existing employee ID to update. If None, inserts a new employee.
    :return: The employee's ID.
    """
    connection = get_database_connection()
    cursor = connection.cursor()
    try:
        if isinstance(role, int):
            role_row = cursor.execute("SELECT id FROM roles WHERE id = ?", (role,)).fetchone()
        else:
            role_row = cursor.execute("SELECT id FROM roles WHERE name = ?", (role,)).fetchone()

        if role_row is None:
            raise ValueError(f"Role '{role}' does not exist.")

        role_id = role_row[0]

        # Hash password if not already an argon2 hash string
        hashed_password = (
            password
            if isinstance(password, str) and password.startswith("$argon2")
            else password_hash(password)
        )

        if employee_id is None:
            cursor.execute("""
            INSERT INTO employees (first_name, second_name, email, username, password, role_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (first_name, second_name, email, username, hashed_password, role_id))
            emp_id = cursor.lastrowid
        else:
            cursor.execute("""
            UPDATE employees
            SET first_name = ?, second_name = ?, email = ?, username = ?, password = ?, role_id = ?
            WHERE id = ?
            """, (first_name, second_name, email, username, hashed_password, role_id, employee_id))
            emp_id = employee_id

        connection.commit()
        return emp_id
    finally:
        connection.close()


def add_employee(first_name, second_name, email, username, password, role="employee"):
    """Convenience setter to add a new employee to the database and return their new ID."""
    return set_employee(first_name, second_name, email, username, password, role=role)

def remove_employee(employee_id):
    """Removes an employee from the database by their ID."""
    connection = get_database_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
        connection.commit()
    finally:
        connection.close()

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


# ---------------------------------------------------------------------------
# Projects (project_name, description, manager, status, start date, deadline)
# ---------------------------------------------------------------------------
# Only two project states for now. Adding one later means editing this table
# definition (SQLite can't alter a CHECK) and the page's filters.
PROJECTS_TABLE = """
    CREATE TABLE {name} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    manager_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('not started', 'in progress')),
    start_date TEXT NOT NULL,
    deadline TEXT NOT NULL,
    CHECK (deadline >= start_date),
    FOREIGN KEY (manager_id) REFERENCES employees(id)
    )
"""

# Same columns as the existing table, so SELECT * and index-based code keep working.
PROJECT_MEMBERS_TABLE = """
    CREATE TABLE IF NOT EXISTS project_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (employee_id) REFERENCES employees(id)
    )
"""

PROJECT_TASKS_TABLE = """
    CREATE TABLE IF NOT EXISTS project_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    assigned_to INTEGER,
    due_date TEXT,
    completed INTEGER NOT NULL DEFAULT 0 CHECK (completed IN (0, 1)),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES employees(id) ON DELETE SET NULL
    )
"""


def create_project_tables(connection):
    """Make the project tables match the code. Safe to run on every start.

    Old database (projects without start_date/deadline) -> projects is rebuilt
    with the new columns and filled with simulated dates, then simulated
    members and tasks are added for projects that have none.
    """
    connection.commit()
    upgraded = migrate_projects_table(connection)

    connection.execute(PROJECT_MEMBERS_TABLE)
    # An employee can only be on a project once.
    connection.execute("""
    DELETE FROM project_members WHERE id NOT IN
        (SELECT MIN(id) FROM project_members GROUP BY project_id, employee_id)
    """)
    connection.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS idx_project_members_unique
    ON project_members (project_id, employee_id)
    """)
    connection.execute(PROJECT_TASKS_TABLE)
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_project_tasks_project ON project_tasks (project_id)")

    if upgraded:
        add_simulated_project_data(connection)
    connection.commit()


def migrate_projects_table(connection):
    """Rebuild the old projects table to add start_date and deadline.

    Same approach as migrate_employees_to_role_id: create the new table, copy
    the rows across (keeping their ids), drop the old one, rename. Existing
    rows get simulated dates (in progress: started 10-44 days ago, deadline
    still ahead; not started: starts in 5-29 days). Anything that isn't
    'not started' becomes 'in progress', as only those two states exist.

    Returns True if the table was created or rebuilt, False if already up to date.
    """
    columns = [row[1] for row in connection.execute("PRAGMA table_info(projects)")]
    if not columns:
        connection.execute(PROJECTS_TABLE.format(name="projects"))
        return False
    if "start_date" in columns and "deadline" in columns:
        return False

    connection.execute("PRAGMA foreign_keys = OFF")  # needed to drop a referenced table
    try:
        connection.execute("DROP TABLE IF EXISTS projects_new")
        connection.execute(PROJECTS_TABLE.format(name="projects_new"))
        connection.execute("""
        INSERT INTO projects_new
            (id, project_name, description, manager_id, status, start_date, deadline)
        SELECT id, project_name, COALESCE(description, ''), manager_id, new_status,
               start_date, date(start_date, '+' || duration || ' days')
        FROM (
            SELECT id, project_name, description, manager_id, new_status,
                   CASE WHEN new_status = 'in progress'
                        THEN date('now', '-' || (10 + (id * 7) % 35) || ' days')
                        ELSE date('now', '+' || (5 + (id * 5) % 25) || ' days')
                   END AS start_date,
                   45 + (id * 11) % 60 AS duration
            FROM (
                SELECT *, CASE WHEN status = 'not started'
                               THEN 'not started' ELSE 'in progress' END AS new_status
                FROM projects
            )
        )
        """)
        connection.execute("DROP TABLE projects")
        connection.execute("ALTER TABLE projects_new RENAME TO projects")
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.execute("PRAGMA foreign_keys = ON")
    return True


def list_projects_for_user(user):
    """Projects the signed-in user can see, as dicts for the projects page.

    Keys: id, project_name, description, status, start_date, deadline,
    manager_id, pending_tasks, total_tasks, progress_percent.
    Users with projects.view_all see every project; everyone else sees the
    projects they manage or are a member of.
    """
    query = """
    SELECT p.id, p.project_name, p.description, p.status, p.start_date,
           p.deadline, p.manager_id,
           COALESCE(SUM(CASE WHEN t.completed = 0 THEN 1 ELSE 0 END), 0) AS pending_tasks,
           COUNT(t.id) AS total_tasks
    FROM projects p
    LEFT JOIN project_tasks t ON t.project_id = p.id
    """
    params = ()
    if not can(user, "projects.view_all"):
        employee_id = user.get("id")
        if employee_id is None:
            return []
        query += """
        WHERE p.manager_id = ?
           OR p.id IN (SELECT project_id FROM project_members WHERE employee_id = ?)
        """
        params = (employee_id, employee_id)
    query += " GROUP BY p.id ORDER BY p.deadline, p.id"

    with closing(get_database_connection()) as connection:
        cursor = connection.execute(query, params)
        names = [column[0] for column in cursor.description]
        projects = [dict(zip(names, row)) for row in cursor.fetchall()]

    for project in projects:
        total = project["total_tasks"]
        done = total - project["pending_tasks"]
        project["progress_percent"] = round(100 * done / total) if total else 0
    return projects


# Simulated project data (test data only)
SIMULATED_TASK_TITLES = [
    "Gather requirements",
    "Draft project plan",
    "Assign responsibilities",
    "Build first version",
    "Review with stakeholders",
    "Final testing and handover",
]


def add_simulated_project_data(connection):
    """Add test members and tasks to every project that doesn't have any.

    Members are picked from employees and team leaders (never the manager or
    the administrator). In-progress projects get 6 tasks with 1-3 completed;
    not-started projects get 4 pending tasks. Does not commit.
    """
    staff = [row[0] for row in connection.execute("""
        SELECT e.id FROM employees e JOIN roles r ON r.id = e.role_id
        WHERE r.name IN ('employee', 'team leader') ORDER BY e.id
    """)]
    projects = connection.execute("""
        SELECT id, manager_id, status, start_date, deadline FROM projects ORDER BY id
    """).fetchall()

    for project_id, manager_id, status, start_date, deadline in projects:
        pool = [employee for employee in staff if employee != manager_id]
        has_members = connection.execute(
            "SELECT 1 FROM project_members WHERE project_id = ?", (project_id,)).fetchone()
        if pool and not has_members:
            offset = project_id % len(pool)
            for k in range(min(2 + project_id % 2, len(pool))):
                connection.execute("""
                    INSERT OR IGNORE INTO project_members (project_id, employee_id)
                    VALUES (?, ?)
                """, (project_id, pool[(offset + k) % len(pool)]))

        if connection.execute(
                "SELECT 1 FROM project_tasks WHERE project_id = ?", (project_id,)).fetchone():
            continue

        team = [row[0] for row in connection.execute(
            "SELECT employee_id FROM project_members WHERE project_id = ? ORDER BY id",
            (project_id,))] or [manager_id]
        task_count, done_count = (6, 1 + project_id % 3) if status == "in progress" else (4, 0)
        first = date.fromisoformat(start_date)
        span = (date.fromisoformat(deadline) - first).days
        for i in range(task_count):
            due = first + timedelta(days=span * (i + 1) // task_count)
            connection.execute("""
                INSERT INTO project_tasks (project_id, title, assigned_to, due_date, completed)
                VALUES (?, ?, ?, ?, ?)
            """, (project_id, SIMULATED_TASK_TITLES[i], team[i % len(team)],
                  due.isoformat(), int(i < done_count)))



###Basis to provide test data for the database for testing purposes
def add_simulated_data_to_db():
    # Format: first_name, second_name, email, username, password, role
    people = [
        ("Alex", "Smith", "alex.smith@makeitall.com", "alex_smith", "password", "employee"),
        ("John", "Paul", "john.paul@makeitall.com", "john_paul", "password", "team leader"),
        ("Sarah", "Jones", "sarah.jones@makeitall.com", "sarah_jones", "password", "manager"),
        ("Admin", "1", "admin@makeitall.com", "admin", "admin1", "administrator"),
        ("Tony", "Stark", "tony.stark@makeitall.com", "tony_stark", "password", "manager")
    ]
    for first, second, email, username, password, role in people:
        add_employee(first, second, email, username, password, role=role)




create_tables()

def select_all_data():
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
    SELECT * FROM project_members
    """)
    data = cursor.fetchall()
    return data

if __name__ == "__main__":
    # Use this to add simulated data to the database for testing purposes.
    add_employee("Tony", "Stark", "tony.stark@makeitall.com", "tony_stark", "password", "manager")


# Run the file once update the database

# Run python -m database.database  if you get an import error.                              


def personal_task_data(user, action, task_id=None, title="", completed=False):
    """Read or change only the signed-in employee's personal tasks."""
    if not can(user, "tasks.manage_own") or user.get("id") is None:
        raise PermissionError("You cannot manage personal tasks.")

    employee_id = user["id"]
    title = title.strip()

    if action in ("add", "edit") and not 1 <= len(title) <= 200:
        raise ValueError("Enter a task between 1 and 200 characters.")

    # closing() closes the connection; the inner 'with' commits or rolls back.
    with closing(get_database_connection()) as connection:
        with connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS personal_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    completed INTEGER NOT NULL DEFAULT 0
                        CHECK (completed IN (0, 1)),
                    FOREIGN KEY (employee_id) REFERENCES employees(id)
                        ON DELETE CASCADE
                )
            """)

            if action == "load":
                return connection.execute("""
                    SELECT id, title, completed
                    FROM personal_tasks
                    WHERE employee_id = ?
                    ORDER BY completed, id DESC
                """, (employee_id,)).fetchall()

            if action == "add":
                connection.execute("""
                    INSERT INTO personal_tasks (employee_id, title)
                    VALUES (?, ?)
                """, (employee_id, title))

            elif action == "edit":
                connection.execute("""
                    UPDATE personal_tasks
                    SET title = ?
                    WHERE id = ? AND employee_id = ?
                """, (title, task_id, employee_id))

            elif action == "complete":
                connection.execute("""
                    UPDATE personal_tasks
                    SET completed = ?
                    WHERE id = ? AND employee_id = ?
                """, (int(completed), task_id, employee_id))

            elif action == "delete":
                connection.execute("""
                    DELETE FROM personal_tasks
                    WHERE id = ? AND employee_id = ?
                """, (task_id, employee_id))

            else:
                raise ValueError("Unknown task action.")