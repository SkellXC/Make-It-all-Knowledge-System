from typing import NamedTuple, Optional

from authentication.permissions import ADMIN_ROLE, can
from pages.admin_dashboard import AdminDashboard
from pages.employee_dashboard import EmployeeDashboard
from pages.team_leader_dashboard import TeamLeaderDashboard
from pages.manager_dashboard import ManagerDashboard
from pages.personal_tasks_page import PersonalTasksPage
from pages.project_tasks_page import ProjectTasksPage
from pages.projects_page import ProjectsPage
from pages.knowledge_page import KnowledgePage
from pages.roles_page import RolesPage
from pages.profile_page import ProfilePage


class Page(NamedTuple):
    key: str                          # internal id, used by show_page()
    label: str                        # text on the sidebar button
    widget: type                      # the page class
    permission: Optional[str] = None  # permission key needed to see it; None = everyone


# Dashboard per role name (the names in authentication/permissions.py ROLES).
DASHBOARDS = {
    "employee": EmployeeDashboard,
    "team leader": TeamLeaderDashboard,
    "manager": ManagerDashboard,
    ADMIN_ROLE: AdminDashboard,
}


def dashboard_for(role):
    """Dashboard class for a role. Unknown roles fall back to the employee one."""
    return DASHBOARDS.get(role, EmployeeDashboard)


# Shared pages, in sidebar order.
# To restrict a page, give it a permission key from authentication/permissions.py.
# The sidebar button and the page are then only created for users who have it.
PAGES = [
    Page("personal_tasks", "Personal To-do", PersonalTasksPage, "tasks.manage_own"),
    Page("project_tasks", "Project Tasks", ProjectTasksPage, "projects.view_own"),
    Page("projects", "Projects", ProjectsPage, "projects.view_own"),
    Page("knowledge", "Knowledge Base", KnowledgePage),
    Page("roles", "Roles & Permissions", RolesPage, "roles.manage"),
    Page("profile", "Profile", ProfilePage),
]


def visible_pages(user):
    """The entries from PAGES this logged-in user is allowed to open."""
    return [
        page for page in PAGES
        if page.permission is None or can(user, page.permission)
    ]