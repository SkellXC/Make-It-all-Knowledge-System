"""Registration window flow; run with the other headless Qt tests."""
import pytest

from app.main_window import MainWindow
from authentication.registration_backend import EMAIL_FORMAT_ERROR

GOOD = dict(
    first_name="Jane",
    second_name="Doe",
    email="jane.doe@makeitall.com",
    username="jane_doe",
    password="Password1!",
    confirm_password="Password1!",
)


@pytest.fixture()
def window(qt_application, db):
    main_window = MainWindow()
    yield main_window
    main_window.close()
    main_window.deleteLater()


def fill_form(page, values):
    for key, value in values.items():
        page.inputs[key].setText(value)


def test_login_and_registration_links_swap_pages(window):
    window.login_page.register_requested.emit()
    assert window.root_stack.currentWidget() is window.registration_page

    window.registration_page.login_requested.emit()
    assert window.root_stack.currentWidget() is window.login_page


def test_registering_shows_mfa_then_skip_logs_in(window):
    window.login_page.register_requested.emit()
    fill_form(window.registration_page, GOOD)
    window.registration_page.register_button.click()

    assert window.root_stack.currentWidget() is window.mfa_page

    window.mfa_page.skip_button.click()
    assert window.root_stack.currentWidget() is window.workspace
    assert window.user["email"] == "jane.doe@makeitall.com"


def test_bad_email_shows_error_and_stays_on_registration(window):
    window.login_page.register_requested.emit()
    fill_form(window.registration_page, {**GOOD, "email": "jane@gmail.com"})
    window.registration_page.register_button.click()

    assert window.root_stack.currentWidget() is window.registration_page
    assert window.registration_page.error_labels["email"].text() == EMAIL_FORMAT_ERROR
    assert not window.registration_page.error_labels["email"].isHidden()
