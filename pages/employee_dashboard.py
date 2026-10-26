from PySide6.QtWidgets import QVBoxLayout, QWidget,QLabel,QHBoxLayout,QGridLayout,QFrame
from database.database import get_projects_for_employee


class EmployeeDashboard(QWidget):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.setup_ui()

    def setup_ui(self):
        self.content_layout = QVBoxLayout(self)
        self.content_layout.setContentsMargins(28, 26, 28, 24)
        # Add this module's widgets to self.content_layout.
    from PySide6.QtWidgets import (
    QFrame, QLabel, QVBoxLayout, QWidget,
    QHBoxLayout, QGridLayout
)

from database.database import get_projects_for_employee


class EmployeeDashboard(QWidget):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.setup_ui()

    def setup_ui(self):
        self.content_layout = QVBoxLayout(self)
        self.content_layout.setContentsMargins(28, 26, 28, 24)
        self.content_layout.setSpacing(20)

        title = QLabel("Employee Dashboard")
        title.setObjectName("PageTitle")
        self.content_layout.addWidget(title)

        subtitle = QLabel(
            f"Welcome back, {self.user['first_name']}"
        )
        subtitle.setObjectName("pageSubtitle")
        self.content_layout.addWidget(subtitle)

        # Get this employee's projects
        projects = get_projects_for_employee(self.user["id"])

        # Count project statuses
        active_projects = 0
        completed_projects = 0
        not_started_projects = 0

        for project in projects:
            if project[4] == "in progress":
                active_projects += 1
            elif project[4] == "completed":
                completed_projects += 1
            elif project[4] == "not started":
                not_started_projects += 1

        # Summary cards
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(16)

        projects_card = self.create_summary_card(
            "My Projects",
            len(projects)
        )

        active_card = self.create_summary_card(
            "Active Projects",
            active_projects
        )

        completed_card = self.create_summary_card(
            "Completed Projects",
            completed_projects
        )

        summary_layout.addWidget(projects_card)
        summary_layout.addWidget(active_card)
        summary_layout.addWidget(completed_card)

        self.content_layout.addLayout(summary_layout)
        
        status_title = QLabel("Project Status")
        status_title.setObjectName("sectionTitle")
        self.content_layout.addWidget(status_title)

        status_layout = QHBoxLayout()
        status_layout.setSpacing(2)

        not_started_bar = QLabel("Not Started")
        not_started_bar.setObjectName("statusNotStarted")

        in_progress_bar = QLabel("In Progress")
        in_progress_bar.setObjectName("statusInProgress")

        completed_bar = QLabel("Completed")
        completed_bar.setObjectName("statusCompleted")

        if not_started_projects > 0:
            status_layout.addWidget(
                not_started_bar,
                not_started_projects
            )

        if active_projects > 0:
            status_layout.addWidget(
                in_progress_bar,
                active_projects
            )

        if completed_projects > 0:
            status_layout.addWidget(
                completed_bar,
                completed_projects
            )

        self.content_layout.addLayout(status_layout)

        # Project section
        project_title = QLabel("My Projects")
        project_title.setObjectName("sectionTitle")
        self.content_layout.addWidget(project_title)

        # Two-column project grid
        projects_layout = QGridLayout()
        projects_layout.setSpacing(16)

        for index, project in enumerate(projects):
            project_card = QFrame()
            project_card.setObjectName("dashboardCard")

            project_layout = QVBoxLayout(project_card)
            project_layout.setContentsMargins(20, 16, 20, 16)
            project_layout.setSpacing(8)

            project_name = QLabel(project[1])
            project_name.setObjectName("cardTitle")

            project_description = QLabel(project[2])
            project_description.setWordWrap(True)

            project_status = QLabel(
                f"Status: {project[4]}"
            )

            project_layout.addWidget(project_name)
            project_layout.addWidget(project_description)
            project_layout.addWidget(project_status)

            row = index // 2
            column = index % 2

            projects_layout.addWidget(
                project_card,
                row,
                column
            )

        self.content_layout.addLayout(projects_layout)

    def create_summary_card(self, title, value):
        card = QFrame()
        card.setObjectName("dashboardCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setObjectName("summaryCardTitle")

        value_label = QLabel(str(value))
        value_label.setObjectName("summaryCardValue")

        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)

        return card
