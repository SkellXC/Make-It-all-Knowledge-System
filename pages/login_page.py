from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget,
)


# Demo only: these credentials provide no real authentication or account storage.
DEMO_ACCOUNTS = {
    "employee@blablabla": "Employee",
    "teamleader@blablabla": "Team Leader",
    "manager@blablabla": "Manager",
}
DEMO_PASSWORD = "blablabla"


class LoginPage(QWidget):
    logged_in = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        card = QFrame()
        card.setObjectName("loginCard")
        card.setFixedWidth(400)
        form = QVBoxLayout(card)
        form.setContentsMargins(28, 28, 28, 28)
        form.setSpacing(14)
        title = QLabel("MakeItAll")
        title.setObjectName("loginTitle")
        form.addWidget(title)

        email_label = QLabel("Email")
        self.email_input = QLineEdit()
        email_label.setBuddy(self.email_input)
        form.addWidget(email_label)
        form.addWidget(self.email_input)
        password_label = QLabel("Password")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_label.setBuddy(self.password_input)
        form.addWidget(password_label)
        form.addWidget(self.password_input)

        self.message = QLabel()
        self.message.setObjectName("loginError")
        self.message.setWordWrap(True)
        form.addWidget(self.message)
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        self.password_input.returnPressed.connect(self.login)
        self.email_input.returnPressed.connect(self.password_input.setFocus)
        form.addWidget(self.login_button)
        hint = QLabel(
            "employee@blablabla\nteamleader@blablabla\nmanager@blablabla"
            "\n\nDemo password: blablabla"
        )
        hint.setObjectName("loginHint")
        hint.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        form.addWidget(hint)
        layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

    def login(self):
        email = self.email_input.text().strip().lower()
        role = DEMO_ACCOUNTS.get(email)
        if role is None or self.password_input.text() != DEMO_PASSWORD:
            self.message.setText("Incorrect demo email or password.")
            self.password_input.clear()
            return
        self.logged_in.emit({"email": email, "role": role})

    def clear_form(self):
        self.email_input.clear()
        self.password_input.clear()
        self.message.clear()
