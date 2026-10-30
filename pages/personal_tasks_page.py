from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from app.todo_widget import create_todo_widget


class PersonalTasksPage(QWidget):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.content_layout = QVBoxLayout(self)
        self.content_layout.setContentsMargins(40, 40, 40, 24)

        # Create the whole feature through one reusable function.
        self.todo = create_todo_widget(user, parent=self)
        self.todo.setMaximumWidth(760)
        row = QHBoxLayout()
        row.addWidget(self.todo, 1)
        row.addStretch()
        self.content_layout.addLayout(row)
