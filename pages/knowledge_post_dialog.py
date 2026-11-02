import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLabel, QLineEdit,
    QTextEdit, QVBoxLayout,
)

from database.knowledge import CATEGORIES, add_post


class CreatePostDialog(QDialog):
    def __init__(self, user, category, parent=None):
        super().__init__(parent)
        self.user = user
        self.category = category
        self.post_id = None
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("knowledgeDialog")
        self.setProperty("formDialog", True)
        self.setWindowTitle("Create post")
        self.setMinimumSize(480, 360)
        self.resize(560, 440)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)
        form = QFormLayout()
        form.setSpacing(10)
        self.category_input = QComboBox()
        self.category_input.setObjectName("postCategoryInput")
        for key, label in CATEGORIES.items():
            self.category_input.addItem(label, key)
        self.category_input.setCurrentIndex(self.category_input.findData(self.category))
        self.title_input = QLineEdit()
        self.title_input.setObjectName("postTitleInput")
        self.title_input.setPlaceholderText("Post title")
        self.content_input = QTextEdit()
        self.content_input.setAcceptRichText(False)
        self.content_input.setObjectName("postContentInput")
        self.content_input.setPlaceholderText("Share a question, solution or useful information.")
        self.content_input.setMinimumHeight(180)
        form.addRow("Category", self.category_input)
        form.addRow("Title", self.title_input)
        form.addRow("Content", self.content_input)
        layout.addLayout(form, 1)
        self.error_label = QLabel()
        self.error_label.setObjectName("knowledgeError")
        self.error_label.setTextFormat(Qt.TextFormat.PlainText)
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        post_button = buttons.button(QDialogButtonBox.StandardButton.Save)
        post_button.setText("Post")
        post_button.setObjectName("formPrimary")
        post_button.setDefault(True)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.save_post)
        layout.addWidget(buttons)
        self.title_input.setFocus()

    def save_post(self):
        category = self.category_input.currentData()
        try:
            post_id = add_post(
                self.user, None, self.title_input.text(), self.content_input.toPlainText(), category
            )
        except (ValueError, PermissionError) as error:
            self.error_label.setText(str(error))
            return
        except sqlite3.Error:
            self.error_label.setText("Could not save the post. Please try again.")
            return
        self.post_id = post_id
        self.category = category
        self.accept()
