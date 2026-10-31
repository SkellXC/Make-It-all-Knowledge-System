"""Reusable to-do interface. Other pages only need create_todo_widget()."""

import sqlite3
from datetime import date
from pathlib import Path

from PySide6.QtCore import QDate, Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDateEdit, QDialog, QDialogButtonBox, QFrame,
    QGridLayout, QHBoxLayout, QLabel, QLayout, QLineEdit, QMenu, QMessageBox,
    QPushButton, QScrollArea, QSizePolicy, QToolButton, QVBoxLayout, QWidget,
)

from database.database import TASK_PRIORITIES, personal_task_data

# Existing colours are kept here so the component styles only its own children.
TODO_STYLE = """
QLabel, QPushButton, QToolButton, QLineEdit {
    font-size: 14px; font-weight: normal; color: #233b53;
}
QLabel#todoTitle { font-size: 30px; font-weight: 600; color: #17334d; }
QLabel#todoNote { color: #788796; font-size: 13px; }
QLabel#emptyTasks { color: #788796; padding: 16px 0; }
QLabel#taskTitle { font-size: 15px; color: #263e53; }
QLabel#doneTask { font-size: 15px; color: #82909c; }
QPushButton { background: transparent; border: none;
    border-radius: 6px; padding: 8px 14px; }
QPushButton:hover { background: #e8eef3; }
QPushButton:focus { border: 1px solid #8ca7bf; }
QFrame#viewBar { background: #e6ecf2; border-radius: 9px; }
QPushButton#viewTab { color: #738395; padding: 8px 16px;
    border: 1px solid transparent; border-radius: 6px; }
QPushButton#viewTab:checked { background: #ffffff; color: #1b3a56;
    border: 1px solid #d8e1e9; font-weight: 600; }
QPushButton#viewTab:hover:!checked { background: #dce5ee; }
QFrame#taskSurface { background: #ffffff; border: 1px solid #dfe6ed;
    border-radius: 10px; }
QFrame#taskRow { background: transparent; border: none;
    border-bottom: 1px solid #edf1f5; }
QFrame#taskRow[last="true"] { border-bottom: none; }
QPushButton#taskCheck { background: #ffffff; color: #ffffff;
    border: 1px solid #adbdca; border-radius: 6px;
    padding: 0; font-size: 14px; font-weight: bold; }
QPushButton#taskCheck:hover { background: #f0f5fa; border-color: #486c8b; }
QPushButton#taskCheck:checked { background: #294e6e;
    border-color: #294e6e; color: #ffffff; }
QPushButton#taskCheck:checked:hover { background: #1e405c; }
QPushButton#taskCheck:focus { border: 2px solid #7c9bb6; }
QPushButton#addLink { color: #355d7e; text-align: left; padding: 10px 4px; }
QWidget#entryForm { background: white; border: 1px solid #d5e0e9;
    border-radius: 9px; }
QPushButton#saveTask { background: #294e6e; color: white; border-radius: 6px; }
QPushButton#saveTask:hover { background: #1e405c; }
QLineEdit { background: white; border: 1px solid #d5e0e9;
    border-radius: 5px; padding: 10px; selection-background-color: #dce8f2;
    selection-color: #233b53; }
QLineEdit:focus { border-color: #7d9db8; }
QScrollArea { border: none; background: transparent; }
QWidget#taskContent { background: transparent; }
QToolButton { background: transparent; border: none; border-radius: 6px;
    color: #8294a4; font-size: 20px; padding: 3px 8px; }
QToolButton:hover { background: #edf2f6; color: #294e6e; }
QToolButton:focus { border: 1px solid #8ca7bf; }
QToolButton::menu-indicator { image: none; }
QMenu { background: white; color: #243247; border: 1px solid #d5e0e9; }
QMenu::item { padding: 9px 22px; }
QMenu::item:selected { background: #eaf0f5; }
QDialog, QMessageBox {
    background-color: #f3f5f8;
}

QDialog QLabel {
    background: transparent;
    color: #233b53;
}

QDialog QPushButton {
    background: #ffffff;
    color: #233b53;
    border: 1px solid #cbd7e2;
    border-radius: 6px;
    padding: 8px 16px;
    min-width: 60px;
}

QDialog QPushButton:hover {
    background: #e6edf4;
}

QDialog QPushButton:default {
    background: #294e6e;
    color: #ffffff;
    border-color: #294e6e;
}
QLabel { background: transparent; border: none; }
QLabel#taskDate { color: #738395; font-size: 12px; }
QLabel#taskDate[overdue="true"] { color: #b54742; }
QLabel#taskPriority { font-size: 12px; border-radius: 4px; padding: 3px 7px; }
QLabel#taskPriority[priority="low"] { color: #647569; background: #eef4ef; }
QLabel#taskPriority[priority="normal"] { color: #486b8a; background: #edf3f8; }
QLabel#taskPriority[priority="high"] { color: #aa4943; background: #fbeeea; }
QLabel#taskSection { color: #738395; font-size: 12px; font-weight: 600; padding: 12px 18px 4px; }
QLabel#taskSection[overdue="true"], QLabel#taskError { color: #b54742; }
QPushButton#viewTab { padding: 8px 14px; }
QComboBox, QDateEdit, QCheckBox { font-size: 13px; color: #233b53; }
QComboBox, QDateEdit { background: white; border: 1px solid #d5e0e9;
    border-radius: 5px; padding: 9px; padding-right: 24px; selection-background-color: #dce8f2;
    selection-color: #233b53; }
QComboBox::drop-down, QDateEdit::drop-down { border: none; width: 24px; }
QComboBox::down-arrow, QDateEdit::down-arrow { image: url("__TODO_DOWN_ICON__");
    width: 12px; height: 12px; }
QDateEdit:disabled { background: #f3f5f8; color: #8493a1; }
QComboBox QAbstractItemView { background: white; color: #233b53;
    selection-background-color: #e6edf4; selection-color: #233b53; }
QCheckBox::indicator { width: 16px; height: 16px; background: white;
    border: 1px solid #adbdca; border-radius: 4px; }
QCheckBox::indicator:checked { background: #294e6e; border-color: #294e6e;
    image: url("__TODO_CHECK_ICON__"); }
QCalendarWidget QWidget { background: white; color: #233b53; }
QCalendarWidget QToolButton { color: #233b53; background: #edf3f8; font-size: 13px; }
QCalendarWidget QAbstractItemView { background: white; color: #233b53;
    selection-background-color: #294e6e; selection-color: white; }
"""


def create_todo_widget(user, parent=None, *, task_data=personal_task_data,
                       title="Personal To-do", subtitle="Private to you"):
    """Return the entire to-do interface, ready to add to any Qt layout.

    task_data handles load/add/edit/complete/delete like personal_task_data().
    Its load result contains (id, title, completed, priority, due_date) per task.
    Dates use YYYY-MM-DD or None. The backend must check access itself.
    Pass a project backend to display project tasks instead of personal tasks.
    """
    return TodoWidget(user, task_data, title, subtitle, parent)


class TaskForm(QWidget):
    """Use the same fields when adding and editing a task."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(16)
        layout.setVerticalSpacing(8)
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("What needs to be done?")
        self.title_input.setMaxLength(200)
        self.title_input.setAccessibleName("Task name")
        layout.addWidget(self.title_input, 0, 0, 1, 2)
        layout.addWidget(QLabel("Priority"), 1, 0)
        self.priority_input = QComboBox()
        self.priority_input.setAccessibleName("Task priority")
        for priority in TASK_PRIORITIES:
            self.priority_input.addItem(priority.title(), priority)
        layout.addWidget(self.priority_input, 2, 0)
        self.has_due_date = QCheckBox("Set due date")
        layout.addWidget(self.has_due_date, 1, 1)
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("dd MMM yyyy")
        self.date_input.setAccessibleName("Task due date")
        self.has_due_date.toggled.connect(self.date_input.setEnabled)
        layout.addWidget(self.date_input, 2, 1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        self.set_values()

    def set_values(self, title="", priority="normal", due_date=None):
        self.title_input.setText(title)
        self.priority_input.setCurrentIndex(self.priority_input.findData(priority))
        self.date_input.setDate(
            QDate.fromString(due_date, "yyyy-MM-dd") if due_date else QDate.currentDate()
        )
        self.has_due_date.setChecked(due_date is not None)
        self.date_input.setEnabled(due_date is not None)

    def values(self):
        return {
            "title": self.title_input.text(),
            "priority": self.priority_input.currentData(),
            "due_date": self.date_input.date().toString("yyyy-MM-dd")
            if self.has_due_date.isChecked() else None,
        }


class TodoWidget(QWidget):
    # A dashboard can listen to this to refresh its totals after a change.
    tasks_changed = Signal()

    def __init__(self, user, task_data, title, subtitle, parent=None):
        super().__init__(parent)
        self.user = user
        self.task_data = task_data
        self.show_completed = False
        # A timer owned by this widget is cancelled when the widget is deleted.
        self.entry_scroll_timer = QTimer(self)
        self.entry_scroll_timer.setSingleShot(True)
        self.entry_scroll_timer.timeout.connect(self.scroll_to_entry)
        self.setup_ui(title, subtitle)
        self.refresh_tasks()

    def setup_ui(self, title, subtitle):
        self.setObjectName("todoWidget")
        icon_folder = Path(__file__).parent / "icons"
        style = TODO_STYLE.replace("__TODO_CHECK_ICON__", (icon_folder / "todo-check.svg").as_posix())
        style = style.replace("__TODO_DOWN_ICON__", (icon_folder / "todo-down.svg").as_posix())
        self.setStyleSheet(style)
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(10)
        heading = QLabel(title)
        heading.setTextFormat(Qt.TextFormat.PlainText)
        heading.setObjectName("todoTitle")
        column.addWidget(heading)
        note = QLabel(subtitle)
        note.setTextFormat(Qt.TextFormat.PlainText)
        note.setObjectName("todoNote")
        note.setWordWrap(True)
        column.addWidget(note)
        column.addSpacing(12)

        toolbar = QHBoxLayout()
        view_bar = QFrame()
        view_bar.setObjectName("viewBar")
        views = QHBoxLayout(view_bar)
        views.setContentsMargins(4, 4, 4, 4)
        views.setSpacing(4)
        self.active_button = QPushButton("Active")
        self.completed_button = QPushButton("Completed")
        for button in (self.active_button, self.completed_button):
            button.setObjectName("viewTab")
            button.setCheckable(True)
            views.addWidget(button)
        self.active_button.clicked.connect(lambda: self.change_view(False))
        self.completed_button.clicked.connect(lambda: self.change_view(True))
        toolbar.addWidget(view_bar)
        toolbar.addStretch()
        self.sort_input = QComboBox()
        self.sort_input.setAccessibleName("Sort tasks")
        self.sort_input.addItem("Due date", "due_date")
        self.sort_input.addItem("Priority", "priority")
        self.sort_input.currentIndexChanged.connect(self.refresh_tasks)
        toolbar.addWidget(self.sort_input)
        column.addLayout(toolbar)

        self.message = QLabel()
        self.message.setObjectName("taskError")
        self.message.setTextFormat(Qt.TextFormat.PlainText)
        self.message.setWordWrap(True)
        self.message.hide()
        column.addWidget(self.message)
        scroll = QScrollArea()
        self.scroll_area = scroll
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        task_content = QWidget()
        task_content.setObjectName("taskContent")
        task_column = QVBoxLayout(task_content)
        task_column.setContentsMargins(0, 0, 8, 0)
        task_column.setSpacing(10)
        task_column.setSizeConstraint(QLayout.SizeConstraint.SetMinAndMaxSize)
        self.task_surface = QFrame()
        self.task_surface.setObjectName("taskSurface")
        self.task_surface.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.rows_layout = QVBoxLayout(self.task_surface)
        self.rows_layout.setContentsMargins(1, 1, 1, 1)
        self.rows_layout.setSpacing(0)
        task_column.addWidget(self.task_surface)
        self.empty_label = QLabel()
        self.empty_label.setObjectName("emptyTasks")
        task_column.addWidget(self.empty_label)
        self.add_link = QPushButton("+ Add task")
        self.add_link.setObjectName("addLink")
        self.add_link.clicked.connect(self.show_task_entry)
        task_column.addWidget(self.add_link, alignment=Qt.AlignmentFlag.AlignLeft)

        self.entry = QWidget()
        self.entry.setObjectName("entryForm")
        entry_layout = QVBoxLayout(self.entry)
        entry_layout.setContentsMargins(14, 14, 14, 14)
        self.form = TaskForm()
        self.form.title_input.returnPressed.connect(self.add_task)
        entry_layout.addWidget(self.form)
        entry_actions = QHBoxLayout()
        save_button = QPushButton("Add task")
        save_button.setObjectName("saveTask")
        save_button.clicked.connect(self.add_task)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.cancel_entry)
        entry_actions.addWidget(save_button)
        entry_actions.addWidget(cancel_button)
        entry_actions.addStretch()
        entry_layout.addLayout(entry_actions)
        task_column.addWidget(self.entry)
        self.entry.hide()
        task_column.addStretch()
        scroll.setWidget(task_content)
        column.addWidget(scroll, 1)

    def show_message(self, text=""):
        self.message.setText(text)
        self.message.setVisible(bool(text))

    def change_view(self, completed):
        self.show_completed = completed
        self.entry.hide()
        self.refresh_tasks()

    def refresh_tasks(self):
        # Reload from the backend so another page can request fresh data.
        try:
            tasks = list(self.task_data(self.user, "load"))
        except (sqlite3.Error, PermissionError, ValueError) as error:
            self.show_message(str(error))
            self.task_surface.hide()
            self.entry.hide()
            self.add_link.hide()
            self.empty_label.setText("Tasks are unavailable for this account.")
            self.empty_label.show()
            return
        self.show_message()
        completed_count = sum(bool(task[2]) for task in tasks)
        self.active_button.setText(f"Active  {len(tasks) - completed_count}")
        self.completed_button.setText(f"Completed  {completed_count}")
        self.active_button.setChecked(not self.show_completed)
        self.completed_button.setChecked(self.show_completed)
        while self.rows_layout.count():
            item = self.rows_layout.takeAt(0).widget()
            item.hide()
            item.deleteLater()

        tasks = [task for task in tasks if bool(task[2]) == self.show_completed]
        priority_order = {"high": 0, "normal": 1, "low": 2}
        if self.sort_input.currentData() == "priority":
            tasks.sort(key=lambda task: (priority_order[task[3]], task[4] is None, task[4] or "", -task[0]))
        else:
            tasks.sort(key=lambda task: (task[4] is None, task[4] or "", priority_order[task[3]], -task[0]))

        # Keep overdue work together at the top in either active sort order.
        today = date.today().isoformat()
        overdue = []
        remaining = []
        for task in tasks:
            if not task[2] and task[4] and task[4] < today:
                overdue.append(task)
            else:
                remaining.append(task)
        if overdue:
            self.add_section(f"Overdue · {len(overdue)}", overdue=True)
            for task in overdue:
                self.add_task_row(task)
            if remaining:
                self.add_section("Other tasks")
        for task in remaining:
            self.add_task_row(task)
        if tasks:
            self.rows_layout.itemAt(self.rows_layout.count() - 1).widget().setProperty("last", True)
        self.task_surface.setVisible(bool(tasks))
        self.empty_label.setText(
            "No completed tasks yet." if self.show_completed
            else "No active tasks. Add one below."
        )
        self.empty_label.setVisible(not tasks)
        self.add_link.setVisible(not self.show_completed and self.entry.isHidden())

    def add_section(self, title, overdue=False):
        label = QLabel(title)
        label.setObjectName("taskSection")
        label.setProperty("overdue", overdue)
        self.rows_layout.addWidget(label)

    def due_date_text(self, due_date, completed):
        if not due_date:
            return "No due date"
        due = date.fromisoformat(due_date)
        days = (due - date.today()).days
        if completed:
            return f"Due {due.strftime('%d %b %Y')}"
        if days < 0:
            return f"{abs(days)} day{'s' if days != -1 else ''} overdue"
        if days == 0:
            return "Today"
        if days == 1:
            return "Tomorrow"
        return f"In {days} days · {due.strftime('%d %b')}"

    def add_task_row(self, task):
        task_id, title, completed, priority, due_date = task
        row = QFrame()
        row.setObjectName("taskRow")
        row.setProperty("task_id", task_id)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(18, 14, 12, 14)
        layout.setSpacing(14)
        checkbox = QPushButton("✓" if completed else "")
        checkbox.setObjectName("taskCheck")
        checkbox.setCheckable(True)
        checkbox.setFixedSize(22, 22)
        checkbox.setChecked(bool(completed))
        checkbox.setAccessibleName(f"Mark {title} as {'active' if completed else 'completed'}")
        # Each call has its own task_id, captured by these callbacks.
        checkbox.toggled.connect(lambda checked: self.change_completion(task_id, checked))
        layout.addWidget(checkbox)
        details = QVBoxLayout()
        details.setSpacing(6)
        text = QLabel(title)
        text.setObjectName("doneTask" if completed else "taskTitle")
        text.setTextFormat(Qt.TextFormat.PlainText)
        text.setWordWrap(True)
        text.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        if completed:
            font = text.font()
            font.setStrikeOut(True)
            text.setFont(font)
        details.addWidget(text)
        metadata = QHBoxLayout()
        metadata.setSpacing(10)
        badge = QLabel(priority.title())
        badge.setObjectName("taskPriority")
        badge.setProperty("priority", priority)
        metadata.addWidget(badge)
        due_label = QLabel(self.due_date_text(due_date, completed))
        due_label.setObjectName("taskDate")
        due_label.setProperty("overdue", bool(not completed and due_date and due_date < date.today().isoformat()))
        if due_date:
            due_label.setToolTip(f"Due {due_date}")
        metadata.addWidget(due_label)
        metadata.addStretch()
        details.addLayout(metadata)
        layout.addLayout(details, 1)
        menu_button = QToolButton()
        menu_button.setObjectName("taskActions")
        menu_button.setText("⋯")
        menu_button.setAccessibleName(f"Actions for {title}")
        menu = QMenu(menu_button)
        menu.addAction("Edit").triggered.connect(lambda: self.edit_task(task))
        menu.addAction("Delete").triggered.connect(lambda: self.delete_task(task_id))
        menu_button.setMenu(menu)
        menu_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        layout.addWidget(menu_button)
        self.rows_layout.addWidget(row)

    def show_task_entry(self):
        self.entry.show()
        self.add_link.hide()
        self.form.title_input.setFocus()
        # Wait for the form's new size before scrolling it into view.
        self.entry_scroll_timer.start(0)

    def scroll_to_entry(self):
        self.scroll_area.ensureWidgetVisible(self.entry, 0, 12)

    def cancel_entry(self):
        self.form.set_values()
        self.entry.hide()
        self.add_link.show()
        self.show_message()

    def save_change(self, action, **values):
        try:
            self.task_data(self.user, action, **values)
        except (sqlite3.Error, PermissionError, ValueError) as error:
            self.show_message(str(error))
            return False
        self.refresh_tasks()
        self.tasks_changed.emit()
        return True

    def add_task(self):
        if self.save_change("add", **self.form.values()):
            self.form.set_values()
            self.form.title_input.setFocus()

    def change_completion(self, task_id, completed):
        if not self.save_change("complete", task_id=task_id, completed=completed):
            error = self.message.text()
            self.refresh_tasks()
            self.show_message(error)

    def edit_task(self, task):
        task_id, title, _completed, priority, due_date = task
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit task")
        dialog.setMinimumWidth(420)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)
        form = TaskForm()
        form.set_values(title, priority, due_date)
        layout.addWidget(form)
        error = QLabel()
        error.setObjectName("taskError")
        error.setWordWrap(True)
        error.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(error)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        layout.addWidget(buttons)

        def save_edit():
            if self.save_change("edit", task_id=task_id, **form.values()):
                dialog.accept()
            else:
                error.setText(self.message.text())

        buttons.accepted.connect(save_edit)
        buttons.rejected.connect(dialog.reject)
        form.title_input.returnPressed.connect(save_edit)
        form.title_input.setFocus()
        dialog.exec()

    def delete_task(self, task_id):
        answer = QMessageBox.question(
            self, "Delete task", "Delete this task?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.save_change("delete", task_id=task_id)
