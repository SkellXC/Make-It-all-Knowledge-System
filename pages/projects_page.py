import datetime as dt
from PySide6.QtWidgets import QVBoxLayout, QWidget, QGridLayout, QLabel, QProgressBar, QFrame, QPushButton
from PySide6.QtGui import QFont, QFontMetrics, Qt, QPainter, QIcon # Truncate large project descriptions

class ElidedLabel(QLabel): # Overriding QLabel's paintEvent
    def paintEvent(self, event):
        painter = QPainter(self)
        metrics = QFontMetrics(self.font())
        # Calculate elided text based on the label's current width
        elided = metrics.elidedText(self.text(), Qt.TextElideMode.ElideRight, self.width())
        painter.drawText(self.rect(), self.alignment(), elided)

class ProjectsPage(QWidget):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.setup_ui()

    def setup_ui(self):
        self.content_layout = QVBoxLayout(self)
        self.content_layout.setContentsMargins(28, 26, 28, 24)

        self.project_overview_grid = QGridLayout()
        self.content_layout.addLayout(self.project_overview_grid)

        # 4 columns and 3 rows with placeholder projects
        for i in range(0, 3):
            for j in range(0, 3):
                project_card = QFrame()
                project_card.setFrameShape(QFrame.Shape.StyledPanel) 
                
                # Stylesheets
                project_card.setStyleSheet("""
                    QFrame {
                        background-color: #ffffff; 
                        border-radius: 8px;
                        border: 1px solid #e0e4e8; /* Light gray border */
                    }
                    QLabel {
                        color: #4a5568; /* Readable dark gray for secondary text */
                        font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; 
                        font-size: 13px; 
                        border: none;
                    }
                    QLabel#CardTitle {
                        color: #2d3748; /* Darker, high-contrast text for title */
                        font-size: 15px;
                        font-weight: bold;
                    }
                    QProgressBar {
                        border: none;
                        border-radius: 4px;
                        background-color: #edf2f7; /* Very light gray track */
                        text-align: center;
                        color: #2d3748; 
                        font-size: 11px;
                    }
                    QProgressBar::chunk {
                        background-color: #4285f4; /* Blue matching the dashboard status bar */
                        border-radius: 4px;
                    }
                    QPushButton {
                        text-align: center;
                        color: #dbe4f0;
                        background: #243c5b;
                        border: 1px solid transparent;
                        border-radius: 6px;
                        padding: 11px 13px;
                    }
                    QPushButton:hover { background: #355783; }
                    QPushButton:checked { background: #355783; color: white; }
                    QPushButton:focus { border-color: #91abd0; }
                    QPushButton:disabled { color: #8495ac; }
                """)
                
                card_layout = QVBoxLayout(project_card)

                # Padding to give space for dashboard cards
                card_layout.setContentsMargins(20, 20, 20, 20)
                card_layout.setSpacing(10)

                project_title_widget = QLabel("Placeholder Project Title")
                project_title_widget.setObjectName("CardTitle") 

                project_date_set_widget = QLabel(dt.date.today().strftime("%d/%m/%Y"))

                project_pending_tasks_widget = QLabel("? Pending Tasks")

                metrics = QFontMetrics(QFont("Arial", 13))
                description = "Brief description of project"
                project_description_widget = ElidedLabel(description)
                project_description_widget.setMinimumWidth(100)

                project_completion_bar_widget = QProgressBar()
                project_completion_bar_widget.setValue(30)
                project_completion_bar_widget.setFixedHeight(12) # Slim completion bar

                view_project_button_widget = QPushButton("View Project")
                view_icon = QIcon.fromTheme(QIcon.ThemeIcon.SystemSearch)
                view_project_button_widget.setIcon(view_icon)

                card_layout.addWidget(project_title_widget)
                card_layout.addWidget(project_date_set_widget)
                card_layout.addWidget(project_pending_tasks_widget)
                card_layout.addWidget(project_description_widget)
                card_layout.addWidget(project_completion_bar_widget)
                card_layout.addWidget(view_project_button_widget)
                card_layout.addStretch()

                self.project_overview_grid.addWidget(project_card, i, j)