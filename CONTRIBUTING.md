## Roles and permissions

Access control works on **permissions**, not role names. A role is just a named
bundle of permissions, and admins can change what each role has from the
**Roles & Permissions** page. So never write `if user["role"] == "manager"`;
ask whether the user has the permission instead.

### Where things live

| What | Where |
|---|---|
| List of permissions, roles, default grants, `can()` | `authentication/permissions.py` |
| Which role has which permission (stored data) | `role_permissions` table, via `database/database.py` |
| Which pages need which permission | `PAGES` in `app/navigation.py` |
| Admin screen for editing roles | `pages/roles_page.py` |

`user` is the dict returned by `login_user()`. It includes a `permissions` set,
loaded at login. Every page receives its own copy as `self.user`.

### Checking a permission

**Showing or hiding something in a page**

```python
from authentication.permissions import can

if can(self.user, "projects.create"):
    self.content_layout.addWidget(self.create_project_button)
```

**Restricting a whole page**: give it a permission in `app/navigation.py`.
The sidebar button and the page are only created for users who have it.

```python
Page("projects", "Projects", ProjectsPage, "projects.view_own"),
Page("knowledge", "Knowledge Base", KnowledgePage),   # no permission = everyone
```

**Protecting a database function**: hiding a button is not security. Anything
that changes data should check again in the backend, as `set_role_permission()`
does:

```python
def create_project(acting_user, name, ...):
    if not can(acting_user, "projects.create"):
        raise PermissionError("You do not have permission to create projects.")
    ...
```

In the UI, catch `PermissionError` and show the message instead of crashing.

### Adding a new permission

1. Add it to `PERMISSIONS` in `authentication/permissions.py`, using
   `area.action` as the key (for example `"knowledge.edit"`) and a short description.
2. Add it to `DEFAULT_ROLE_PERMISSIONS` for every role that should start with it.
3. Restart the app. The permission is created in the database and granted to those
   roles. It then shows up on the Roles & Permissions page automatically.
4. Use it with `can(...)` in your page, in `PAGES`, and in your backend function.

Things to know:

- **Defaults apply once.** `DEFAULT_ROLE_PERMISSIONS` is only read when a permission
  is first created. Changing the defaults for an existing permission does nothing.
  Use the Roles & Permissions page instead (or delete `database/database.db` to start fresh).
- **Removing a permission** from `PERMISSIONS` deletes it, and every role's grant of it,
  from the database on next start.
- **Changes take effect at next login.** Permissions are read when a user logs in, so
  someone already logged in keeps their old permissions until they log out and back in.
- **Administrator always has every permission** and its role is locked. This is
  hard-coded and never read from the database.
- `permissions.py` must not import from `database/` (the database imports it).

### Current permissions

| Key | Description | Default roles |
|---|---|---|
| `projects.view_own` | View projects you are a member of | employee, team leader, manager |
| `projects.view_all` | View every project | manager |
| `projects.create` | Create projects | manager |
| `projects.assign` | Add or remove project members | manager |
| `tasks.manage_own` | Manage your personal tasks | employee, team leader, manager |
| `tasks.manage_project` | Manage tasks within a project | team leader, manager |
| `roles.manage` | Change which permissions each role has | administrator only |