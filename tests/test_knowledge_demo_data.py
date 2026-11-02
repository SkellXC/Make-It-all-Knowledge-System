from database.knowledge import add_post, get_posts, get_replies
from database.seed_knowledge import DEMO_POSTS, seed_demo_posts


def snapshot(db, knowledge_only=False):
    with db.get_database_connection() as connection:
        tables = [name for name, in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name != 'sqlite_sequence'"
        ) if name.startswith('knowledge_') == knowledge_only]
        return {table: connection.execute(f'SELECT * FROM "{table}" ORDER BY rowid').fetchall()
                for table in tables}


def test_demo_data_is_repeatable_and_preserves_other_modules(db, accounts):
    with db.get_database_connection() as connection:
        row = connection.execute(
            "SELECT id, email FROM employees WHERE email = ?", (accounts['employee'][0],)
        ).fetchone()
    user = {'id': row[0], 'email': row[1]}
    existing = add_post(user, None, 'Existing team post', 'Keep this content.')
    other_tables = snapshot(db)

    post_ids = seed_demo_posts()
    first_run = snapshot(db, knowledge_only=True)
    assert seed_demo_posts() == post_ids
    assert snapshot(db, knowledge_only=True) == first_run
    assert snapshot(db) == other_tables
    assert len(post_ids) == len(DEMO_POSTS) == 18
    assert len(get_posts()) == 19
    assert any(post['id'] == existing and post['content'] == 'Keep this content.'
               for post in get_posts())
    assert len(get_posts(category='technical')) == 10
    assert len(get_posts(category='non-technical')) == 9
    assert all(len(get_replies(post_id)) == 3 for post_id in post_ids)
    assert all(post['like_count'] >= 1 for post in get_posts() if post['id'] in post_ids)
    with db.get_database_connection() as connection:
        assert connection.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        assert connection.execute('PRAGMA foreign_key_check').fetchall() == []
