# Reusing the to-do widget

`app/todo_widget.py` exposes one function for the entire interface:

```python
from app.todo_widget import create_todo_widget

self.todo = create_todo_widget(self.user, parent=self)
self.content_layout.addWidget(self.todo)
```

This displays the signed-in employee's private personal tasks. The existing
`PersonalTasksPage` is a small wrapper that adds the page margins and width limit.
Other pages can choose their own layout without copying the interface code.

## What is included

- Add, edit, delete, complete and restore tasks.
- Low, Normal and High priority (Normal is the default).
- An optional due date, selected with a calendar.
- Active and Completed views with counts.
- Sorting by due date or priority. Overdue active tasks stay in a separate group
  at the top. Tasks without a date go last when sorting by date.
- Days remaining, Today, Tomorrow and overdue labels. Completed tasks show their
  stored date without being marked overdue.

## Connecting project tasks

The function accepts a different backend and headings:

```python
# project_task_data must be implemented by the projects module.
# It can capture a project_id when the projects page creates it.
self.todo = create_todo_widget(
    self.user,
    parent=self,
    task_data=project_task_data,
    title="Project tasks",
    subtitle="Tasks for this project",
)
self.content_layout.addWidget(self.todo)
```

The supplied backend receives `user`, an action, and keyword arguments:

| Action | Arguments | Result |
| --- | --- | --- |
| `load` | none | List of `(id, title, completed, priority, due_date)` tuples |
| `add` | `title`, `priority`, `due_date` | No return value needed |
| `edit` | `task_id`, `title`, `priority`, `due_date` | No return value needed |
| `complete` | `task_id`, `completed` | No return value needed |
| `delete` | `task_id` | No return value needed |

Priorities are `low`, `normal` or `high`. Dates are `YYYY-MM-DD` strings or `None`.
The backend must validate input and check the user's project membership and
permissions. Raise `PermissionError`, `ValueError` or `sqlite3.Error` for an error
that should be displayed. The widget does not grant project access.

The project backend is an integration point, not included project functionality.
The default backend continues to protect personal task ownership in SQLite.

## Keeping another page up to date

```python
self.todo.tasks_changed.connect(self.refresh_summary)
```

The signal is emitted after a successful change. Call `self.todo.refresh_tasks()`
when another part of the app changes tasks or when returning to a dashboard.

## How the code is divided

- `create_todo_widget()` is the single entry point other pages call.
- `TodoWidget` builds the list, handles buttons and calls the supplied backend.
- `TaskForm` shares the name, priority and date fields between add and edit.
- `personal_task_data()` validates and stores personal tasks. It adds the new
  columns to older databases without deleting tasks, IDs or completion states.

Existing tasks receive Normal priority and no due date. No database reset is
needed. Personal tasks remain separate from project progress.
