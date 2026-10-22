from pages.employee_dashboard import EmployeeDashboard
from pages.team_leader_dashboard import TeamLeaderDashboard
from pages.manager_dashboard import ManagerDashboard
from pages.personal_tasks_page import PersonalTasksPage
from pages.project_tasks_page import ProjectTasksPage
from pages.projects_page import ProjectsPage
from pages.knowledge_page import KnowledgePage
from pages.profile_page import ProfilePage


DASHBOARDS = {
    "Employee": EmployeeDashboard,
    "Team Leader": TeamLeaderDashboard,
    "Manager": ManagerDashboard,
}

# Shared pages: key, sidebar label, widget class.
PAGES = [
    ("personal_tasks", "Personal To-do", PersonalTasksPage),
    ("project_tasks", "Project Tasks", ProjectTasksPage),
    ("projects", "Projects", ProjectsPage),
    ("knowledge", "Knowledge Base", KnowledgePage),
    ("profile", "Profile", ProfilePage),
]
