import sys

from PySide6.QtWidgets import QApplication

from app.main_window import MainWindow
from app.styles import STYLESHEET


def main():
    application = QApplication(sys.argv)
    application.setApplicationName("MakeItAll")
    application.setStyle("Fusion")
    application.setStyleSheet(STYLESHEET)
    window = MainWindow()
    window.show()
    return application.exec()


if __name__ == "__main__":
    sys.exit(main())

"""
Employee, manager and team leader passwords are: password
Admin password is: admin1
Depending on the role.
alex.smith@makeitall.com
sarah.jones@makeitall.com
"""