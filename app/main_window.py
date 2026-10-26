from PySide6.QtWidgets import (
    QButtonGroup, QFrame, QHBoxLayout, QLabel, QMainWindow,
    QPushButton, QStackedWidget, QVBoxLayout, QWidget,
)

from app.navigation import PAGES
from pages.login_page import LoginPage
from pages.employee_dashboard import EmployeeDashboard
from pages.manager_dashboard import ManagerDashboard
from pages.team_leader_dashboard import TeamLeaderDashboard


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MakeItAll")
        self.resize(1100, 700)
        self.setMinimumSize(900, 600)
        self.pages = {}
        self.nav_buttons = {}
        self.user = None

        self.root_stack = QStackedWidget()
        self.setCentralWidget(self.root_stack)
        self.login_page = LoginPage()
        self.login_page.logged_in.connect(self.start_session)
        self.root_stack.addWidget(self.login_page)

        self.workspace = QWidget()
        self.root_stack.addWidget(self.workspace)
        layout = QHBoxLayout(self.workspace)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(205)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 26, 16, 20)
        sidebar_layout.setSpacing(6)
        brand = QLabel("MakeItAll")
        brand.setObjectName("brand")
        sidebar_layout.addWidget(brand)
        sidebar_layout.addSpacing(20)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.page_stack = QStackedWidget()

        links = [("dashboard", "Dashboard")]
        links.extend((key, label) for key, label, page_class in PAGES)
        for key, label in links:
            button = QPushButton(label)
            button.setCheckable(True)
            # Remember each button's page key for later clicks.
            button.clicked.connect(
                lambda checked=False, page_key=key: self.show_page(page_key)
            )
            self.button_group.addButton(button)
            sidebar_layout.addWidget(button)
            self.nav_buttons[key] = button

        sidebar_layout.addStretch()
        self.account_label = QLabel()
        self.account_label.setWordWrap(True)
        sidebar_layout.addWidget(self.account_label)
        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self.logout)
        sidebar_layout.addWidget(self.logout_button)
        layout.addWidget(sidebar)
        layout.addWidget(self.page_stack, 1)
        self.login_page.email_input.setFocus()

    def start_session(self, user):
        self.clear_pages()
        self.user = user.copy()
        role = user["role"]

        if role == "employee":
            dashboard = EmployeeDashboard
        elif role == "manager":
            dashboard = ManagerDashboard
        elif role == "team leader":
            dashboard = TeamLeaderDashboard
        else:
            return 
        self.add_page("dashboard",dashboard)

        for key,label, page_class in PAGES:
            self.add_page(key,page_class)
        self.account_label.setText(f"{user['email']}\n{user['role']}")
        self.login_page.clear_form()
        self.root_stack.setCurrentWidget(self.workspace)
        self.show_page("dashboard")

    def add_page(self, key, page_class):
        page = page_class(user=self.user.copy())
        self.pages[key] = page
        self.page_stack.addWidget(page)

    def clear_pages(self):
        # Rebuild on login so accounts cannot inherit another user's page state.
        for page in self.pages.values():
            self.page_stack.removeWidget(page)
            page.deleteLater()
        self.pages.clear()

    def logout(self):
        self.root_stack.setCurrentWidget(self.login_page)
        self.clear_pages()
        self.user = None
        self.account_label.clear()
        self.login_page.clear_form()
        self.login_page.email_input.setFocus()

    def show_page(self, key):
        self.page_stack.setCurrentWidget(self.pages[key])
        self.nav_buttons[key].setChecked(True)
