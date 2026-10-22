from PySide6.QtWidgets import QVBoxLayout, QWidget


class ProjectsPage(QWidget):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.setup_ui()

    def setup_ui(self):
        self.content_layout = QVBoxLayout(self)
        self.content_layout.setContentsMargins(28, 26, 28, 24)
        # Add this module's widgets to self.content_layout.
