# Personal to-do data for the 3 November demo

The sample-data script adds role-specific personal tasks to every account already
in the demo laptop's database. It does not create accounts or change permissions.
The default deadline reference date is **3 November 2026**, regardless of when
setup is run.

## Set up the demo laptop

Download the version containing `seed_demo_tasks.py`, activate the app's Python
environment, and run these commands from the repository folder:

```bash
python seed_demo_tasks.py
python main.py
```

The script uses only Python's standard library. If it reports that the personal
task table is missing, open the updated app, log in and visit Personal To-do once,
then close the app and run the script again.

Every account receives 12 examples tailored to its role. On 3 November, an
unchanged sample list contains:

| View | Examples |
| --- | --- |
| Active | 9 tasks: 2 overdue, 2 due today, 1 due tomorrow, 3 upcoming, 1 undated |
| Completed | 3 tasks, including dated and undated examples |
| Priority | High, Normal and Low across both views |

The overdue deadlines are 31 October and 2 November. Tasks due today have a
3 November deadline; tomorrow's task is due 4 November. Later deadlines are
6, 10 and 17 November.

The app calculates labels using the laptop's actual date. During a rehearsal on
2 November, tasks due 3 November correctly show Tomorrow; on the demo date they
show Today.

## Reusing an existing demonstration database

The normal command skips matching task titles for each account. It does not
create duplicates or overwrite changes made during practice.

To rebase the named demo tasks from an earlier setup date to 3 November:

```bash
python seed_demo_tasks.py --date 2026-11-03 --refresh-dates
```

This updates only the matching examples' deadlines. Their priority and completion
states, and unrelated tasks, are kept. A verified database backup is made in
`database/backups/` before any changes.

Only the script and instructions belong in Git. Each laptop generates its own
sample data; the app database and its backups remain local.
