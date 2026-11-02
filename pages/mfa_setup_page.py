from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QWidget


class MfaSetupPage(QWidget):
    """Mock 'Set up MFA?' screen shown after registering."""

    skipped = Signal()

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

        title = QLabel("Set up MFA?")
        title.setObjectName("loginTitle")
        form.addWidget(title)

        description = QLabel(
            "Multi-factor authentication adds an extra layer of security to "
            "your account. You can skip this for now."
        )
        description.setObjectName("loginHint")
        description.setWordWrap(True)
        form.addWidget(description)

        # Placeholder: intentionally not connected to anything yet.
        self.yes_button = QPushButton("Yes")
        form.addWidget(self.yes_button)

        self.skip_button = QPushButton("Skip")
        self.skip_button.setObjectName("secondaryButton")
        self.skip_button.clicked.connect(self.skipped.emit)
        form.addWidget(self.skip_button)

        layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)