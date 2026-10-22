

1. Open the folder in your editor.
2. With Python  installed, run these commands from the project folder. Select `.venv/Scripts/python.exe` as your editor's Python interpreter on Windows.

   ```powershell
   py -3 -m venv .venv
   .venv\Scripts\python.exe -m pip install -r requirements.txt
   .venv\Scripts\python.exe main.py
   ```
3. Run `main.py`, log in using a demo account, and open your menu section.


## Suggested ownership

| Developer | Files in pages/ |
| --- | --- |
| 1: authentication/profile | login_page.py, registration_page.py, profile_page.py |
| 2: personal tasks | personal_tasks_page.py |
| 3: project tasks | project_tasks_page.py |
| 4: projects | projects_page.py |
| 5: leadership dashboards | team_leader_dashboard.py, manager_dashboard.py |
| 6: knowledge | knowledge_page.py |
| 7: integration | employee_dashboard.py, plus app/, main.py and tests/ |



For example, to work on Personal To-do, edit only `pages/personal_tasks_page.py`. Add a Qt widget import and place the widget in the existing layout:

```python
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

# Inside the existing setup_ui(), after the layout is created:
self.content_layout.addWidget(QLabel("Personal To-do"))
self.content_layout.addStretch()
```

Do not replace the class or create another window. `setup_ui()` builds your page. Add button handlers as methods in the same class and connect them with `button.clicked.connect(self.method_name)`.

Each workspace page receives `self.user`, for example `{"email": "employee@blablabla", "role": "Employee"}`. Read it when your module needs the signed-in account. Personal tasks must belong to that user and remain separate from project tasks. Do not change the role to grant access.


For a new page, copy an empty workspace page, rename its class, then import it in `app/navigation.py` and add `("unique_key", "Menu label", YourPage)` to `PAGES`. The shell creates its sidebar button automatically. Keep the `(user=None, parent=None)` constructor. `DASHBOARDS` maps the three roles to their dashboard files.




