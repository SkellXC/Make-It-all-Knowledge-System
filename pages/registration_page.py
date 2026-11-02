from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from authentication.registration_backend import register_user


class RegistrationPage(QWidget):
    registered = Signal(dict)   # emitted with the new user (same shape as login)
    login_requested = Signal()  # emitted when "Login here" is clicked

    def __init__(self, parent=None):
        super().__init__(parent)
        self.inputs = {}        # field key -> QLineEdit
        self.error_labels = {}  # field key -> small red QLabel
        self.setup_ui()

    def setup_ui(self):
        self.content_layout = QVBoxLayout(self)
        self.content_layout.setContentsMargins(28, 26, 28, 24)

        card = QFrame()
        card.setObjectName("loginCard")
        card.setFixedWidth(400)
        form = QVBoxLayout(card)
        form.setContentsMargins(28, 24, 28, 24)
        form.setSpacing(4)

        title = QLabel("MakeItAll")
        title.setObjectName("loginTitle")
        form.addWidget(title)
        subtitle = QLabel("Create your account")
        subtitle.setObjectName("loginHint")
        form.addWidget(subtitle)
        form.addSpacing(6)

        # First and last name share a row to keep the card compact.
        names = QHBoxLayout()
        names.setSpacing(10)
        names.addLayout(self.make_field("First name", "first_name"))
        names.addLayout(self.make_field("Last name", "second_name"))
        form.addLayout(names)

        form.addLayout(self.make_field("Email", "email"))
        form.addLayout(self.make_field("Username", "username"))
        form.addLayout(self.make_field("Password", "password", secret=True))
        form.addLayout(self.make_field("Confirm password", "confirm_password", secret=True))

        # Pressing Enter moves to the next field; Enter in the last one submits.
        order = ["first_name", "second_name", "email", "username",
                 "password", "confirm_password"]
        for current, following in zip(order, order[1:]):
            self.inputs[current].returnPressed.connect(self.inputs[following].setFocus)
        self.inputs["confirm_password"].returnPressed.connect(self.register)

        # Shown only if something unexpected goes wrong (e.g. database error).
        self.message = QLabel()
        self.message.setObjectName("fieldError")
        self.message.setWordWrap(True)
        self.message.hide()
        form.addWidget(self.message)

        form.addSpacing(8)
        self.register_button = QPushButton("Create account")
        self.register_button.clicked.connect(self.register)
        form.addWidget(self.register_button)
        form.addSpacing(4)

        login_link = QLabel(
            'Already have an account? '
            '<a href="#login" style="color:#476da6; text-decoration:none;">Login here</a>'
        )
        login_link.setObjectName("loginHint")
        login_link.setTextFormat(Qt.TextFormat.RichText)
        login_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_link.linkActivated.connect(lambda _link: self.login_requested.emit())
        self.login_link = login_link
        form.addWidget(login_link)

        self.content_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

    def make_field(self, label_text, key, secret=False):
        """A label, an input and a small red error line, stacked vertically."""
        column = QVBoxLayout()
        column.setSpacing(3)

        label = QLabel(label_text)
        line_edit = QLineEdit()
        if secret:
            line_edit.setEchoMode(QLineEdit.EchoMode.Password)
        label.setBuddy(line_edit)

        error = QLabel()
        error.setObjectName("fieldError")
        error.setWordWrap(True)
        error.hide()  # takes no space until there is an error

        column.addWidget(label)
        column.addWidget(line_edit)
        column.addWidget(error)
        self.inputs[key] = line_edit
        self.error_labels[key] = error
        return column

    def show_errors(self, errors):
        for key, label in self.error_labels.items():
            text = errors.get(key, "")
            label.setText(text)
            label.setVisible(bool(text))

    def register(self):
        self.message.hide()
        try:
            user, errors = register_user(
                self.inputs["first_name"].text(),
                self.inputs["second_name"].text(),
                self.inputs["email"].text(),
                self.inputs["username"].text(),
                self.inputs["password"].text(),
                self.inputs["confirm_password"].text(),
            )
        except Exception:
            self.show_errors({})
            self.message.setText("Something went wrong creating your account. Please try again.")
            self.message.show()
            return

        self.show_errors(errors)
        if user is None:
            return

        self.registered.emit(user)

    def clear_form(self):
        for line_edit in self.inputs.values():
            line_edit.clear()
        self.show_errors({})
        self.message.hide()