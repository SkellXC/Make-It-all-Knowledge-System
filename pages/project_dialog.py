import sqlite3

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QComboBox, QDateEdit, QDialog, QDialogButtonBox, QFormLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QPlainTextEdit, QVBoxLayout,
)

from database.database import PROJECT_STATUSES, get_all_employees, get_project_members

# Who can be picked as the project manager / ticked as a team member.
MANAGER_ROLES = ("manager", "administrator")
MEMBER_ROLES = ("employee", "team leader")


class ProjectDialog(QDialog):
    """Add a project, or edit one if `project` (a dict from list_projects_for_user) is given.

    on_save(values) is called when Save is pressed. It should call the database
    function and raise ValueError / PermissionError / sqlite3.Error on failure;
    the message is shown in the dialog and the dialog stays open. values() has
    exactly the keyword names add_project and update_project expect.
    """

    def __init__(self, user, on_save, project=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.on_save = on_save
        self.setWindowTitle("Edit project" if project else "Add project")
        self.setMinimumWidth(480)

        # (id, first, second, email, username, password, role_name, role_icon)
        employees = get_all_employees()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)
        form = QFormLayout()
        form.setSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setMaxLength(100)
        self.name_input.setPlaceholderText("Project name")

        self.description_input = QPlainTextEdit()
        self.description_input.setFixedHeight(90)
        self.description_input.setPlaceholderText("What is this project about?")

        self.status_input = QComboBox()
        for status in PROJECT_STATUSES:
            self.status_input.addItem(status.capitalize(), status)

        self.start_input = self.make_date_edit()
        self.deadline_input = self.make_date_edit()

        self.manager_input = QComboBox()
        for employee in employees:
            if employee[6] in MANAGER_ROLES:
                self.manager_input.addItem(f"{employee[1]} {employee[2]} ({employee[6]})", employee[0])

        # Anyone already on the project stays in the list, whatever their role,
        # so saving can never silently drop them.
        current_members = set(get_project_members(project["id"])) if project else set()
        self.members_input = QListWidget()
        self.members_input.setFixedHeight(130)
        for employee in employees:
            if employee[6] in MEMBER_ROLES or employee[0] in current_members:
                item = QListWidgetItem(f"{employee[1]} {employee[2]} ({employee[6]})")
                item.setData(Qt.ItemDataRole.UserRole, employee[0])
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(
                    Qt.CheckState.Checked if employee[0] in current_members
                    else Qt.CheckState.Unchecked)
                self.members_input.addItem(item)

        if project:
            self.name_input.setText(project["project_name"])
            self.description_input.setPlainText(project["description"])
            self.status_input.setCurrentIndex(max(0, self.status_input.findData(project["status"])))
            self.start_input.setDate(QDate.fromString(project["start_date"], "yyyy-MM-dd"))
            self.deadline_input.setDate(QDate.fromString(project["deadline"], "yyyy-MM-dd"))
            manager_index = self.manager_input.findData(project["manager_id"])
        else:
            self.deadline_input.setDate(QDate.currentDate().addMonths(1))
            manager_index = self.manager_input.findData(user.get("id"))
        if manager_index >= 0:
            self.manager_input.setCurrentIndex(manager_index)

        form.addRow("Name", self.name_input)
        form.addRow("Description", self.description_input)
        form.addRow("Status", self.status_input)
        form.addRow("Start date", self.start_input)
        form.addRow("Deadline", self.deadline_input)
        form.addRow("Manager", self.manager_input)
        form.addRow("Team", self.members_input)
        layout.addLayout(form)

        self.error_label = QLabel()
        self.error_label.setWordWrap(True)
        self.error_label.setTextFormat(Qt.TextFormat.PlainText)
        self.error_label.setStyleSheet("color: #b3261e;")
        layout.addWidget(self.error_label)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.name_input.setFocus()

    @staticmethod
    def make_date_edit():
        edit = QDateEdit()
        edit.setCalendarPopup(True)
        edit.setDisplayFormat("dd MMM yyyy")
        edit.setDate(QDate.currentDate())
        return edit

    def values(self):
        member_ids = []
        for row in range(self.members_input.count()):
            item = self.members_input.item(row)
            if item.checkState() == Qt.CheckState.Checked:
                member_ids.append(item.data(Qt.ItemDataRole.UserRole))
        return {
            "project_name": self.name_input.text(),
            "description": self.description_input.toPlainText(),
            "manager_id": self.manager_input.currentData(),
            "status": self.status_input.currentData(),
            "start_date": self.start_input.date().toString("yyyy-MM-dd"),
            "deadline": self.deadline_input.date().toString("yyyy-MM-dd"),
            "member_ids": member_ids,
        }

    def save(self):
        try:
            self.on_save(self.values())
        except (sqlite3.Error, PermissionError, ValueError) as error:
            self.error_label.setText(str(error))
            return
        self.accept()
