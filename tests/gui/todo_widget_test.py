"""Exercise the reusable component with its real backend and an alternative."""

from datetime import date, timedelta

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QPushButton

from app.todo_widget import TaskForm, create_todo_widget
from authentication.login_backend import login_user


def task_ids(widget):
    return [widget.rows_layout.itemAt(i).widget().property("task_id")
            for i in range(widget.rows_layout.count())
            if widget.rows_layout.itemAt(i).widget().property("task_id") is not None]


def test_add_edit_complete_and_restore_through_the_widget(qt_application, db, monkeypatch):
    db.add_employee("Alex", "Smith", "alex@makeitall.com", "alex", "Password1!")
    user = login_user("alex@makeitall.com", "Password1!")
    widget = create_todo_widget(user)
    changes = []
    widget.tasks_changed.connect(lambda: changes.append(True))
    widget.show_task_entry()
    widget.form.title_input.setText("Write report")
    widget.form.priority_input.setCurrentIndex(widget.form.priority_input.findData("high"))
    widget.form.has_due_date.setChecked(True)
    widget.form.date_input.setDate(QDate.currentDate().addDays(2))
    widget.add_task()
    task = db.personal_task_data(user, "load")[0]
    assert task[1:] == ("Write report", 0, "high", (date.today() + timedelta(days=2)).isoformat())

    def edit_dialog(dialog):
        form = dialog.findChild(TaskForm)
        assert form.values()["priority"] == "high"
        assert form.has_due_date.isChecked()
        form.title_input.setText("Revised report")
        form.priority_input.setCurrentIndex(form.priority_input.findData("low"))
        form.has_due_date.setChecked(False)
        dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Save).click()
        return QDialog.DialogCode.Accepted

    monkeypatch.setattr(QDialog, "exec", edit_dialog)
    widget.edit_task(task)
    assert db.personal_task_data(user, "load")[0][1:] == ("Revised report", 0, "low", None)
    widget.rows_layout.itemAt(0).widget().findChild(QPushButton, "taskCheck").click()
    assert task_ids(widget) == []
    widget.completed_button.click()
    widget.rows_layout.itemAt(0).widget().findChild(QPushButton, "taskCheck").click()
    assert db.personal_task_data(user, "load")[0][2] == 0
    assert len(changes) == 4
    reopened = create_todo_widget(user)
    assert task_ids(reopened) == [task[0]]
    widget.close()
    reopened.close()


def test_alternative_backend_sorting_and_overdue_display(qt_application):
    today = date.today()
    rows = [
        (1, "Later, high", 0, "high", (today + timedelta(days=5)).isoformat()),
        (2, "Today, low", 0, "low", today.isoformat()),
        (3, "Overdue", 0, "normal", (today - timedelta(days=2)).isoformat()),
        (4, "No date", 0, "normal", None),
        (5, "Finished", 1, "high", (today - timedelta(days=1)).isoformat()),
    ]
    user = {"id": 42}
    calls = []

    def project_tasks(acting_user, action, **values):
        calls.append((acting_user, action, values))
        return rows if action == "load" else None

    widget = create_todo_widget(user, task_data=project_tasks,
                                title="Project tasks", subtitle="Paper sales")
    assert task_ids(widget) == [3, 2, 1, 4]
    assert widget.active_button.text() == "Active  4"
    assert "Overdue · 1" in [label.text() for label in widget.findChildren(QLabel, "taskSection")]
    assert widget.due_date_text(rows[2][4], False) == "2 days overdue"
    assert widget.due_date_text(today.isoformat(), False) == "Today"
    assert widget.due_date_text((today + timedelta(days=1)).isoformat(), False) == "Tomorrow"
    widget.sort_input.setCurrentIndex(1)
    assert task_ids(widget) == [3, 1, 4, 2]
    widget.completed_button.click()
    assert task_ids(widget) == [5]
    assert "overdue" not in widget.due_date_text(rows[4][4], True)
    widget.save_change("edit", task_id=1, title="Updated", priority="low", due_date=None)
    assert calls[-2] == (user, "edit", {"task_id": 1, "title": "Updated", "priority": "low", "due_date": None})
    assert all(call[0] is user for call in calls)
    widget.close()


def test_permission_failure_is_shown_without_an_add_form(qt_application, db):
    widget = create_todo_widget(None)
    assert "cannot manage" in widget.message.text()
    assert widget.add_link.isHidden()
    assert widget.entry.isHidden()
    widget.close()
