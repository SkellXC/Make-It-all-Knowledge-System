import importlib
import os
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from app.main_window import MainWindow
from app.navigation import DASHBOARDS, PAGES
from pages.login_page import DEMO_ACCOUNTS, DEMO_PASSWORD


class ShellTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self):
        self.callback_errors = []
        self.previous_hook = sys.excepthook
        sys.excepthook = lambda kind, error, trace: self.callback_errors.append(error)

    def tearDown(self):
        sys.excepthook = self.previous_hook
        self.assertEqual(self.callback_errors, [])

    def login(self, window, email):
        window.login_page.email_input.setText(email)
        window.login_page.password_input.setText(DEMO_PASSWORD)
        window.login_page.login_button.click()
        self.application.processEvents()
        self.assertIs(window.root_stack.currentWidget(), window.workspace)

    def test_page_stubs(self):
        modules = {
            "registration_page": "RegistrationPage",
            "employee_dashboard": "EmployeeDashboard",
            "team_leader_dashboard": "TeamLeaderDashboard",
            "manager_dashboard": "ManagerDashboard",
            "personal_tasks_page": "PersonalTasksPage",
            "project_tasks_page": "ProjectTasksPage",
            "projects_page": "ProjectsPage",
            "knowledge_page": "KnowledgePage",
            "profile_page": "ProfilePage",
        }
        importlib.import_module("main")
        for module_name, class_name in modules.items():
            module = importlib.import_module(f"pages.{module_name}")
            page = getattr(module, class_name)()
            self.assertEqual(page.layout().count(), 0)
            page.deleteLater()

    def test_role_login_navigation_and_logout(self):
        window = MainWindow()
        try:
            window.show()
            self.assertEqual(window.windowTitle(), "MakeItAll")
            self.assertIs(window.root_stack.currentWidget(), window.login_page)
            for email, role in DEMO_ACCOUNTS.items():
                self.login(window, email)
                self.assertIsInstance(window.pages["dashboard"], DASHBOARDS[role])
                original_pages = window.pages.copy()
                self.assertEqual(window.page_stack.count(), len(PAGES) + 1)
                self.assertEqual(len(window.pages), len(PAGES) + 1)
                for size in [(1100, 700), (900, 600)]:
                    window.resize(*size)
                    for key, button in window.nav_buttons.items():
                        button.click()
                        self.application.processEvents()
                        page = window.page_stack.currentWidget()
                        self.assertIs(page, original_pages[key])
                        self.assertEqual(page.user, {"email": email, "role": role})
                        self.assertEqual(page.layout().count(), 0)
                        self.assertTrue(button.isChecked())
                        self.assertEqual(
                            sum(b.isChecked() for b in window.nav_buttons.values()), 1
                        )
                window.logout_button.click()
                self.assertIs(window.root_stack.currentWidget(), window.login_page)
                self.assertEqual(window.page_stack.count(), 0)
                self.assertEqual(window.pages, {})
                self.assertIsNone(window.user)
                self.assertEqual(window.account_label.text(), "")
                self.assertEqual(window.login_page.email_input.text(), "")
                self.assertEqual(window.login_page.password_input.text(), "")
        finally:
            window.close()
            window.deleteLater()

    def test_invalid_login_and_fresh_session(self):
        window = MainWindow()
        try:
            for email, password in [
                ("", ""),
                ("unknown@blablabla", DEMO_PASSWORD),
                ("employee@blablabla", "wrong"),
            ]:
                window.login_page.email_input.setText(email)
                window.login_page.password_input.setText(password)
                window.login_page.login_button.click()
                self.assertIs(window.root_stack.currentWidget(), window.login_page)
                self.assertIsNone(window.user)
                self.assertIn("Incorrect", window.login_page.message.text())
            self.login(window, " EMPLOYEE@BLABLABLA ")
            old_page = window.pages["personal_tasks"]
            window.logout_button.click()
            self.login(window, "manager@blablabla")
            self.assertIsNot(window.pages["personal_tasks"], old_page)
            self.assertEqual(window.login_page.message.text(), "")
        finally:
            window.close()
            window.deleteLater()


if __name__ == "__main__":
    unittest.main()
