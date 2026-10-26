"""Permissions and roles are defined here, in code.

The database only stores *which permissions each role has*. Keeping the list
of permissions in code means a permission can never exist in the database
without something in the program that checks it.

This file must not import from database/ (database.py imports this file).
"""

ADMIN_ROLE = "administrator"

# key -> description shown on the admin screen
PERMISSIONS = {
    "projects.view_own":    "View projects you are a member of",
    "projects.view_all":    "View every project",
    "projects.create":      "Create projects",
    "projects.assign":      "Add or remove project members",
    "tasks.manage_own":     "Manage your personal tasks",
    "tasks.manage_project": "Manage tasks within a project",
    "roles.manage":         "Change which permissions each role has",
}

# (name, icon path, locked). Locked roles can never be edited at runtime.
ROLES = [
    ("employee",      "icons/employee.svg",      False),
    ("team leader",   "icons/team_leader.svg",   False),
    ("manager",       "icons/manager.svg",       False),
    (ADMIN_ROLE,      "icons/administrator.svg", True),
]

# Starting permissions, applied ONCE when a permission is first created.
# After that the admin screen is in charge, so a restart never undoes an
# admin's change. The admin role is not listed: it always has everything.
DEFAULT_ROLE_PERMISSIONS = {
    "employee":    {"projects.view_own", "tasks.manage_own"},
    "team leader": {"projects.view_own", "tasks.manage_own", "tasks.manage_project"},
    "manager":     {"projects.view_own", "projects.view_all", "projects.create",
                    "projects.assign", "tasks.manage_own", "tasks.manage_project"},
}


def can(user, permission):
    """True if this logged-in user (the dict from login_user) has the permission."""
    if not user:
        return False
    if user.get("role") == ADMIN_ROLE:
        return True  # hard-coded: never read from the database
    return permission in user.get("permissions", ())