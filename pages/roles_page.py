from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QScrollArea, QVBoxLayout, QWidget,
)

from authentication.permissions import ADMIN_ROLE
from database.database import (
    get_all_permissions,
    get_all_roles,
    get_permissions_for_role,
    set_role_permission,
)


class RolesPage(QWidget):
    """Admin screen: pick a role on the left, tick its permissions on the right.

    Every tick is saved straight away through set_role_permission(), which does
    the real permission and locked-role checks. This page only displays the
    result; if the database layer refuses, the tick is put back and the reason
    is shown.

    The page is listed in app/navigation.py with the "roles.manage" permission,
    so only users who have it can open it.
    """

    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.current_role = None
        self.locked_roles = {}   # role name -> True if it can't be edited
        self.checkboxes = {}     # permission key -> QCheckBox
        self.setup_ui()

    def setup_ui(self):
        self.content_layout = QVBoxLayout(self)
        self.content_layout.setContentsMargins(28, 26, 28, 24)
        self.content_layout.setSpacing(20)

        title = QLabel("Roles & Permissions")
        title.setObjectName("PageTitle")
        self.content_layout.addWidget(title)

        subtitle = QLabel(
            "Choose what each role can do. Changes save immediately and apply "
            "the next time a user logs in."
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)
        self.content_layout.addWidget(subtitle)

        body = QHBoxLayout()
        body.setSpacing(16)

        self.role_list = QListWidget()
        self.role_list.setObjectName("roleList")
        self.role_list.setFixedWidth(210)
        body.addWidget(self.role_list)
        body.addWidget(self.build_permissions_card(), 1)
        self.content_layout.addLayout(body, 1)

        # Connect after everything exists, then select the first role.
        self.role_list.currentItemChanged.connect(self.show_role)
        self.load_roles()

    def build_permissions_card(self):
        card = QFrame()
        card.setObjectName("dashboardCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        self.role_heading = QLabel()
        self.role_heading.setObjectName("sectionTitle")
        layout.addWidget(self.role_heading)

        self.locked_note = QLabel(
            "This role is locked: it always has every permission and cannot be changed."
        )
        self.locked_note.setObjectName("lockedNote")
        self.locked_note.setWordWrap(True)
        layout.addWidget(self.locked_note)

        self.message = QLabel()
        self.message.setObjectName("rolesMessage")
        self.message.setWordWrap(True)
        layout.addWidget(self.message)

        # Scrolls, so the list can keep growing as teammates add permissions.
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.viewport().setAutoFillBackground(False)

        inner = QWidget()
        inner.setAutoFillBackground(False)
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(2)

        # Permissions come back sorted by key, so "projects.*" etc. sit together.
        group = None
        for key, description in get_all_permissions():
            prefix = key.split(".")[0]
            if prefix != group:
                group = prefix
                heading = QLabel(prefix.replace("_", " ").title())
                heading.setObjectName("permissionGroup")
                inner_layout.addWidget(heading)
            checkbox = QCheckBox(description)
            checkbox.setToolTip(key)
            checkbox.toggled.connect(
                lambda checked, permission_key=key: self.on_toggled(permission_key, checked)
            )
            inner_layout.addWidget(checkbox)
            self.checkboxes[key] = checkbox
        inner_layout.addStretch()

        scroll.setWidget(inner)
        layout.addWidget(scroll, 1)
        return card

    def load_roles(self):
        for role_id, name, icon, is_locked in get_all_roles():
            self.locked_roles[name] = bool(is_locked) or name == ADMIN_ROLE
            item = QListWidgetItem(name.title())
            item.setData(Qt.ItemDataRole.UserRole, name)
            self.role_list.addItem(item)
        if self.role_list.count():
            self.role_list.setCurrentRow(0)

    def show_role(self, current, _previous=None):
        if current is None:
            return
        self.current_role = current.data(Qt.ItemDataRole.UserRole)
        self.role_heading.setText(current.text())
        self.locked_note.setVisible(self.locked_roles[self.current_role])
        self.message.clear()
        self.refresh_checkboxes()

    def refresh_checkboxes(self):
        """Set every tick to what the database says for the selected role."""
        granted = get_permissions_for_role(self.current_role)
        locked = self.locked_roles[self.current_role]
        for key, checkbox in self.checkboxes.items():
            checkbox.blockSignals(True)   # don't trigger a save while loading
            checkbox.setChecked(key in granted)
            checkbox.blockSignals(False)
            checkbox.setEnabled(not locked)

    def on_toggled(self, permission_key, enabled):
        try:
            set_role_permission(self.user, self.current_role, permission_key, enabled)
        except (PermissionError, ValueError) as error:
            self.refresh_checkboxes()   # put the tick back
            self.message.setText(str(error))
            return
        self.message.clear()