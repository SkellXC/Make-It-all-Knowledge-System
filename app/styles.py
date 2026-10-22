STYLESHEET = """
QWidget { color: #243247; font-size: 14px; }
QMainWindow, QStackedWidget { background: #f3f5f8; }
QFrame#sidebar { background: #192b43; }
QFrame#sidebar QLabel { color: #dbe4f0; background: transparent; }
QFrame#sidebar QLabel#brand {
    color: white;
    font-size: 19px;
    font-weight: 600;
    background: transparent;
}
QFrame#sidebar QPushButton {
    text-align: left;
    color: #dbe4f0;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 11px 13px;
}
QFrame#sidebar QPushButton:hover { background: #243c5b; }
QFrame#sidebar QPushButton:checked { background: #355783; color: white; }
QFrame#sidebar QPushButton:focus { border-color: #91abd0; }
QFrame#sidebar QPushButton:disabled { color: #8495ac; }
QFrame#loginCard {
    background: white;
    border: 1px solid #dce2ea;
    border-radius: 9px;
}
QFrame#loginCard QLabel { background: transparent; }
QLabel#loginTitle { font-size: 25px; font-weight: 600; }
QLabel#loginHint { color: #617086; }
QLabel#loginError { color: #a3313c; }
QLineEdit {
    background: white;
    border: 1px solid #bdc9d9;
    border-radius: 5px;
    padding: 9px;
}
QLineEdit:focus { border-color: #476da6; }
QFrame#loginCard QPushButton {
    background: #476da6;
    color: white;
    border: 1px solid #476da6;
    border-radius: 6px;
    padding: 10px;
}
QFrame#loginCard QPushButton:hover { background: #3b5e92; }
QFrame#loginCard QPushButton:focus { border: 2px solid #91abd0; }
"""
