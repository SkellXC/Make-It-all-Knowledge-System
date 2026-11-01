import sqlite3
from datetime import datetime, timezone

from PySide6.QtCore import Qt
from PySide6.QtGui import QTextOption
from PySide6.QtWidgets import (
    QButtonGroup, QDialog, QFrame, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QStackedWidget,
    QTextEdit, QVBoxLayout, QWidget,
)

from database.knowledge import (
    CATEGORIES, add_reply, get_liked_post_ids, get_post,
    get_posts, get_replies, set_post_like,
)
from pages.knowledge_post_dialog import CreatePostDialog


def time_ago(created_at):
    created = datetime.fromisoformat(created_at).replace(tzinfo=timezone.utc)
    seconds = max(0, int((datetime.now(timezone.utc) - created).total_seconds()))
    if seconds < 60:
        return "just now"
    if seconds < 3600:
        return f"{seconds // 60} min ago"
    if seconds < 86400:
        return f"{seconds // 3600} hr ago"
    return f"{seconds // 86400} days ago"


class PostBody(QTextEdit):
    """Selectable plain text that wraps long words; the outer page handles scrolling."""

    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.setObjectName("knowledgeBody")
        self.setReadOnly(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.document().setDocumentMargin(0)
        self.document().documentLayout().documentSizeChanged.connect(self.fit_height)
        self.setPlainText(text)

    def fit_height(self, size):
        self.setFixedHeight(max(1, int(size.height()) + 2))


class KnowledgePage(QWidget):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.category = "technical"
        self.current_post_id = None
        self.liked_ids = set()
        self.post_buttons = {}
        self.like_buttons = {}
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("knowledgePage")
        self.content_layout = QVBoxLayout(self)
        self.content_layout.setContentsMargins(28, 26, 28, 24)
        self.content_layout.setSpacing(18)
        heading = QHBoxLayout()
        title = QLabel("Knowledge Base")
        title.setObjectName("knowledgeTitle")
        heading.addWidget(title, 1)
        self.post_button = QPushButton("＋ Create post")
        self.post_button.setObjectName("knowledgePrimary")
        self.post_button.clicked.connect(self.create_post)
        heading.addWidget(self.post_button)
        self.content_layout.addLayout(heading)
        self.setup_category_switch()

        self.message = QLabel()
        self.message.setObjectName("knowledgeError")
        self.message.setWordWrap(True)
        self.message.hide()
        self.content_layout.addWidget(self.message)
        self.view_stack = QStackedWidget()
        self.setup_feed()
        self.setup_post_view()
        self.content_layout.addWidget(self.view_stack, 1)

    def setup_category_switch(self):
        switch = QFrame()
        switch.setObjectName("knowledgeCategorySwitch")
        switch_layout = QHBoxLayout(switch)
        switch_layout.setContentsMargins(4, 4, 4, 4)
        switch_layout.setSpacing(4)
        group = QButtonGroup(self)
        group.setExclusive(True)
        self.category_buttons = {}
        for key, label in CATEGORIES.items():
            button = QPushButton(label)
            button.setObjectName("knowledgeCategory")
            button.setCheckable(True)
            button.setChecked(key == self.category)
            button.clicked.connect(lambda checked=False, category=key: self.set_category(category))
            group.addButton(button)
            switch_layout.addWidget(button)
            self.category_buttons[key] = button
        switch_row = QHBoxLayout()
        switch_row.addWidget(switch)
        switch_row.addStretch()
        hint = QLabel("Newest first")
        hint.setObjectName("knowledgeHint")
        switch_row.addWidget(hint)
        self.content_layout.addLayout(switch_row)

    def setup_feed(self):
        self.feed_page = QWidget()
        layout = QVBoxLayout(self.feed_page)
        layout.setContentsMargins(0, 0, 0, 0)
        self.feed_scroll = QScrollArea()
        self.feed_scroll.setObjectName("knowledgeScroll")
        self.feed_scroll.setWidgetResizable(True)
        self.feed_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.feed_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        container = QWidget()
        self.feed_layout = QVBoxLayout(container)
        self.feed_layout.setContentsMargins(0, 0, 6, 0)
        self.feed_layout.setSpacing(14)
        self.feed_scroll.setWidget(container)
        layout.addWidget(self.feed_scroll)
        self.view_stack.addWidget(self.feed_page)

    def setup_post_view(self):
        self.post_page = QWidget()
        layout = QVBoxLayout(self.post_page)
        layout.setContentsMargins(0, 0, 0, 0)
        self.back_button = QPushButton("← Back to posts")
        self.back_button.setObjectName("knowledgeLink")
        self.back_button.clicked.connect(self.show_feed)
        layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self.post_scroll = QScrollArea()
        self.post_scroll.setObjectName("knowledgeScroll")
        self.post_scroll.setWidgetResizable(True)
        self.post_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.post_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        container = QWidget()
        content_layout = QVBoxLayout(container)
        content_layout.setContentsMargins(0, 0, 6, 0)
        content_layout.setSpacing(14)
        card = QFrame()
        card.setObjectName("knowledgePostCard")
        post_layout = QVBoxLayout(card)
        post_layout.setContentsMargins(22, 20, 22, 20)
        post_layout.setSpacing(14)
        self.post_header = QVBoxLayout()
        self.post_header.setContentsMargins(0, 0, 0, 0)
        post_layout.addLayout(self.post_header)
        self.post_title = QLabel()
        self.post_title.setObjectName("knowledgePostTitle")
        self.post_title.setTextFormat(Qt.TextFormat.PlainText)
        self.post_title.setWordWrap(True)
        post_layout.addWidget(self.post_title)
        self.post_content = PostBody()
        post_layout.addWidget(self.post_content)
        self.post_actions = QVBoxLayout()
        self.post_actions.setContentsMargins(0, 0, 0, 0)
        post_layout.addLayout(self.post_actions)
        content_layout.addWidget(card)
        self.replies_heading = QLabel("Comments")
        self.replies_heading.setObjectName("knowledgeSection")
        content_layout.addWidget(self.replies_heading)
        self.reply_input = QTextEdit()
        self.reply_input.setObjectName("replyInput")
        self.reply_input.setAcceptRichText(False)
        self.reply_input.setPlaceholderText("Add a comment…")
        self.reply_input.setFixedHeight(90)
        content_layout.addWidget(self.reply_input)
        self.reply_error = QLabel()
        self.reply_error.setObjectName("knowledgeError")
        self.reply_error.setWordWrap(True)
        self.reply_error.hide()
        content_layout.addWidget(self.reply_error)
        self.reply_button = QPushButton("Comment")
        self.reply_button.setObjectName("knowledgePrimary")
        self.reply_button.clicked.connect(self.submit_reply)
        content_layout.addWidget(self.reply_button, alignment=Qt.AlignmentFlag.AlignLeft)
        replies = QWidget()
        self.replies_layout = QVBoxLayout(replies)
        self.replies_layout.setContentsMargins(0, 0, 0, 0)
        self.replies_layout.setSpacing(10)
        content_layout.addWidget(replies)
        content_layout.addStretch()
        self.post_scroll.setWidget(container)
        layout.addWidget(self.post_scroll, 1)
        self.view_stack.addWidget(self.post_page)

    def showEvent(self, event):
        super().showEvent(event)
        self.show_feed()

    def set_category(self, category):
        self.category = category
        self.category_buttons[category].setChecked(True)
        self.show_feed()

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def show_error(self, text):
        self.message.setText(text)
        self.message.show()

    def show_feed(self, checked=False):
        try:
            posts = get_posts(category=self.category)
            self.liked_ids = get_liked_post_ids(self.user)
        except (sqlite3.Error, PermissionError):
            self.show_error("Could not load posts. Please try opening this page again.")
            return
        self.message.hide()
        self.current_post_id = None
        self.reply_input.clear()
        self.reply_error.hide()
        self.clear_layout(self.feed_layout)
        self.post_buttons.clear()
        self.like_buttons.clear()
        for post in posts:
            self.feed_layout.addWidget(self.create_post_card(post))
        if not posts:
            empty = QLabel("No posts here yet. Share the first post in this category.")
            empty.setObjectName("knowledgeHint")
            empty.setWordWrap(True)
            self.feed_layout.addWidget(empty)
        self.feed_layout.addStretch()
        self.view_stack.setCurrentWidget(self.feed_page)

    def author_header(self, record, show_category=True):
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        initials = "".join(word[0] for word in record["author"].split()[:2]).upper()
        avatar = QLabel(initials)
        avatar.setObjectName("knowledgeAvatar")
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        palette = ["#526f9e", "#6e659f", "#39877f", "#a27749"]
        avatar.setStyleSheet(f"background-color: {palette[(record['author_id'] or 0) % len(palette)]};")
        layout.addWidget(avatar)
        name = QLabel(record["username"])
        name.setObjectName("knowledgeUsername")
        name.setTextFormat(Qt.TextFormat.PlainText)
        name.setWordWrap(True)
        layout.addWidget(name)
        created = QLabel("· " + time_ago(record["created_at"]))
        created.setObjectName("knowledgeHint")
        created.setToolTip(record["created_at"] + " UTC")
        layout.addWidget(created)
        layout.addStretch()
        if show_category:
            badge = QLabel(CATEGORIES[record["category"]])
            badge.setObjectName("knowledgeBadge")
            badge.setProperty("category", record["category"])
            layout.addWidget(badge)
        return header

    def action_bar(self, post):
        bar = QWidget()
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        liked = post["id"] in self.liked_ids
        like = QPushButton(f"{'♥' if liked else '♡'}  {post['like_count']}")
        like.setObjectName("knowledgeAction")
        like.setCheckable(True)
        like.setChecked(liked)
        like.setToolTip("Like this post; click again to remove your like.")
        like.clicked.connect(
            lambda checked, post_id=post["id"], button=like: self.save_like(post_id, checked, button)
        )
        layout.addWidget(like)
        comments = QPushButton(f"Comments  {post['reply_count']}")
        comments.setObjectName("knowledgeAction")
        comments.clicked.connect(lambda checked=False, post_id=post["id"]: self.open_post(post_id))
        layout.addWidget(comments)
        layout.addStretch()
        self.like_buttons[post["id"]] = like
        self.post_buttons[post["id"]] = comments
        return bar

    def create_post_card(self, post):
        card = QFrame()
        card.setObjectName("knowledgePostCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(14)
        layout.addWidget(self.author_header(post))
        title = QLabel(post["title"])
        title.setObjectName("knowledgePostTitle")
        title.setTextFormat(Qt.TextFormat.PlainText)
        title.setWordWrap(True)
        layout.addWidget(title)
        preview = post["content"].strip()
        if len(preview) > 600:
            preview = preview[:600].rstrip() + "…"
        content = PostBody(preview)
        layout.addWidget(content)
        layout.addWidget(self.action_bar(post))
        return card

    def save_like(self, post_id, liked, button):
        try:
            count = set_post_like(self.user, post_id, liked)
        except (sqlite3.Error, PermissionError, ValueError):
            button.setChecked(not liked)
            self.show_error("Could not save your like. Please try again.")
            return
        if liked:
            self.liked_ids.add(post_id)
        else:
            self.liked_ids.discard(post_id)
        button.setText(f"{'♥' if liked else '♡'}  {count}")
        self.message.hide()

    def open_post(self, post_id):
        try:
            post = get_post(post_id)
            if post is None:
                self.show_error("This post is no longer available.")
                return
            replies = get_replies(post_id)
            self.liked_ids = get_liked_post_ids(self.user)
        except (sqlite3.Error, PermissionError):
            self.show_error("Could not load this discussion. Please try again.")
            return
        self.message.hide()
        if post_id != self.current_post_id:
            self.reply_input.clear()
            self.post_scroll.verticalScrollBar().setValue(0)
        self.current_post_id = post_id
        self.clear_layout(self.post_header)
        self.post_header.addWidget(self.author_header(post))
        self.post_title.setText(post["title"])
        self.post_content.setPlainText(post["content"])
        self.clear_layout(self.post_actions)
        self.post_actions.addWidget(self.action_bar(post))
        self.replies_heading.setText(f"Comments ({len(replies)})")
        self.reply_error.hide()
        self.clear_layout(self.replies_layout)
        for reply in replies:
            card = QFrame()
            card.setObjectName("knowledgeReply")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(18, 16, 18, 16)
            layout.addWidget(self.author_header(reply, show_category=False))
            text = PostBody(reply["content"])
            layout.addWidget(text)
            self.replies_layout.addWidget(card)
        if not replies:
            empty = QLabel("No comments yet. Start the conversation.")
            empty.setObjectName("knowledgeHint")
            empty.setWordWrap(True)
            self.replies_layout.addWidget(empty)
        self.view_stack.setCurrentWidget(self.post_page)

    def submit_reply(self):
        if self.current_post_id is None:
            return
        try:
            add_reply(self.user, self.current_post_id, self.reply_input.toPlainText())
        except (ValueError, PermissionError) as error:
            self.reply_error.setText(str(error))
            self.reply_error.show()
            return
        except sqlite3.Error:
            self.reply_error.setText("Could not save your comment. Your text has been kept.")
            self.reply_error.show()
            return
        self.reply_input.clear()
        self.open_post(self.current_post_id)

    def create_post(self):
        dialog = CreatePostDialog(self.user, self.category, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.set_category(dialog.category)
            self.open_post(dialog.post_id)
        dialog.deleteLater()
