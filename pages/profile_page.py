
from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
    QFileDialog,
    QFrame
)

from database.database import (
    get_user_profile_picture,
    save_user_profile_picture
)

from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class ProfilePage(QWidget):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)

        self.user = user
        self.setup_ui()

    def setup_ui(self):
        self.content_layout = QVBoxLayout(self)
        self.content_layout.setContentsMargins(28, 26, 28, 24)
        self.content_layout.setSpacing(15)

        title = QLabel("Profile")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
        """)

        subtitle = QLabel("View your account details")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setObjectName("pageSubtitle")

        self.content_layout.addWidget(title)
        self.content_layout.addWidget(subtitle)

        self.content_layout.addSpacing(15)

        self.profile_picture = QLabel()
        self.profile_picture.setFixedSize(180, 180)
        self.profile_picture.setAlignment(Qt.AlignCenter)

        self.profile_picture.setStyleSheet("""
            QLabel {
                background-color: white;
                border-radius: 10px;
            }
        """)

        self.load_profile_picture()

        change_photo_button = QPushButton("Change Photo")
        change_photo_button.setFixedSize(160, 42)
        change_photo_button.clicked.connect(self.change_photo)

        picture_layout = QVBoxLayout()
        picture_layout.setSpacing(10)
        picture_layout.setAlignment(Qt.AlignCenter)

        picture_layout.addWidget(
            self.profile_picture,
            alignment=Qt.AlignCenter
        )

        picture_layout.addWidget(
            change_photo_button,
            alignment=Qt.AlignCenter
        )

        self.content_layout.addLayout(picture_layout)

        self.content_layout.addSpacing(10)

        info_box = QFrame()
        info_box.setObjectName("dashboardCard")
        info_box.setFixedWidth(500)

        info_layout = QVBoxLayout(info_box)
        info_layout.setContentsMargins(24, 18, 24, 18)
        info_layout.setSpacing(10)

        name_label = QLabel(
            f"{self.user['first_name']} "
            f"{self.user['second_name']}"
        )

        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("""
            font-size: 21px;
            font-weight: bold;
        """)

        email_label = QLabel(
            f"Email: {self.user['email']}"
        )

        email_label.setAlignment(Qt.AlignCenter)
        email_label.setStyleSheet(
            "font-size: 17px;"
        )

        role_label = QLabel(
            f"Role: {self.user['role'].title()}"
        )

        role_label.setAlignment(Qt.AlignCenter)
        role_label.setStyleSheet(
            "font-size: 17px;"
        )

        info_layout.addWidget(name_label)
        info_layout.addWidget(email_label)
        info_layout.addWidget(role_label)

        self.content_layout.addWidget(
            info_box,
            alignment=Qt.AlignCenter
        )

        self.content_layout.addStretch()

    def change_photo(self):
        file_dialog = QFileDialog(self)

        file_dialog.setNameFilter(
            "Images (*.png *.xpm *.jpg *.jpeg *.bmp)"
        )

        if file_dialog.exec():
            selected_file = file_dialog.selectedFiles()[0]

            with open(selected_file, "rb") as f:
                image_data = f.read()

            save_user_profile_picture(
                self.user["id"],
                image_data
            )

            self.load_profile_picture()

    def load_profile_picture(self):
        picture_data = get_user_profile_picture(
            self.user["id"]
        )

        if picture_data:
            pixmap = QPixmap()
            pixmap.loadFromData(picture_data)

            self.profile_picture.setPixmap(
                pixmap.scaled(
                    180,
                    180,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )
