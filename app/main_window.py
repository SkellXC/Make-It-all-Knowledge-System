from PySide6.QtWidgets import (
    QButtonGroup, QFrame, QHBoxLayout, QLabel, QMainWindow,
    QPushButton, QStackedWidget, QVBoxLayout, QWidget,
)

from app.navigation import PAGES, dashboard_for, visible_pages
from pages.login_page import LoginPage


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
        links.extend((page.key, page.label) for page in PAGES)
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

        # The dashboard depends on the role; every other page is shown only if
        # the user has the permission listed for it in app/navigation.py.
        self.add_page("dashboard", dashboard_for(user["role"]))
        for page in visible_pages(self.user):
            self.add_page(page.key, page.widget)

        # Hide sidebar buttons for pages this user can't open.
        for key, button in self.nav_buttons.items():
            button.setVisible(key in self.pages)

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
        if key not in self.pages:
            return  # not available to this user
        self.page_stack.setCurrentWidget(self.pages[key])
