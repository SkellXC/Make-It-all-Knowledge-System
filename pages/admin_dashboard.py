from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
    QScrollArea,
)
from PySide6.QtGui import Qt

from database.database import (
    get_all_employees,
    get_all_permissions,
    get_all_roles,
)


class AdminDashboard(QWidget):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.setup_ui()

    def setup_ui(self):
        # scroll bar
        # outer page container to hold scroll bar
        scroll_layout = QVBoxLayout(self)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"QScrollArea {{ background: #f3f5f8; border: none; }}")
        scroll.viewport().setAutoFillBackground(False)
        scroll_layout.addWidget(scroll)

        # put page contents into scroll area
        content = QWidget()
        content.setAutoFillBackground(False)
        content.setObjectName("admin_dashboard_content")
        content.setStyleSheet(f"#admin_dashboard_content {{ background: #f3f5f8; }}")
        scroll.setWidget(content)


        # dashboard
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(28, 26, 28, 24)
        self.content_layout.setSpacing(20)

        title = QLabel("Administrator Dashboard")
        title.setObjectName("PageTitle")
        self.content_layout.addWidget(title)

        subtitle = QLabel(
            f"Welcome back, {self.user['first_name']}. "
            "Use Roles & Permissions to control what each role can do."
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)
        self.content_layout.addWidget(subtitle)

        employees = get_all_employees()
        roles = get_all_roles()
        permissions = get_all_permissions()

        # Summary cards
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(16)
        summary_layout.addWidget(self.create_summary_card("Employees", len(employees)))
        summary_layout.addWidget(self.create_summary_card("Roles", len(roles)))
        summary_layout.addWidget(self.create_summary_card("Permissions", len(permissions)))
        self.content_layout.addLayout(summary_layout)

        # Employees per role. Employee tuple: index 6 is the role name.
        roles_title = QLabel("Employees by Role")
        roles_title.setObjectName("sectionTitle")
        self.content_layout.addWidget(roles_title)

        roles_layout = QGridLayout()
        roles_layout.setSpacing(16)
        for index, (role_id, role_name, icon, is_locked) in enumerate(roles):
            count = sum(1 for employee in employees if employee[6] == role_name)
            roles_layout.addWidget(
                self.create_summary_card(role_name.title(), count),
                index // 2,
                index % 2,
            )
        self.content_layout.addLayout(roles_layout)
        self.content_layout.addStretch()

    def create_summary_card(self, title, value):
        card = QFrame()
        card.setObjectName("dashboardCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setObjectName("summaryCardTitle")

        value_label = QLabel(str(value))
        value_label.setObjectName("summaryCardValue")

        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)

        return card