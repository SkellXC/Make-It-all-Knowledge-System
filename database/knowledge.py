"""Topics, posts and flat replies shared by all signed-in employees."""

import sqlite3
from contextlib import closing

from database.database import get_database_connection


CATEGORIES = {"technical": "Technical", "non-technical": "Non-technical"}


POST_QUERY = """
    SELECT p.id, p.topic_id, p.title, p.content, p.created_at, p.category, p.author_id,
           t.title AS topic_title,
           COALESCE(e.username, 'Deleted user') AS username,
           COALESCE(e.first_name || ' ' || e.second_name, 'Deleted user') AS author,
           (SELECT COUNT(*) FROM knowledge_replies r WHERE r.post_id = p.id) AS reply_count,
           (SELECT COUNT(*) FROM knowledge_post_likes l WHERE l.post_id = p.id) AS like_count
    FROM knowledge_posts p
    JOIN knowledge_topics t ON t.id = p.topic_id
    LEFT JOIN employees e ON e.id = p.author_id
"""


def get_topics():
    with closing(get_database_connection()) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT id, title, description FROM knowledge_topics ORDER BY title COLLATE NOCASE"
        ).fetchall()
        return [dict(row) for row in rows]


def get_posts(topic_id=None, category=None):
    """Newest posts first. The legacy topic filter remains available to other modules."""
    with closing(get_database_connection()) as connection:
        connection.row_factory = sqlite3.Row
        query = POST_QUERY
        parameters = []
        filters = []
        if topic_id is not None:
            filters.append("p.topic_id = ?")
            parameters.append(topic_id)
        if category is not None:
            if category not in CATEGORIES:
                raise ValueError("Choose Technical or Non-technical.")
            filters.append("p.category = ?")
            parameters.append(category)
        if filters:
            query += " WHERE " + " AND ".join(filters)
        rows = connection.execute(
            query + " ORDER BY p.created_at DESC, p.id DESC", parameters
        ).fetchall()
        return [dict(row) for row in rows]


def get_post(post_id):
    with closing(get_database_connection()) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(POST_QUERY + " WHERE p.id = ?", (post_id,)).fetchone()
        return dict(row) if row else None


def get_replies(post_id):
    with closing(get_database_connection()) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute("""
            SELECT r.id, r.content, r.created_at, r.author_id,
                   COALESCE(e.username, 'Deleted user') AS username,
                   COALESCE(e.first_name || ' ' || e.second_name, 'Deleted user') AS author
            FROM knowledge_replies r
            LEFT JOIN employees e ON e.id = r.author_id
            WHERE r.post_id = ?
            ORDER BY r.created_at, r.id
        """, (post_id,)).fetchall()
        return [dict(row) for row in rows]


def require_employee(connection, user):
    # All signed-in roles share this page; authors still need to exist in employees.
    if not user or not user.get("id"):
        raise PermissionError("Please sign in before adding knowledge.")
    employee = connection.execute(
        "SELECT id FROM employees WHERE id = ? AND email = ?",
        (user["id"], user.get("email")),
    ).fetchone()
    if employee is None:
        raise PermissionError("This employee account is no longer available.")
    return employee[0]


def add_topic(user, title, description=""):
    title = title.strip()
    if not title:
        raise ValueError("Enter a topic name.")
    with closing(get_database_connection()) as connection:
        author_id = require_employee(connection, user)
        if connection.execute(
            "SELECT id FROM knowledge_topics WHERE title = ?", (title,)
        ).fetchone():
            raise ValueError("A topic with this name already exists.")
        with connection:
            cursor = connection.execute(
                "INSERT INTO knowledge_topics (title, description, author_id) VALUES (?, ?, ?)",
                (title, description.strip(), author_id),
            )
        return cursor.lastrowid


def add_reply(user, post_id, content):
    content = content.strip()
    if not content:
        raise ValueError("Write a reply before posting.")
    with closing(get_database_connection()) as connection:
        author_id = require_employee(connection, user)
        if connection.execute(
            "SELECT id FROM knowledge_posts WHERE id = ?", (post_id,)
        ).fetchone() is None:
            raise ValueError("This post is no longer available.")
        with connection:
            cursor = connection.execute("""
                INSERT INTO knowledge_replies (post_id, author_id, content)
                VALUES (?, ?, ?)
            """, (post_id, author_id, content))
        return cursor.lastrowid


def add_post(user, topic_id, title, content, category="technical"):
    title, content = title.strip(), content.strip()
    if not title or not content:
        raise ValueError("Enter a post title and content.")
    if category not in CATEGORIES:
        raise ValueError("Choose Technical or Non-technical.")
    with closing(get_database_connection()) as connection:
        author_id = require_employee(connection, user)
        with connection:
            # Keep the existing topic relationship without showing a second topic picker.
            if topic_id is None:
                connection.execute(
                    "INSERT OR IGNORE INTO knowledge_topics (title, author_id) VALUES (?, ?)",
                    (CATEGORIES[category], author_id),
                )
                topic_id = connection.execute(
                    "SELECT id FROM knowledge_topics WHERE title = ?", (CATEGORIES[category],)
                ).fetchone()[0]
            elif connection.execute(
                "SELECT id FROM knowledge_topics WHERE id = ?", (topic_id,)
            ).fetchone() is None:
                raise ValueError("Select an existing topic.")
            cursor = connection.execute("""
                INSERT INTO knowledge_posts (topic_id, author_id, title, content, category)
                VALUES (?, ?, ?, ?, ?)
            """, (topic_id, author_id, title, content, category))
        return cursor.lastrowid


def get_liked_post_ids(user):
    with closing(get_database_connection()) as connection:
        employee_id = require_employee(connection, user)
        return {row[0] for row in connection.execute(
            "SELECT post_id FROM knowledge_post_likes WHERE employee_id = ?", (employee_id,)
        )}


def set_post_like(user, post_id, liked):
    with closing(get_database_connection()) as connection:
        employee_id = require_employee(connection, user)
        if connection.execute(
            "SELECT id FROM knowledge_posts WHERE id = ?", (post_id,)
        ).fetchone() is None:
            raise ValueError("This post is no longer available.")
        with connection:
            if liked:
                connection.execute(
                    "INSERT OR IGNORE INTO knowledge_post_likes (post_id, employee_id) VALUES (?, ?)",
                    (post_id, employee_id),
                )
            else:
                connection.execute(
                    "DELETE FROM knowledge_post_likes WHERE post_id = ? AND employee_id = ?",
                    (post_id, employee_id),
                )
        return connection.execute(
            "SELECT COUNT(*) FROM knowledge_post_likes WHERE post_id = ?", (post_id,)
        ).fetchone()[0]
