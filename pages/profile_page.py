
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
from app.styles import STYLESHEET
from PySide6.QtGui import QPixmap, QPainter, QPainterPath
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
        # border radius to make pfp a circle is 50% of width and height
        width_height = 180 # square so width and height are the same
        self.profile_picture.setFixedSize(width_height, width_height)
        self.profile_picture.setAlignment(Qt.AlignCenter)

        self.profile_picture.setStyleSheet(f"""
            QLabel {{
                background-color: white;
                border-radius: {width_height // 2}; /* make the border a circle shape */
                border-width: 2px;
                border-style: solid;
                border-color: #555555;
            }}
        """)

        self.load_profile_picture()

        change_photo_button = QPushButton("Change Photo")
        change_photo_button.setObjectName("change_pfp")
        change_photo_button.setStyleSheet(STYLESHEET)
        change_photo_button.setFixedSize(160, 42)
        change_photo_button.clicked.connect(self.change_photo)

        picture_layout = QVBoxLayout()
        picture_layout.setSpacing(10)
        picture_layout.setAlignment(Qt.AlignCenter)

        picture_layout.addWidget(
            self.profile_picture,
            alignment=Qt.AlignCenter
        )
        self.profile_picture.lower()

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

            if picture_data:
                pixmap = QPixmap()
                if pixmap.loadFromData(picture_data):
                    inner_size = 180 - 2 * 2 # label size - border on each side
                    self.profile_picture.setPixmap(self.circular_pixmap(pixmap, inner_size))

    @staticmethod
    def circular_pixmap(pixmap, size):
        """Crop a pixmap to a centred square, then clip it to a circle."""
        # fill the square (cropping the overflow) instead of leaving gaps
        scaled = pixmap.scaled(
            size, size,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        x = (scaled.width() - size) // 2
        y = (scaled.height() - size) // 2
        square = scaled.copy(x, y, size, size)

        result = QPixmap(size, size)
        result.fill(Qt.GlobalColor.transparent)

        painter = QPainter(result)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, square)
        painter.end()
        return result
