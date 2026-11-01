"""Knowledge tables and the small upgrade needed to retain deleted authors' posts."""

import sqlite3


TABLES = {
    "knowledge_topics": """(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL COLLATE NOCASE UNIQUE,
        description TEXT NOT NULL DEFAULT '',
        author_id INTEGER,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (author_id) REFERENCES employees(id) ON DELETE SET NULL
    )""",
    "knowledge_posts": """(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_id INTEGER NOT NULL,
        author_id INTEGER,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        category TEXT NOT NULL DEFAULT 'technical'
            CHECK (category IN ('technical', 'non-technical')),
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (topic_id) REFERENCES knowledge_topics(id),
        FOREIGN KEY (author_id) REFERENCES employees(id) ON DELETE SET NULL
    )""",
    "knowledge_post_likes": """(
        post_id INTEGER NOT NULL,
        employee_id INTEGER NOT NULL,
        PRIMARY KEY (post_id, employee_id),
        FOREIGN KEY (post_id) REFERENCES knowledge_posts(id),
        FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
    )""",
    "knowledge_replies": """(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        author_id INTEGER,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (post_id) REFERENCES knowledge_posts(id),
        FOREIGN KEY (author_id) REFERENCES employees(id) ON DELETE SET NULL
    )""",
}


def create_knowledge_tables(connection):
    # SQLite requires a table rebuild to change a foreign key. Disable checks
    # outside the transaction, then validate before committing and restore them.
    connection.commit()
    connection.execute("PRAGMA foreign_keys = OFF")
    try:
        with connection:
            connection.execute("BEGIN")
            for table, definition in TABLES.items():
                connection.execute(f"CREATE TABLE IF NOT EXISTS {table} {definition}")
                columns = [row[1] for row in connection.execute(f"PRAGMA table_info({table})")]
                employee_keys = [row for row in connection.execute(f"PRAGMA foreign_key_list({table})")
                                 if row[2] == "employees"]
                delete_action = "CASCADE" if table == "knowledge_post_likes" else "SET NULL"
                missing_field = (
                    table == "knowledge_topics" and "description" not in columns
                    or table == "knowledge_posts" and "category" not in columns
                )
                if employee_keys and employee_keys[0][6] == delete_action and not missing_field:
                    continue

                sequence = connection.execute(
                    "SELECT seq FROM sqlite_sequence WHERE name = ?", (table,)
                ).fetchone()
                connection.execute(f"CREATE TABLE {table}_updated {definition}")
                names = ", ".join(columns)
                connection.execute(
                    f"INSERT INTO {table}_updated ({names}) SELECT {names} FROM {table}"
                )
                connection.execute(f"DROP TABLE {table}")
                connection.execute(f"ALTER TABLE {table}_updated RENAME TO {table}")
                if sequence:
                    connection.execute(
                        "UPDATE sqlite_sequence SET seq = MAX(seq, ?) WHERE name = ?",
                        (sequence[0], table),
                    )

            connection.execute("""
                CREATE INDEX IF NOT EXISTS knowledge_replies_post_id
                ON knowledge_replies(post_id)
            """)
            if connection.execute("PRAGMA foreign_key_check").fetchone():
                raise sqlite3.IntegrityError("Database contains invalid foreign key references.")
    finally:
        connection.execute("PRAGMA foreign_keys = ON")
