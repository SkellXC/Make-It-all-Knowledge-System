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
QFrame#summaryCard {
    background-color: white;
    border: 1px solid #d9dee7;
    border-radius: 10px;
}

QLabel#summaryCardTitle {
    color: #667085;
    font-size: 13px;
    font-weight: 500;
}

QLabel#summaryCardValue {
    color: #1f2937;
    font-size: 28px;
    font-weight: bold;
}
QFrame#statusNotStarted {
    background-color: #f59e0b;
    border-top-left-radius: 9px;
    border-bottom-left-radius: 9px;
}

QFrame#statusInProgress {
    background-color: #3b82f6;
}
QFrame#sectionTitle{
    color: #111827;
    font-size: 18px;
    font-weight: bold;
}

QFrame#statusCompleted {
    background-color: #22c55e;
    border-top-right-radius: 9px;
    border-bottom-right-radius: 9px;
}
QFrame#dashboardCard{
    border: 1px solid #d9dee7;
    border-radius: 10px;
    background-color:white; 
}
QLabel#statusCompleted{
    text-align:center;
}
QLabel#statusInProgress{
    text-align:center;
}
QFrame#statusEmpty {
    background-color: #d9dee7;
    border-radius: 9px;
}
QFrame#loginCard QPushButton:hover { background: #3b5e92; }
QFrame#loginCard QPushButton:focus { border: 2px solid #91abd0; }
/* Roles & Permissions page */
QListWidget#roleList {
    background: white;
    border: 1px solid #d9dee7;
    border-radius: 10px;
    padding: 6px;
    outline: none;
}
QListWidget#roleList::item { padding: 10px 12px; border-radius: 6px; }
QListWidget#roleList::item:hover { background: #eef2f8; }
QListWidget#roleList::item:selected { background: #355783; color: white; }
QLabel#permissionGroup {
    color: #667085;
    font-size: 13px;
    font-weight: 600;
    padding-top: 10px;
}
QLabel#lockedNote { color: #617086; }
QLabel#rolesMessage { color: #a3313c; }
QCheckBox { spacing: 10px; padding: 5px 0; }
QCheckBox:disabled { color: #8495ac; }
/* Shared Knowledge Base */
QWidget#knowledgePage { font-family: 'Segoe UI'; }
QWidget#knowledgePage QLabel#knowledgeTitle {
    font-size: 25px;
    font-weight: 600;
}
QLabel#knowledgeSection { font-size: 17px; font-weight: 600; }
QLabel#knowledgePostTitle { font-size: 20px; font-weight: 600; color: #202d3d; }
QLabel#knowledgeUsername { font-size: 13px; font-weight: 600; }
QLabel#knowledgeAvatar { color: white; font-size: 12px; font-weight: 600; border-radius: 18px; }
QLabel#knowledgeHint { color: #617086; }
QLabel#knowledgeError { color: #a3313c; }
QFrame#knowledgePostCard, QFrame#knowledgeReply {
    background: white;
    border: 1px solid #d9dee7;
    border-radius: 16px;
}
QFrame#knowledgePostCard QLabel, QFrame#knowledgeReply QLabel { background: transparent; }
QScrollArea#knowledgeScroll { background: transparent; border: none; }
QScrollArea#knowledgeScroll > QWidget > QWidget { background: transparent; }
QWidget#knowledgePage QListWidget, QWidget#knowledgePage QTextEdit,
QDialog#knowledgeDialog QTextEdit, QDialog#knowledgeDialog QComboBox {
    background: white;
    border: 1px solid #d9dee7;
    border-radius: 6px;
    padding: 6px;
    selection-background-color: #e2ebf8;
    selection-color: #243247;
}
QWidget#knowledgePage QListWidget::item { padding: 9px; }
QWidget#knowledgePage QListWidget::item:selected { background: #e2ebf8; }
QWidget#knowledgePage QPushButton, QDialog#knowledgeDialog QPushButton {
    background: white;
    color: #365a8d;
    border: 1px solid #ccd6e4;
    border-radius: 6px;
    padding: 9px 12px;
}
QWidget#knowledgePage QPushButton:hover, QDialog#knowledgeDialog QPushButton:hover {
    background: #edf2f9;
}
QWidget#knowledgePage QPushButton#knowledgePrimary {
    background: #476da6;
    color: white;
    border-color: #476da6;
}
QWidget#knowledgePage QPushButton:disabled { background: #e9edf3; color: #8495ac; }
QWidget#knowledgePage QPushButton#knowledgeLink {
    background: transparent;
    border: none;
    padding: 4px 0;
    text-align: left;
}
QWidget#knowledgePage QPushButton#knowledgeLink:hover { color: #243c5b; }
QFrame#knowledgeCategorySwitch { background: #e8edf3; border-radius: 12px; }
QWidget#knowledgePage QPushButton#knowledgeCategory {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 9px;
    padding: 9px 18px;
    color: #617086;
}
QWidget#knowledgePage QPushButton#knowledgeCategory:checked {
    background: white;
    border-color: #d9e1eb;
    color: #284b7a;
    font-weight: 600;
}
QWidget#knowledgePage QLabel#knowledgeBadge {
    background: #eaf1fc;
    color: #355e95;
    border-radius: 8px;
    padding: 4px 9px;
    font-size: 12px;
}
QWidget#knowledgePage QLabel#knowledgeBadge[category="non-technical"] {
    background: #e9f4ef;
    color: #35735a;
}
QWidget#knowledgePage QPushButton#knowledgeAction {
    background: #eef1f5;
    border: 1px solid transparent;
    border-radius: 17px;
    color: #46556a;
    padding: 7px 14px;
    font-weight: 600;
}
QWidget#knowledgePage QPushButton#knowledgeAction:hover { background: #e2e8f0; }
QWidget#knowledgePage QPushButton#knowledgeAction:checked {
    background: #fff0ee;
    color: #bc5146;
}
QWidget#knowledgePage QTextEdit#knowledgeBody {
    background: transparent;
    border: none;
    padding: 0;
}
QWidget#knowledgePage QScrollBar:vertical {
    background: #f3f5f8;
    width: 8px;
    border: none;
}
QWidget#knowledgePage QScrollBar::handle:vertical {
    background: #c5cfdc;
    border-radius: 4px;
    min-height: 24px;
}
QWidget#knowledgePage QScrollBar::add-line:vertical,
QWidget#knowledgePage QScrollBar::sub-line:vertical { height: 0; }
QWidget#knowledgePage QScrollBar::add-page:vertical,
QWidget#knowledgePage QScrollBar::sub-page:vertical { background: transparent; }

/* Registration page */
QLabel#fieldError { color: #d32f2f; font-size: 11px; }
QFrame#loginCard QPushButton#secondaryButton {
    background: white;
    color: #476da6;
    border: 1px solid #476da6;
}
QFrame#loginCard QPushButton#secondaryButton:hover { background: #eef2f8; }
"""
