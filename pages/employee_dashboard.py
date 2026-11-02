from datetime import date

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
    QScrollArea
)
from PySide6.QtCore import Qt

from app import colors
from app.donut_chart import StatusOverviewCard
from database.database import get_projects_for_employee, get_tasks_for_user

# Project rows come from SELECT projects.*, so the columns are:
# [0] id, [1] project_name, [2] description, [3] manager_id,
# [4] status, [5] start_date, [6] deadline
DEADLINE_INDEX = 6

# The overdue section lists at most this many tasks, then shows "+ N more".
MAX_OVERDUE_SHOWN = 8

TODAY = date.today()


def load_tasks(user):
    """Unfinished tasks for this user, as dicts the dashboard can use.

    get_tasks_for_user() returns rows shaped like:
    (source, id, title, project_name, due_date)
    where source is 'project' or 'personal' and due_date is 'YYYY-MM-DD' or None.
    """
    tasks = []
    for source, task_id, title, project_name, due_date in get_tasks_for_user(user):
        if source == "personal":
            continue  # project tasks only
        tasks.append({
            "source": source,
            "id": task_id,
            "title": title,
            "project": project_name or "Personal task",
            "due": date.fromisoformat(due_date) if due_date else None,
        })
    return tasks


def get_highest_priority_project(projects):
    """The project with the nearest deadline.

    The projects table has no priority column, so the nearest deadline stands
    in for priority. Swap the key below if you add a priority field later.
    """
    if not projects:
        return None
    return min(projects, key=lambda p: p[DEADLINE_INDEX])


def clear_layout(layout):
    """Remove and delete everything inside a layout, including nested layouts."""
    while layout.count():
        item = layout.takeAt(0)
        if item.widget() is not None:
            item.widget().hide()  # gone from the screen straight away
            item.widget().deleteLater()
        elif item.layout() is not None:
            clear_layout(item.layout())
            item.layout().deleteLater()


class EmployeeDashboard(QWidget):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.setup_ui()

    def setup_ui(self):
        # outer page container to hold scroll bar
        scroll_layout = QVBoxLayout(self)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: #f3f5f8; border: none; }")
        scroll.viewport().setAutoFillBackground(False)
        scroll_layout.addWidget(scroll)

        # put page contents into scroll area
        content = QWidget()
        content.setAutoFillBackground(False)
        content.setObjectName("employee_dashboard_content")
        content.setStyleSheet("#employee_dashboard_content { background: #f3f5f8; }")
        scroll.setWidget(content)

        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(28, 26, 28, 24)
        self.content_layout.setSpacing(20)

        self.refresh_content()

    def on_show(self):
        """Called by MainWindow every time the Dashboard page is opened."""
        self.refresh_content()

    def refresh_content(self):
        """Reload projects and tasks from the database and rebuild every section."""
        global TODAY
        TODAY = date.today()  # keeps "overdue" correct if the app stays open overnight

        clear_layout(self.content_layout)
        projects = get_projects_for_employee(self.user["id"])
        self.tasks = load_tasks(self.user)

        # Sections appear top to bottom in this order. Move a line to move a section.
        self.build_header()
        self.build_overdue_section()
        self.build_overview(projects)
        self.build_priority_section(projects)
        self.build_project_todo_section()
        self.content_layout.addStretch()  # keeps cards at their natural height

    # HEADER

    def build_header(self):
        overdue_count = len([t for t in self.tasks if t["due"] and t["due"] < TODAY])

        # left: big welcome + subtitle (stacked)
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        title = QLabel(f"Welcome back, {self.user['first_name']}")
        title.setObjectName("PageTitle")
        title.setStyleSheet("#PageTitle { font-size: 40px; font-weight: bold; }")
        text_layout.addWidget(title)

        subtitle = QLabel(f"You have {overdue_count} task{'s' if overdue_count != 1 else ''} overdue.")
        subtitle.setObjectName("pageSubtitle")
        subtitle.setStyleSheet("#pageSubtitle { font-size: 20px; font-weight: bold; }")
        text_layout.addWidget(subtitle)

        # right: today's date
        date_label = QLabel(TODAY.strftime("%A\n%d %B %Y"))
        date_label.setObjectName("pageDate")
        date_label.setStyleSheet("#pageDate { font-size: 16px; color: #5a6b75; }")
        date_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        header = QHBoxLayout()
        header.addLayout(text_layout, 1)
        header.addWidget(date_label)
        self.content_layout.addLayout(header)

    # OVERDUE TASKS

    def build_overdue_section(self):
        """A highlighted card listing overdue tasks, most overdue first."""
        overdue = sorted(
            [t for t in self.tasks if t["due"] and t["due"] < TODAY],
            key=lambda t: t["due"],
        )

        # Nothing overdue: a calm green card instead of a red one.
        if not overdue:
            card, layout = self.create_list_card("Overdue tasks", "overdueCard")
            card.setStyleSheet(
                f"#overdueCard {{ background: {colors.DONE_TINT}; border: 1px solid {colors.DONE_TEXT}; border-radius: 10px; }}"
            )
            layout.itemAt(0).widget().setStyleSheet(f"color: {colors.DONE_TEXT}; font-weight: bold; font-size: 18px;")
            layout.addWidget(QLabel("You're all caught up. No overdue tasks."))
            self.content_layout.addWidget(card)
            return

        card, layout = self.create_list_card(f"Overdue tasks ({len(overdue)})", "overdueCard")
        card.setStyleSheet(
            f"#overdueCard {{ background: {colors.OVERDUE_TINT}; border: 1px solid {colors.OVERDUE_TEXT}; border-radius: 10px; }}"
        )
        layout.itemAt(0).widget().setStyleSheet(f"color: {colors.OVERDUE_TEXT}; font-weight: bold; font-size: 18px;")

        for task in overdue[:MAX_OVERDUE_SHOWN]:
            days = (TODAY - task["due"]).days
            # show the project and the original due date under the title
            row_task = dict(task, project=f"{task['project']} · due {task['due'].strftime('%a %d %b')}")
            layout.addWidget(
                self.create_task_row(row_task, f"{days} day{'s' if days != 1 else ''} overdue", colors.OVERDUE_TEXT)
            )

        hidden = len(overdue) - MAX_OVERDUE_SHOWN
        if hidden > 0:
            more = QLabel(f"+ {hidden} more overdue")
            more.setStyleSheet(f"color: {colors.OVERDUE_TEXT}; margin-top: 6px;")
            layout.addWidget(more)

        self.content_layout.addWidget(card)

    # OVERVIEW
    def build_overview(self, projects):
        """Two donut cards side by side: projects by status, tasks by due date."""
        not_started = len([p for p in projects if p[4] == "not started"])
        in_progress = len([p for p in projects if p[4] == "in progress"])

        due_dates = [t["due"] for t in self.tasks]
        overdue = len([d for d in due_dates if d and d < TODAY])
        due_today = len([d for d in due_dates if d == TODAY])
        upcoming = len([d for d in due_dates if d and d > TODAY])
        no_date = len([d for d in due_dates if d is None])

        row = QHBoxLayout()
        row.setSpacing(16)
        row.addWidget(StatusOverviewCard(
            "Project status",
            "A snapshot of your projects.",
            [("Not started", not_started, colors.NOT_STARTED),
             ("In progress", in_progress, colors.IN_PROGRESS)],
            "Projects",
        ))
        row.addWidget(StatusOverviewCard(
            "Task overview",
            "Your open tasks by due date.",
            [("Overdue", overdue, colors.OVERDUE), ("Due today", due_today, colors.DUE_SOON),
             ("Upcoming", upcoming, colors.UPCOMING), ("No due date", no_date, colors.NO_DATE)],
            "Tasks",
        ))
        self.content_layout.addLayout(row)

    # HIGHEST PRIORITY PROJECT

    def build_priority_section(self, projects):
        self.content_layout.addWidget(
            self.create_priority_card(get_highest_priority_project(projects))
        )

    def create_priority_card(self, project):
        card = QFrame()
        card.setObjectName("dashboardCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(6)

        heading = QLabel("Highest Priority Project")
        heading.setObjectName("summaryCardTitle")
        layout.addWidget(heading)

        name = QLabel(project[1] if project else "No projects yet")
        name.setObjectName("priorityName")
        name.setStyleSheet("#priorityName { font-size: 20px; font-weight: bold; }")
        name.setWordWrap(True)
        layout.addWidget(name)

        if project:
            deadline = date.fromisoformat(project[DEADLINE_INDEX])
            layout.addWidget(QLabel(f"Status: {project[4]}"))
            layout.addWidget(QLabel(f"Deadline: {deadline.strftime('%a %d %b %Y')}"))
        return card

    # PROJECT TO-DO LIST

    def build_project_todo_section(self):
        """To-do list of project tasks that are not overdue, grouped by due date.

        Personal to-do items are left out; overdue tasks have their own section.
        """
        remaining = [
            t for t in self.tasks
            if t["source"] == "project" and not (t["due"] and t["due"] < TODAY)
        ]
        dated = sorted([t for t in remaining if t["due"]], key=lambda t: t["due"])
        undated = [t for t in remaining if not t["due"]]

        card, layout = self.create_list_card(f"Project to-do ({len(remaining)})", "dashboardCard")

        if not remaining:
            empty = QLabel("No upcoming project tasks.")
            empty.setStyleSheet("color: #5a6b75;")
            layout.addWidget(empty)

        groups = [
            ("Today", lambda d: d == 0),
            ("Tomorrow", lambda d: d == 1),
            ("This week", lambda d: 2 <= d <= 7),
            ("Later", lambda d: d > 7),
        ]
        for name, matches in groups:
            members = [t for t in dated if matches((t["due"] - TODAY).days)]
            if not members:
                continue
            group_label = QLabel(name)
            group_label.setStyleSheet("color: #5a6b75; margin-top: 8px;")
            layout.addWidget(group_label)
            for task in members:
                layout.addWidget(self.create_task_row(task, task["due"].strftime("%a %d %b"), colors.UPCOMING))

        if undated:
            group_label = QLabel("No due date")
            group_label.setStyleSheet("color: #5a6b75; margin-top: 8px;")
            layout.addWidget(group_label)
            for task in undated:
                layout.addWidget(self.create_task_row(task, "", "#5a6b75"))

        self.content_layout.addWidget(card)

    # HELPERS
    def create_list_card(self, heading, object_name):
        card = QFrame()
        card.setObjectName(object_name)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(6)
        heading_label = QLabel(heading)
        heading_label.setObjectName("cardTitle")
        layout.addWidget(heading_label)  # index 0, so callers can restyle it
        return card, layout

    def create_task_row(self, task, due_text, due_color):
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 2, 0, 2)

        left = QVBoxLayout()
        left.setSpacing(0)
        left.addWidget(QLabel(task["title"]))
        project = QLabel(task["project"])
        project.setStyleSheet("color: #5a6b75; font-size: 12px;")
        left.addWidget(project)

        due = QLabel(due_text)
        due.setStyleSheet(f"color: {due_color}; font-weight: bold;")

        row_layout.addLayout(left, 1)
        row_layout.addWidget(due, 0, Qt.AlignmentFlag.AlignTop)
        return row