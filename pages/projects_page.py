import datetime as dt
from PySide6.QtWidgets import QVBoxLayout, QLayout, QWidget, QGridLayout, QLabel, QProgressBar, QFrame, QPushButton
from PySide6.QtGui import QFont, QFontMetrics, Qt, QPainter, QIcon # Truncate large project descriptions
# Importing necessary data using functions from database.py
from database.database import list_projects_for_user, get_employee_by_id, get_projects_for_employee, get_projects_for_manager

MAX_ROWS = 3
CARD_STYLE = """                    
                    QFrame {
                        background-color: #ffffff; 
                        border-radius: 8px;
                        border: 1px solid #e0e4e8; /* Light gray border */
                    }
                    QLabel {
                        color: #4a5568; /* Readable dark gray for secondary text */
                        font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; 
                        font-size: 13px; 
                        border: none;
                    }
                    QLabel#CardTitle {
                        color: #2d3748; /* Darker, high-contrast text for title */
                        font-size: 15px;
                        font-weight: bold;
                    }
                    QProgressBar {
                        border: none;
                        border-radius: 4px;
                        background-color: #edf2f7; /* Very light gray track */
                        text-align: center;
                        color: #2d3748; 
                        font-size: 11px;
                    }
                    QProgressBar::chunk {
                        background-color: #4285f4; /* Blue matching the dashboard status bar */
                        border-radius: 4px;
                    }
                    QPushButton {
                        text-align: center;
                        color: #dbe4f0;
                        background: #243c5b;
                        border: 1px solid transparent;
                        border-radius: 6px;
                        padding: 11px 13px;
                    }
                    QPushButton:hover { background: #355783; }
                    QPushButton:checked { background: #355783; color: white; }
                    QPushButton:focus { border-color: #91abd0; }
                    QPushButton:disabled { color: #8495ac; }
"""

class ElidedLabel(QLabel): # Overriding QLabel's paintEvent
    def paintEvent(self, event):
        painter = QPainter(self)
        metrics = QFontMetrics(self.font())
        # Calculate elided text based on the label's current width
        elided = metrics.elidedText(self.text(), Qt.TextElideMode.ElideRight, self.width())
        painter.drawText(self.rect(), self.alignment(), elided)

# creating collapsible panel widget for use in ProjectsPage class
# consists of a header button which expands into a frame when clicked
class CollapsiblePanel(QWidget):
    def __init__(self, title, parent=None):
          super().__init__(parent)
          self.is_expanded = True

          # vertical layout
          self.main_layout = QVBoxLayout(self)
          self.main_layout.setContentsMargins(0, 0, 0, 0)
          self.main_layout.setSpacing(0)

          # header button
          self.toggle_button = QPushButton(f"{title}")
          expand_icon = QIcon.fromTheme(QIcon.ThemeIcon.GoDown)
          self.toggle_button.setIcon(expand_icon)
          self.toggle_button.setStyleSheet(""" 
          QPushButton {
                text-align: center;
                color: #dbe4f0;
                background: #243c5b;
                border: 1px solid transparent;                               border-radius: 6px;
                padding: 11px 13px;
             }
             QPushButton:hover { background: #355783; }
          """)
          # frame area
          self.content_area = QFrame()
          self.content_area.setStyleSheet("""
            QFrame {
            border: 1px solid #d2d6da;
            border-top: none; /* Seamless connection to the button */
            border-bottom-left-radius: 4px;
            border-bottom-right-radius: 4px;
            background-color: #ffffff;
            }
            """
          )

          # frame content's layout
          self.content_layout = QVBoxLayout(self.content_area)
          self.content_layout.setContentsMargins(15, 15, 15, 15)

          # add widgets to layout
          self.main_layout.addWidget(self.toggle_button)
          self.main_layout.addWidget(self.content_area)

          # signal
          self.toggle_button.clicked.connect(self.toggle_panel)
    def toggle_panel(self):
        self.is_expanded = not self.is_expanded
        self.content_area.setVisible(self.is_expanded)
        # update icon on button
        icon = QIcon.ThemeIcon.GoDown if self.is_expanded else QIcon.ThemeIcon.GoUp
        self.toggle_button.setIcon(QIcon.fromTheme(icon))

    def addWidget(self, item):
        if isinstance(item, QLayout):
            self.content_layout.addLayout(item)
        else: self.content_layout.addWidget(item)

    def addLayout(self, layout):
        self.content_layout.addLayout(layout)
     
class ProjectsPage(QWidget):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.setup_ui()

    def build_project_card(self, project):
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setStyleSheet(CARD_STYLE)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel(project["project_name"])
        title.setObjectName("CardTitle")

        deadline = QLabel(f"Due {project['deadline']}")
        pending = QLabel(f"{project['pending_tasks']} pending tasks")

        description = ElidedLabel(project['description'])
        description.setMinimumWidth(100)

        progress = QProgressBar()
        progress.setValue(project["progress_percent"])
        progress.setFixedHeight(12)

        view_button = QPushButton("View Project")
        view_button.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.SystemSearch))

        for widget in (title, deadline, pending, description, progress, view_button):
            layout.addWidget(widget)
        layout.addStretch()
        return card
    def build_project_section(self, title, projects):
        panel = CollapsiblePanel(title)
        if not projects:
            panel.addWidget(QLabel("No Projects"))
            return panel

        grid = QGridLayout()
        for index, project in enumerate(projects):
            # top to bottom, then new column
            grid.addWidget(self.build_project_card(project),
            index % MAX_ROWS, index // MAX_ROWS)
        panel.addLayout(grid)
        return panel

    def setup_ui(self):
        self.content_layout = QVBoxLayout(self)
        self.content_layout.setContentsMargins(28, 26, 28, 24)

        # import projects
        employee = get_employee_by_id(self.user["id"])

        # !-- Role Map --!
        # retrieve and store employee role in memory using a 'role map' dictionary, good for scalability
        role_map = {
            1: "employee",
            2: "team leader",
            3: "manager",
            4: "administrator"
        }
        self.current_user_role = role_map.get(employee[6], "employee") # defaults to employee if field is broken
        employee_projects = get_projects_for_employee(self.user["id"])
        employee_projects_in_progress = []
        employee_projects_not_started = []
        for project in employee_projects:
            if (project[4] == "in progress"):
                employee_projects_in_progress.append(project)
            elif (project[4] == "not started"):
                employee_projects_not_started.append(project)
        # instead of repeating if statements to check permissions, permission based access controls (PBAC) will be implemented
        # widgets do not care who the user is, only what the user is allowed to do
        # permissions will be mapped to bools that will be used into PyQt's .setVisible()

        # !-- Permission Map --!
        # permission map is a dictionary of dictionaries
        role_permissions = {
            "employee":{
                "create_project": False,
                "delete_project": False,
                "manage_tasks": False,
                "check_tasks": True,
                "mark_project_completed": False,
            },
            "team leader":{
                "create_project": False, # Assuming managers delegate projects to team leaders
                "delete_project": False,
                "manage_tasks": True,
                "check_tasks": True,
                "mark_project_completed": False, # Assuming team leaders need manager's approval to mark project complete
                    },
            "manager":{
                "create_project": True,
                "delete_project": True,
                "manage_tasks": True,
                "check_tasks": True,
                "mark_project_completed": True,
            },
            "administrator":{
                "create_project": True,
                "delete_project": True,
                "manage_tasks": True,
                "check_tasks": True,
                "mark_project_completed": True,
            }
        }
        self.current_user_role = employee[6] if employee[6] in role_permissions else "employee"

        # attach PBAC's to employee
        self.perms = role_permissions[self.current_user_role]

        projects = list_projects_for_user(self.user)
        in_progress = [p for p in projects if p["status"] == "in progress"]
        not_started = [p for p in projects if p["status"] in "not started"]

        # adding project containers
        self.content_layout.addWidget(self.build_project_section("Projects in progress", in_progress))
        self.content_layout.addWidget(self.build_project_section("Projects not started", not_started))
        self.content_layout.addStretch()

        # Expanded project page
