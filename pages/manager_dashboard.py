from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from database.database import get_projects_for_manager


class ManagerDashboard(QWidget):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.setup_ui()

    def setup_ui(self):
        self.content_layout = QVBoxLayout(self)
        self.content_layout.setContentsMargins(28, 26, 28, 24)
        self.content_layout.setSpacing(20)

        title = QLabel("Manager Dashboard")
        title.setObjectName("PageTitle")
        self.content_layout.addWidget(title)

        subtitle = QLabel("Monitor project progress and team workload")
        subtitle.setObjectName("pageSubtitle")
        self.content_layout.addWidget(subtitle)

        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(16)

        projects = get_projects_for_manager(self.user["id"])

        active_projects = 0
        not_started_projects = 0
        completed_projects = 0

        for project in projects:
            if project[4] == "not started":
                not_started_projects += 1
            elif project[4] == "in progress":
                active_projects += 1
            elif project[4] == "completed":
                completed_projects += 1

        not_started_projects_card = self.create_summary_card(
            "Unstarted Projects",
            not_started_projects
        )

        active_projects_card = self.create_summary_card(
            "Active Projects",
            active_projects
        )

        completed_projects_card = self.create_summary_card(
            "Completed Projects",
            completed_projects
        )

        team_members_card = self.create_summary_card(
            "Team Members",
            10
        )

        summary_layout.addWidget(not_started_projects_card)
        summary_layout.addWidget(active_projects_card)
        summary_layout.addWidget(completed_projects_card)
        summary_layout.addWidget(team_members_card)

        self.content_layout.addLayout(summary_layout)

        # PROJECT STATUS

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

        # PROJECT PROGRESS

        project_title = QLabel("Project Progress")
        project_title.setObjectName("sectionTitle")
        self.content_layout.addWidget(project_title)

        projects_layout = QGridLayout()
        projects_layout.setSpacing(16)

        for index, project in enumerate(projects):

            project_card = QFrame()
            project_card.setObjectName("dashboardCard")

            project_layout = QVBoxLayout(project_card)

            project_name = QLabel(project[1])
            project_layout.addWidget(project_name)

            project_description = QLabel(project[2])
            project_layout.addWidget(project_description)

            project_status = QLabel(
                f"Status: {project[4]}"
            )
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