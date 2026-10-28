import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QInputDialog, QLabel, QLayout,
    QLineEdit, QMenu, QMessageBox, QPushButton, QScrollArea,
    QSizePolicy, QToolButton, QVBoxLayout, QWidget,
)

from authentication.permissions import can
from database.database import personal_task_data


class PersonalTasksPage(QWidget):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.show_completed = False
        self.setup_ui()

        if can(self.user, "tasks.manage_own") and self.user.get("id") is not None:
            self.refresh_tasks()

    def setup_ui(self):
        self.setObjectName("todoPage")
        self.setStyleSheet("""
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
                border-radius: 5px; padding: 10px; selection-background-color: #dce8f2; }
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
        """)

        self.content_layout = QVBoxLayout(self)
        self.content_layout.setContentsMargins(40, 40, 40, 24)

        # The page content stops growing on wide windows.
        content = QWidget()
        content.setMaximumWidth(760)
        column = QVBoxLayout(content)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(10)
        content_row = QHBoxLayout()
        content_row.addWidget(content, 1)
        content_row.addStretch()
        self.content_layout.addLayout(content_row)

        title = QLabel("Personal To-do")
        title.setObjectName("todoTitle")
        column.addWidget(title)
        note = QLabel("Private to you")
        note.setObjectName("todoNote")
        column.addWidget(note)
        column.addSpacing(18)

        if not can(self.user, "tasks.manage_own") or self.user.get("id") is None:
            column.addWidget(QLabel("Personal tasks are unavailable for this account."))
            column.addStretch()
            return

        tabs = QHBoxLayout()
        view_bar = QFrame()
        view_bar.setObjectName("viewBar")
        view_layout = QHBoxLayout(view_bar)
        view_layout.setContentsMargins(4, 4, 4, 4)
        view_layout.setSpacing(4)
        self.active_button = QPushButton("Active")
        self.completed_button = QPushButton("Completed")
        for button in (self.active_button, self.completed_button):
            button.setObjectName("viewTab")
            button.setCheckable(True)
            button.setMinimumWidth(130)
            view_layout.addWidget(button)
        tabs.addWidget(view_bar)
        tabs.addStretch()
        column.addLayout(tabs)
        self.active_button.clicked.connect(lambda: self.change_view(False))
        self.completed_button.clicked.connect(lambda: self.change_view(True))

        # One scroll area holds the rows and the small task-entry form.
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        task_content = QWidget()
        task_content.setObjectName("taskContent")
        task_column = QVBoxLayout(task_content)
        task_column.setContentsMargins(0, 0, 8, 0)
        task_column.setSpacing(10)
        task_column.setSizeConstraint(QLayout.SizeConstraint.SetMinAndMaxSize)
        self.task_surface = QFrame()
        self.task_surface.setObjectName("taskSurface")
        self.task_surface.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
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
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Task name")
        self.task_input.setMaxLength(200)
        self.task_input.setAccessibleName("New personal task")
        self.task_input.returnPressed.connect(self.add_task)
        entry_layout.addWidget(self.task_input)

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

    def change_view(self, completed):
        self.show_completed = completed
        self.entry.hide()
        self.refresh_tasks()

    def refresh_tasks(self):
        try:
            rows = personal_task_data(self.user, "load")
        except (sqlite3.Error, PermissionError, ValueError) as error:
            QMessageBox.warning(self, "Personal tasks", str(error))
            return

        completed_count = sum(row[2] for row in rows)
        self.active_button.setText(f"Active  {len(rows) - completed_count}")
        self.completed_button.setText(f"Completed  {completed_count}")
        self.active_button.setChecked(not self.show_completed)
        self.completed_button.setChecked(self.show_completed)

        # Remove the old rows before displaying the current view.
        while self.rows_layout.count():
            row = self.rows_layout.takeAt(0).widget()
            row.hide()
            row.deleteLater()

        visible_count = 0
        for task_id, title, completed in rows:
            if bool(completed) != self.show_completed:
                continue
            self.add_task_row(task_id, title, bool(completed))
            visible_count += 1

        if visible_count:
            last_row = self.rows_layout.itemAt(visible_count - 1).widget()
            last_row.setProperty("last", True)
        self.task_surface.setVisible(visible_count > 0)

        self.empty_label.setText(
            "No completed tasks yet." if self.show_completed
            else "No active tasks. Add one below."
        )
        self.empty_label.setVisible(visible_count == 0)
        self.add_link.setVisible(not self.show_completed and self.entry.isHidden())

    def add_task_row(self, task_id, title, completed):
        row = QFrame()
        row.setObjectName("taskRow")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(18, 16, 12, 16)
        layout.setSpacing(14)

        # A checkable button gives a consistent tick on Windows and macOS.
        checkbox = QPushButton("✓" if completed else "")
        checkbox.setObjectName("taskCheck")
        checkbox.setCheckable(True)
        checkbox.setFixedSize(22, 22)
        checkbox.setChecked(completed)
        checkbox.setAccessibleName(f"Mark {title} as {'active' if completed else 'completed'}")
        # Connect after setChecked(), so loading a row does not save it again.
        checkbox.toggled.connect(
            lambda checked, task=task_id: self.change_completion(task, checked)
        )
        layout.addWidget(checkbox)

        text = QLabel(title)
        text.setObjectName("taskTitle")
        text.setTextFormat(Qt.TextFormat.PlainText)
        text.setWordWrap(True)
        if completed:
            text.setObjectName("doneTask")
            font = text.font()
            font.setStrikeOut(True)
            text.setFont(font)
        layout.addWidget(text, 1)

        menu_button = QToolButton()
        menu_button.setText("⋯")
        menu_button.setAccessibleName(f"Actions for {title}")
        menu_button.setToolTip("Task actions")
        menu = QMenu(menu_button)
        edit = menu.addAction("Edit")
        delete = menu.addAction("Delete")
        edit.triggered.connect(
            lambda checked=False, task=task_id, name=title: self.edit_task(task, name)
        )
        delete.triggered.connect(
            lambda checked=False, task=task_id: self.delete_task(task)
        )
        menu_button.setMenu(menu)
        menu_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        layout.addWidget(menu_button)
        self.rows_layout.addWidget(row)

    def show_task_entry(self):
        self.entry.show()
        self.add_link.hide()
        self.task_input.setFocus()

    def cancel_entry(self):
        self.task_input.clear()
        self.entry.hide()
        self.add_link.show()

    def save_change(self, action, **values):
        """Handle database errors in one place for all task changes."""
        try:
            personal_task_data(self.user, action, **values)
        except (sqlite3.Error, PermissionError, ValueError) as error:
            QMessageBox.warning(self, "Personal tasks", str(error))
            return False
        self.refresh_tasks()
        return True

    def add_task(self):
        if self.save_change("add", title=self.task_input.text()):
            self.task_input.clear()
            self.task_input.setFocus()

    def change_completion(self, task_id, completed):
        if not self.save_change("complete", task_id=task_id, completed=completed):
            # Restore the stored checkbox value if saving failed.
            self.refresh_tasks()

    def edit_task(self, task_id, title):
        new_title, accepted = QInputDialog.getText(
            self, "Edit task", "Task name (up to 200 characters):", text=title
        )
        if accepted:
            self.save_change("edit", task_id=task_id, title=new_title)

    def delete_task(self, task_id):
        answer = QMessageBox.question(
            self, "Delete task", "Delete this personal task?"
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.save_change("delete", task_id=task_id)
