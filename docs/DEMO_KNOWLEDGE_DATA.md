# Knowledge Base demonstration data

The committed `database/database.db` includes 18 fictional example discussions:
9 Technical and 9 Non-technical, each with 3 comments and varying numbers of likes.
Existing posts and all records belonging to other modules are retained.

To restore these examples after replacing the database, run from the project root:

```sh
python -m database.seed_knowledge
```

The script uses the existing Alex Smith, John Paul and Sarah Jones demo accounts.
It does not create accounts, change passwords, reset project/task data or run at startup.
It can be repeated without duplicating its posts, comments or likes. Missing knowledge
tables are created using the existing schema. Missing demo accounts produce a clear error.
Existing sample text and user discussions are not overwritten.

Topics covered include printing, Wi-Fi, display issues, sharing files, office supplies,
onboarding, meetings and handovers. Office-procedure examples are fictional discussion
content, not approved company policy. Reactions use the application's existing likes.

SQLite is a single binary file: Git cannot combine two independently edited databases.
Before committing it, start with the latest version from `main`, back it up and rerun
the relevant sample-data scripts. Do not replace it with an older personal copy.
