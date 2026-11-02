from datetime import date

from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette

from app import colors
from app.donut_chart import StatusOverviewCard
from pages.employee_dashboard import EmployeeDashboard
from database.database import (
    get_task_counts_for_team_leader,
    get_team_progress_for_team_leader,
)

CHARTS_PER_ROW = 2


def clear_layout(layout):
    """Remove and delete everything inside a layout, including nested layouts."""
    while layout.count():
        item = layout.takeAt(0)
        if item.widget() is not None:
            item.widget().hide()
            item.widget().deleteLater()
        elif item.layout() is not None:
            clear_layout(item.layout())
            item.layout().deleteLater()


class TeamLeaderView(QWidget):
    """The team leader tab: task progress and people for each project."""

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

        content = QWidget()
        content.setAutoFillBackground(False)
        content.setObjectName("team_leader_dashboard_content")
        content.setStyleSheet("#team_leader_dashboard_content { background: #f3f5f8; }")
        scroll.setWidget(content)

        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(28, 26, 28, 24)
        self.content_layout.setSpacing(20)

        self.refresh_content()

    def on_show(self):
        """Called by MainWindow every time the Dashboard page is opened."""
        self.refresh_content()

    def refresh_content(self):
        """Reload the task counts for this team leader's projects and rebuild every section."""
        clear_layout(self.content_layout)
        self.rows = get_task_counts_for_team_leader(self.user["id"])

        # Group the per-employee rows by project: {project_id: [row, ...]}
        self.team = {}
        for row in get_team_progress_for_team_leader(self.user["id"]):
            self.team.setdefault(row[0], []).append(row[1:])

        self.build_header()
        self.build_project_charts()
        self.content_layout.addStretch()

    # ----------------------------------------------------------------- header
    def build_header(self):
        count = len(self.rows)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        title = QLabel(f"Welcome back, {self.user['first_name']}")
        title.setObjectName("PageTitle")
        title.setStyleSheet("#PageTitle { font-size: 40px; font-weight: bold; }")
        text_layout.addWidget(title)

        subtitle = QLabel(f"You manage {count} project{'s' if count != 1 else ''}.")
        subtitle.setObjectName("pageSubtitle")
        subtitle.setStyleSheet("#pageSubtitle { font-size: 20px; font-weight: bold; }")
        text_layout.addWidget(subtitle)

        date_label = QLabel(date.today().strftime("%A\n%d %B %Y"))
        date_label.setObjectName("pageDate")
        date_label.setStyleSheet("#pageDate { font-size: 16px; color: #5a6b75; }")
        date_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        header = QHBoxLayout()
        header.addLayout(text_layout, 1)
        header.addWidget(date_label)
        self.content_layout.addLayout(header)

    # ----------------------------------------------- task progress per project
    def build_project_charts(self):
        """One donut per managed project: tasks still to do vs tasks done."""
        section_title = QLabel("Task progress by project")
        section_title.setObjectName("sectionTitle")
        section_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.content_layout.addWidget(section_title)

        if not self.rows:
            empty = QLabel("You don't manage any projects yet.")
            empty.setStyleSheet("color: #5a6b75;")
            self.content_layout.addWidget(empty)
            return

        grid = QGridLayout()
        grid.setSpacing(16)
        for column in range(CHARTS_PER_ROW):
            grid.setColumnStretch(column, 1)  # equal widths, even with one project

        for index, (project_id, name, status, deadline, todo, done) in enumerate(self.rows):
            total = todo + done
            due = date.fromisoformat(deadline).strftime("%d %b %Y")
            if total:
                subtitle = f"{todo} of {total} tasks still to do · due {due}"
            else:
                subtitle = f"No tasks yet · due {due}"

            card = StatusOverviewCard(
                name,
                subtitle,
                [("To do", todo, colors.NOT_STARTED), ("Done", done, colors.DONE)],
                "Tasks",  # the number in the middle is the total
            )

            # chart on top, the people on the project underneath
            cell = QVBoxLayout()
            cell.setSpacing(12)
            cell.addWidget(card)
            cell.addWidget(self.create_team_card(self.team.get(project_id, [])))
            cell.addStretch()  # keeps cards at the top when neighbours are taller
            grid.addLayout(cell, index // CHARTS_PER_ROW, index % CHARTS_PER_ROW)

        self.content_layout.addLayout(grid)

    def create_team_card(self, members):
        """Employees on one project, with how many of their own tasks are done."""
        card = QFrame()
        card.setObjectName("dashboardCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        count = len(members)
        heading = QLabel(f"{count} employee{'s' if count != 1 else ''} working on this project")
        heading.setObjectName("cardTitle")
        layout.addWidget(heading)

        if not members:
            empty = QLabel("Nobody is on this project yet.")
            empty.setStyleSheet("color: #5a6b75;")
            layout.addWidget(empty)

        for employee_id, first_name, second_name, assigned, completed in members:
            name = f"{first_name} {second_name}"
            if employee_id == self.user["id"]:
                name += " (you)"
            summary = f"{completed} of {assigned} tasks done" if assigned else "No tasks assigned"

            top = QHBoxLayout()
            top.addWidget(QLabel(name), 1)
            summary_label = QLabel(summary)
            summary_label.setStyleSheet("color: #5a6b75;")
            top.addWidget(summary_label)

            bar = QProgressBar()
            bar.setRange(0, max(assigned, 1))
            bar.setValue(completed)
            bar.setTextVisible(False)
            bar.setFixedHeight(8)
            bar.setStyleSheet(
                f"QProgressBar {{ background: {colors.TRACK}; border: none; border-radius: 4px; }}"
                f"QProgressBar::chunk {{ background: {colors.DONE}; border-radius: 4px; }}"
            )

            person = QVBoxLayout()
            person.setSpacing(4)
            person.addLayout(top)
            person.addWidget(bar)
            layout.addLayout(person)
        return card


TAB_STYLE = """
QTabWidget::pane { border: none; background: #f3f5f8; }
QTabWidget { background: #f3f5f8; }
QTabBar { background: #f3f5f8; }
QTabWidget::tab-bar { left: 28px; }
QTabBar::tab {
    padding: 12px 20px; margin-right: 6px; font-size: 15px; font-weight: bold;
    color: #5a6b75; background: transparent; border-bottom: 3px solid transparent;
}
QTabBar::tab:selected { color: #476da6; border-bottom: 3px solid #476da6; }
QTabBar::tab:hover:!selected { color: #13222b; }
"""


class TeamLeaderDashboard(QWidget):
    """Team leader dashboard with two tabs.

    Team view : the projects they look after (TeamLeaderView above).
    My work   : the normal employee dashboard, for their own tasks.
    """

    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user

        self.team_view = TeamLeaderView(user=user)
        self.my_work_view = EmployeeDashboard(user=user)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(TAB_STYLE)
        # paint the empty strip beside the tabs in the page colour too
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#f3f5f8"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        self.tabs.addTab(self.team_view, "Team view")
        self.tabs.addTab(self.my_work_view, "My work")
        self.tabs.currentChanged.connect(self.refresh_current_tab)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tabs)

    def on_show(self):
        """Called by MainWindow every time the Dashboard page is opened."""
        self.refresh_current_tab()

    def refresh_current_tab(self, *_):
        """Reload whichever tab is on screen, so it never shows stale data."""
        page = self.tabs.currentWidget()
        if hasattr(page, "on_show"):
            page.on_show()