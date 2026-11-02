"""Manager dashboard: a "Management view" tab and a "My work" tab.

Self-contained: it only needs
  - app/donut_chart.py            (StatusOverviewCard)
  - pages/employee_dashboard.py   (EmployeeDashboard, used for the My work tab)
  - the two manager queries in database/database.py
"""
from datetime import date

from app.styles import STYLESHEET

from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette

from app import colors
from app.donut_chart import StatusOverviewCard
from pages.employee_dashboard import EmployeeDashboard
from database.database import (
    get_task_counts_for_manager,
    get_team_progress_for_manager,
)

CHARTS_PER_ROW = 2
PAGE_BACKGROUND = "#f3f5f8"

TAB_STYLE = f"""
QTabWidget::pane {{ border: none; background: {PAGE_BACKGROUND}; }}
QTabWidget {{ background: {PAGE_BACKGROUND}; }}
QTabBar {{ background: {PAGE_BACKGROUND}; }}
QTabWidget::tab-bar {{ left: 28px; }}
QTabBar::tab {{
    padding: 12px 20px; margin-right: 6px; font-size: 15px; font-weight: bold;
    color: #5a6b75; background: transparent; border-bottom: 3px solid transparent;
}}
QTabBar::tab:selected {{ color: {colors.ACCENT}; border-bottom: 3px solid {colors.ACCENT}; }}
QTabBar::tab:hover:!selected {{ color: #13222b; }}
"""


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


def progress_bar(completed, assigned):
    """A thin green bar showing completed out of assigned."""
    bar = QProgressBar()
    bar.setRange(0, max(assigned, 1))
    bar.setValue(completed)
    bar.setTextVisible(False)
    bar.setFixedHeight(8)
    bar.setStyleSheet(
        f"QProgressBar {{ background: {colors.TRACK}; border: none; border-radius: 4px; }}"
        f"QProgressBar::chunk {{ background: {colors.DONE}; border-radius: 4px; }}"
    )
    return bar


def white_card():
    card = QFrame()
    card.setObjectName("dashboardCard")
    layout = QVBoxLayout(card)
    layout.setContentsMargins(20, 16, 20, 16)
    layout.setSpacing(10)
    return card, layout


class ManagerView(QWidget):
    """The Management view tab."""

    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.setup_ui()

    def setup_ui(self):
        # outer page container to hold the scroll bar
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(STYLESHEET)
        scroll.viewport().setAutoFillBackground(False)
        outer.addWidget(scroll)

        content = QWidget()
        content.setAutoFillBackground(False)
        content.setObjectName("manager_dashboard_content")
        content.setStyleSheet(f"#manager_dashboard_content {{ background: {PAGE_BACKGROUND}; }}")
        scroll.setWidget(content)

        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(28, 26, 28, 24)
        self.content_layout.setSpacing(20)

        self.refresh_content()

    def on_show(self):
        """Called each time the tab / page is opened, so the data is never stale."""
        self.refresh_content()

    def refresh_content(self):
        clear_layout(self.content_layout)
        self.load_data()
        self.build_header()
        self.build_summary()
        self.build_project_charts()
        self.content_layout.addStretch()

    def load_data(self):
        manager_id = self.user["id"]
        self.rows = get_task_counts_for_manager(manager_id)

        # {project_id: [(employee_id, first, second, assigned, completed, role), ...]}
        self.team = {}
        for row in get_team_progress_for_manager(manager_id):
            self.team.setdefault(row[0], []).append(row[1:])

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

    # ------------------------------------------------ total projects managed
    def build_summary(self):
        total = len(self.rows)
        in_progress = len([r for r in self.rows if r[2] == "in progress"])
        not_started = len([r for r in self.rows if r[2] == "not started"])

        card, layout = white_card()
        layout.setSpacing(4)

        heading = QLabel("Projects under management")
        heading.setObjectName("summaryCardTitle")
        value = QLabel(str(total))
        value.setObjectName("summaryCardValue")
        value.setStyleSheet("font-size: 40px; font-weight: bold;")
        breakdown = QLabel(f"{in_progress} in progress · {not_started} not started")
        breakdown.setStyleSheet("color: #5a6b75;")

        layout.addWidget(heading)
        layout.addWidget(value)
        layout.addWidget(breakdown)
        self.content_layout.addWidget(card)

    # ----------------------------------------------- task progress per project
    def build_project_charts(self):
        """One donut per project (to do vs done) with the people underneath."""
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
            subtitle = (
                f"{done} of {total} tasks done · due {due}" if total
                else f"No tasks yet · due {due}"
            )
            chart = StatusOverviewCard(
                name,
                subtitle,
                [("To do", todo, colors.NOT_STARTED), ("Done", done, colors.DONE)],
                "Tasks",  # the number in the middle is the total
                complete_label="Done",
            )

            cell = QVBoxLayout()
            cell.setSpacing(12)
            cell.addWidget(chart)
            cell.addWidget(self.create_team_card(self.team.get(project_id, [])))
            cell.addStretch()  # keeps cards at the top when neighbours are taller
            grid.addLayout(cell, index // CHARTS_PER_ROW, index % CHARTS_PER_ROW)

        self.content_layout.addLayout(grid)

    def create_team_card(self, members):
        """Everyone on one project, with how many of their own tasks are done."""
        card, layout = white_card()

        count = len(members)
        heading = QLabel(f"{count} employee{'s' if count != 1 else ''} working on this project")
        heading.setObjectName("cardTitle")
        layout.addWidget(heading)

        if not members:
            empty = QLabel("Nobody is on this project yet.")
            empty.setStyleSheet("color: #5a6b75;")
            layout.addWidget(empty)

        for employee_id, first, second, assigned, completed, role in members:
            name = f"{first} {second}"
            if role == "team leader":
                name += " (team leader)"

            top = QHBoxLayout()
            top.addWidget(QLabel(name), 1)
            summary = QLabel(f"{completed} of {assigned} tasks done" if assigned else "No tasks assigned")
            summary.setStyleSheet("color: #5a6b75;")
            top.addWidget(summary)

            person = QVBoxLayout()
            person.setSpacing(4)
            person.addLayout(top)
            person.addWidget(progress_bar(completed, assigned))
            layout.addLayout(person)
        return card


class ManagerDashboard(QWidget):
    """What MainWindow creates for managers: two tabs.

    Management view : projects under management and per-project progress.
    My work         : the normal employee dashboard, for the manager's own tasks.
    """

    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user

        self.management_view = ManagerView(user=user)
        self.my_work_view = EmployeeDashboard(user=user)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(TAB_STYLE)
        self.tabs.addTab(self.management_view, "Management view")
        self.tabs.addTab(self.my_work_view, "My work")
        self.tabs.currentChanged.connect(self.refresh_current_tab)

        # paint the empty strip beside the tabs in the page colour too
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(PAGE_BACKGROUND))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tabs)

    def on_show(self):
        """Called by MainWindow every time the Dashboard page is opened."""
        self.refresh_current_tab()

    def refresh_current_tab(self, *_):
        """Reload whichever tab is on screen."""
        page = self.tabs.currentWidget()
        if hasattr(page, "on_show"):
            page.on_show()