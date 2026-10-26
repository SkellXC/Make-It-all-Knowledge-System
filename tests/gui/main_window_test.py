"""Smoke tests: log in through the real window and check what each role sees."""
import pytest
from PySide6.QtCore import Qt

from app.main_window import MainWindow
from app.navigation import visible_pages

ROLES = ["employee", "team leader", "manager", "administrator"]


def log_in(window, email, password):
    window.login_page.email_input.setText(email)
    window.login_page.password_input.setText(password)
    window.login_page.login_button.click()


@pytest.fixture()
def window(qt_application, accounts):
    main_window = MainWindow()
    yield main_window
    main_window.close()
    main_window.deleteLater()


@pytest.mark.parametrize("role", ROLES)
def test_each_role_sees_only_its_permitted_pages(window, accounts, role):
    log_in(window, *accounts[role])

    assert window.root_stack.currentWidget() is window.workspace
    expected = {"dashboard"} | {page.key for page in visible_pages(window.user)}
    assert set(window.pages) == expected
    for key, button in window.nav_buttons.items():
        assert button.isHidden() == (key not in expected)
    # Only people with roles.manage (the administrator, by default) get this page.
    assert ("roles" in window.pages) == (role == "administrator")


@pytest.mark.parametrize("role", ROLES)
def test_every_visible_page_can_be_opened(window, accounts, role):
    log_in(window, *accounts[role])

    for key, button in window.nav_buttons.items():
        if key in window.pages:
            button.click()
            assert window.page_stack.currentWidget() is window.pages[key]


def test_wrong_password_stays_on_login_page(window, accounts):
    email, _password = accounts["employee"]
    log_in(window, email, "wrong password")

    assert window.root_stack.currentWidget() is window.login_page
    assert "Incorrect" in window.login_page.message.text()
    assert window.user is None


def test_switching_accounts_does_not_keep_the_old_users_pages(window, accounts):
    log_in(window, *accounts["administrator"])
    assert "roles" in window.pages

    window.logout_button.click()
    assert window.root_stack.currentWidget() is window.login_page
    assert window.pages == {}
    assert window.user is None

    log_in(window, *accounts["employee"])
    assert "roles" not in window.pages
    assert window.nav_buttons["roles"].isHidden()


def test_roles_page_saves_a_tick_to_the_database(window, db, accounts):
    log_in(window, *accounts["administrator"])
    page = window.pages["roles"]

    assert page.current_role == "employee"  # first role in the list
    assert "projects.create" not in db.get_permissions_for_role("employee")

    page.checkboxes["projects.create"].setChecked(True)

    assert "projects.create" in db.get_permissions_for_role("employee")


def test_roles_page_locks_the_administrator(window, accounts):
    log_in(window, *accounts["administrator"])
    page = window.pages["roles"]

    for row in range(page.role_list.count()):
        if page.role_list.item(row).data(Qt.ItemDataRole.UserRole) == "administrator":
            page.role_list.setCurrentRow(row)

    assert page.current_role == "administrator"
    assert not any(box.isEnabled() for box in page.checkboxes.values())
    assert all(box.isChecked() for box in page.checkboxes.values())