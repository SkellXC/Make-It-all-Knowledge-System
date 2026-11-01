import sqlite3

from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QLabel, QLineEdit, QTextEdit, QVBoxLayout,
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
        self.setWindowTitle("Create post")
        self.resize(500, 420)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Category"))
        self.category_input = QComboBox()
        self.category_input.setObjectName("postCategoryInput")
        for key, label in CATEGORIES.items():
            self.category_input.addItem(label, key)
        self.category_input.setCurrentIndex(self.category_input.findData(self.category))
        layout.addWidget(self.category_input)
        layout.addWidget(QLabel("Title"))
        self.title_input = QLineEdit()
        self.title_input.setObjectName("postTitleInput")
        layout.addWidget(self.title_input)
        layout.addWidget(QLabel("Content"))
        self.content_input = QTextEdit()
        self.content_input.setAcceptRichText(False)
        self.content_input.setObjectName("postContentInput")
        layout.addWidget(self.content_input, 1)
        self.error_label = QLabel()
        self.error_label.setObjectName("knowledgeError")
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Post")
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
