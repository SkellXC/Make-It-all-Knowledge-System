from PySide6.QtWidgets import QVBoxLayout, QListWidget, QWidget, QPushButton, QLabel, QHBoxLayout, QProgressBar, QDialog
from PySide6.QtGui import QIcon
from app.todo_widget import create_todo_widget
from database.database import (
    project_task_data, get_project_members, get_all_roles,
    update_project, get_project_for_user,
)
from pages.project_dialog import ProjectDialog

# styling
EMPLOYEE_LIST_STYLE = """
    QListWidget {
        background-color: #ffffff;
        border: 1px solid #dce5ee;
        border-radius: 6px;
        padding: 4px;
        outline: none; /* Removes the dotted focus outline */
    }
    QListWidget::item {
        color: #4a5568; 
        font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
        font-size: 13.5px;
        padding: 10px 12px;
        border-bottom: 1px solid #edf1f5; /* Subtle separator line */
    }
    QListWidget::item:last {
        border-bottom: none; /* Removes the line under the final item */
    }
    QListWidget::item:hover {
        background-color: #f8fafc; /* Very faint blue-gray on hover */
        border-radius: 4px;
    }
    QListWidget::item:selected {
        background-color: #e2e8f0;
        color: #17334d;
    }
"""
EXPANDED_PAGE_STYLE = """
    QWidget#ExpandedPage {
        background-color: #f3f5f8;
    }
    QLabel {
        color: #4a5568; 
        font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; 
        font-size: 13.5px;
    }
    QLabel#ProjectTitle {
        color: #17334d; /* Matches TodoWidget title */
        font-size: 28px;
        font-weight: 600;
        margin-bottom: 4px;
    }
    QLabel#SectionHeader {
        color: #233b53;
        font-size: 14px;
        font-weight: bold;
        margin-top: 12px;
        margin-bottom: 4px;
    }
    QProgressBar {
        border: none;
        border-radius: 5px;
        background-color: #dce5ee; /* Soft gray track */
        text-align: center;
        color: #17334d; 
        font-size: 11px;
        font-weight: bold;
    }
    QProgressBar::chunk {
        background-color: #294e6e; /* Deep blue matching TodoWidget buttons */
        border-radius: 5px;
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
"""

class ExpandedProjectsPage(QWidget):
    def __init__(self, user, project_data, user_perms, parent=None):
        super().__init__(parent)
        self.user = user
        self.project_data = project_data
        self.user_perms = user_perms
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.setObjectName("ExpandedPage") # linking stylsheet
        self.setStyleSheet(EXPANDED_PAGE_STYLE)

        # back to projects overview button
        self.back_button = QPushButton("Back to Overview")
        back_icon = QIcon.fromTheme(QIcon.ThemeIcon.GoPrevious)
        self.back_button.setIcon(back_icon)
        self.back_button.setStyleSheet(EXPANDED_PAGE_STYLE)

        # project details

        # project header section (back button, title, project status, edit button)
        header_layout = QHBoxLayout()
        self.edit_button = QPushButton("Edit Project")
        self.edit_button.setVisible(self.user_perms["create_project"])
        self.edit_button.clicked.connect(self.open_edit_dialog)
        self.edit_button.setStyleSheet(EXPANDED_PAGE_STYLE)

        header_layout.addWidget(self.back_button)
        header_layout.addStretch()
        header_layout.addWidget(self.edit_button)

        self.main_layout.addLayout(header_layout)

        # main project section
        content_split = QHBoxLayout()

        details_column = QVBoxLayout()

        self.project_title = QLabel(self.project_data['project_name'])
        self.project_title.setObjectName("ProjectTitle")

        self.desc_header = QLabel("Description")
        self.desc_header.setObjectName("SectionHeader")

        self.proj_desc = QLabel(self.project_data['description'])
        self.proj_desc.setWordWrap(True)
        
        self.progress_header = (QLabel("Overall Progress"))
        self.progress_header.setObjectName("SectionHeader")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(self.project_data.get("progress_percent", 0))
        self.progress_bar.setFixedHeight(12)

        # listing employees working on the project in a frame
        self.employee_list = QListWidget()
        self.employee_list.setStyleSheet(EMPLOYEE_LIST_STYLE)
        self.fill_member_list()

        details_column.addWidget(self.project_title)
        details_column.addWidget(self.desc_header)
        details_column.addWidget(self.proj_desc)
        details_column.addSpacing(20)
        details_column.addWidget(self.progress_header)
        details_column.addWidget(self.progress_bar)
        details_column.addWidget(self.employee_list)
        details_column.addStretch()

        # employee list will be added to details column soon


        # project tasks column
        tasks_column = QVBoxLayout()

        # function for injecting project id and perms
        def inject_project_id(user, action, **kwargs):
            kwargs['project_id'] = self.project_data['id']
            kwargs['user_perms'] = self.user_perms
            return project_task_data(user, action, **kwargs)

        self.todo = create_todo_widget(
            self.user,
            parent=self,
            title="Project Tasks",
            task_data=inject_project_id,
            subtitle="All your project's tasks, in one place.",
            can_manage=self.user_perms["manage_tasks"],
        )
        self.todo.setMaximumWidth(760)
        # keep the progress bar in step with ticking tasks on and off
        self.todo.tasks_changed.connect(self.refresh_project)
        tasks_column.addWidget(self.todo)

        content_split.addLayout(details_column, 1)
        content_split.addLayout(tasks_column, 2)
        self.main_layout.addLayout(content_split)

    def fill_member_list(self):
        self.employee_list.clear()
        role_map = {role[0]: role[1] for role in get_all_roles()}
        for details in get_project_members(self.project_data["id"]).values():
            role_string = role_map.get(details["role_id"], "Unknown role")
            self.employee_list.addItem(
                f"{role_string}: {details['first_name']} {details['second_name']}, {details['email']}")

    def open_edit_dialog(self):
        dialog = ProjectDialog(
            self.user,
            on_save=lambda values: update_project(self.user, self.project_data["id"], **values),
            project=self.project_data,
            parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_project()

    def refresh_project(self):
        """Reload this project's details, team and progress from the database."""
        fresh = get_project_for_user(self.user, self.project_data["id"])
        if fresh is None:
            return
        self.project_data = fresh
        self.project_title.setText(fresh["project_name"])
        self.proj_desc.setText(fresh["description"])
        self.progress_bar.setValue(fresh["progress_percent"])
        self.fill_member_list()
