"""Load tidy, realistic demo data for the Team 03 presentation.

Run from the project folder:   python seed_demo_data.py
Optional:                      python seed_demo_data.py --date 2026-11-03

What it does (a backup of database/database.db is made first):
  * Moves every employee email to @make-it-all.co.uk (the admin's email too).
  * Sets every non-admin password to "password". The admin password is not changed.
  * Removes the duplicate Tony Stark account and adds a few more employees.
  * REPLACES all projects, project tasks and project members with 8 distinct,
    relevant projects. Alex is on only two of them.
  * REPLACES personal to-dos for Alex, John and Sarah (priorities, overdue,
    today, upcoming and completed). Other test to-dos are removed.
  * REPLACES the Knowledge Base with topics and technical / non-technical
    posts, replies and likes.

Dates are relative to today (or --date), so "overdue", "today" and "tomorrow"
look right on the day you present. Run it again on the morning of the demo.
Do not run seed_demo_tasks.py afterwards: it would add generic tasks.
"""

import argparse
import shutil
import sqlite3
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import os
os.chdir(ROOT)  # the app uses the relative path database/database.db

from authentication.authentication import password_hash  # noqa: E402
import database.database as db  # noqa: E402

OLD_DOMAIN = "@makeitall.com"
NEW_DOMAIN = "@make-it-all.co.uk"
DEMO_PASSWORD = "password"
ADMIN_ROLE = "administrator"

# first, second, username, role  (email is built from first.second)
NEW_PEOPLE = [
    ("Priya", "Patel", "priya_patel", "employee"),
    ("Marcus", "Webb", "marcus_webb", "employee"),
    ("Hannah", "Clarke", "hannah_clarke", "employee"),
    ("Omar", "Farouk", "omar_farouk", "employee"),
    ("Lucy", "Chen", "lucy_chen", "team leader"),
]


def build_plan(today):
    """Everything below is keyed by first name so it is easy to edit."""

    def d(offset):
        return None if offset is None else (today + timedelta(days=offset)).isoformat()

    # name, description, manager, status, start, deadline, members, tasks
    # task = (title, assignee, due offset, priority, done)
    projects = [
        ("Staff Intranet Redesign",
         "Replace the outdated intranet with a searchable, mobile-friendly site for "
         "company news, policies and forms.",
         "Sarah", "in progress", -35, 21, ["John", "Alex", "Priya", "Hannah"], [
             ("Gather requirements from each department", "Priya", -28, "high", True),
             ("Audit existing intranet pages", "Alex", -24, "normal", True),
             ("Agree navigation and page structure", "John", -18, "high", True),
             ("Design home page wireframes", "Priya", -10, "normal", True),
             ("Migrate HR policy documents", "Alex", -4, "normal", True),
             ("Write help and FAQ content", "Alex", -1, "normal", False),
             ("Build staff directory search", "Hannah", 3, "high", False),
             ("User testing with the admin team", "John", 12, "normal", False),
             ("Launch announcement to all staff", "Alex", 19, "low", False),
         ]),
        ("Office Laptop Refresh",
         "Replace 60 ageing staff laptops with the new standard build and securely "
         "retire the old devices.",
         "Sarah", "in progress", -42, 14, ["John", "Peter", "Marcus", "Steve"], [
             ("Approve budget and supplier quote", "John", -38, "high", True),
             ("Order 60 replacement laptops", "Peter", -30, "high", True),
             ("Create standard laptop image", "Marcus", -21, "high", True),
             ("Test image with a pilot group", "Steve", -12, "normal", True),
             ("Deploy laptops to finance and admin", "Peter", -1, "high", False),
             ("Deploy laptops to the support team", "Steve", 4, "normal", False),
             ("Securely wipe and recycle old laptops", "Marcus", 9, "normal", False),
             ("Update the asset register", "John", 12, "low", False),
         ]),
        ("Cyber Security Awareness Training",
         "Run phishing and password training for every employee, in line with NCSC "
         "guidance.",
         "Sarah", "in progress", -21, 35, ["Lucy", "Alex", "Hannah", "Omar"], [
             ("Choose the training provider", "Lucy", -17, "high", True),
             ("Draft the phishing awareness module", "Omar", -9, "normal", True),
             ("Write password and MFA guidance", "Hannah", -3, "normal", True),
             ("Record a short introduction video", "Alex", 0, "normal", False),
             ("Pilot the training with the support team", "Omar", 7, "high", False),
             ("Set up completion tracking", "Hannah", 14, "normal", False),
             ("Send training invitations to staff", "Lucy", 21, "low", False),
             ("Review results and report to managers", "Lucy", 33, "normal", False),
         ]),
        ("Customer Portal Migration",
         "Move the customer support portal to the new hosting platform without losing "
         "ticket history.",
         "Sarah", "in progress", -60, 10, ["John", "Lucy", "Priya", "Marcus", "Steve"], [
             ("Inventory portal features and integrations", "Priya", -55, "normal", True),
             ("Set up the new hosting environment", "Marcus", -45, "high", True),
             ("Migrate the ticket database to staging", "Steve", -30, "high", True),
             ("Test single sign-on with staff accounts", "Marcus", -20, "normal", True),
             ("Verify migrated ticket history", "Priya", -10, "normal", True),
             ("Fix attachment links after migration", "Steve", 1, "high", False),
             ("Run final load and security checks", "Lucy", 4, "high", False),
             ("Agree the cut-over date with support leads", "John", 6, "normal", False),
             ("Switch DNS to the new platform", "Marcus", 9, "high", False),
         ]),
        ("Print Services Consolidation",
         "Replace six departmental printers with two managed multifunction devices and "
         "set up print-usage reporting.",
         "Sarah", "not started", 7, 75, ["Lucy", "Peter", "Omar"], [
             ("Survey current printer usage", "Omar", 14, "normal", False),
             ("Shortlist managed print suppliers", "Lucy", 21, "high", False),
             ("Plan device locations and cabling", "Peter", 30, "normal", False),
             ("Write a 'how to print' guide for staff", "Omar", 60, "low", False),
         ]),
        ("New Starter Onboarding Pack",
         "Create one pack covering accounts, equipment and first-week tasks for every "
         "new employee.",
         "Sarah", "not started", 14, 60, ["John", "Hannah", "Priya"], [
             ("Collect current starter checklists", "Hannah", 20, "normal", False),
             ("Draft the IT account request form", "Priya", 28, "high", False),
             ("Create the equipment handover guide", "John", 40, "normal", False),
             ("Review the pack with HR", "John", 55, "low", False),
         ]),
        ("Office Network Upgrade",
         "Install new Wi-Fi access points and update the wired network across all floors.",
         "Tony", "in progress", -28, 30, ["Peter", "Steve", "Omar", "Sarah"], [
             ("Survey Wi-Fi coverage on every floor", "Omar", -24, "high", True),
             ("Approve the network upgrade budget", "Sarah", -20, "high", True),
             ("Select the new access points", "Peter", -14, "normal", True),
             ("Install access points on floors 1 and 2", "Steve", -5, "normal", True),
             ("Sign off the weekend downtime schedule", "Sarah", 3, "normal", False),
             ("Install access points on floors 3 and 4", "Steve", 7, "high", False),
             ("Update the network diagram", "Peter", 18, "low", False),
         ]),
        ("Backup and Recovery Review",
         "Check that business-critical systems can be restored quickly and document "
         "the recovery steps.",
         "Tony", "not started", 10, 50, ["Steve", "Marcus", "Lucy"], [
             ("List business-critical systems", "Marcus", 18, "high", False),
             ("Test restoring last month's backup", "Steve", 30, "high", False),
             ("Write the recovery runbook", "Lucy", 42, "normal", False),
         ]),
    ]

    # (title, priority, due offset, done)
    personal = {
        "Alex": [
            ("Submit October expense claim", "high", -2, False),
            ("Reply to Finance about the laptop invoice", "high", 0, False),
            ("Send updated FAQ draft to John for review", "high", 2, False),
            ("Prepare notes for Thursday's intranet review", "normal", 1, False),
            ("Book a room for the user testing session", "normal", 3, False),
            ("Complete the cyber security refresher quiz", "normal", 8, False),
            ("Tidy shared drive folders", "low", 5, False),
            ("Read the new starter guide", "low", None, False),
            ("Submit last week's timesheet", "high", -6, True),
            ("Order printer paper for the second floor", "normal", -5, True),
            ("Back up project documents to the shared drive", "normal", -3, True),
            ("Update the team contact list", "low", -8, True),
        ],
        "John": [
            ("Prepare the team briefing agenda", "high", 0, False),
            ("Review the team's weekly workload notes", "high", 1, False),
            ("Approve Priya's leave request", "normal", -1, False),
            ("One-to-one with Alex", "normal", 2, False),
            ("Check changes to the laptop asset register", "normal", 4, False),
            ("Update the escalation contacts list", "low", 6, False),
            ("Draft retrospective notes for the laptop refresh", "normal", 9, False),
            ("Think about a new-starter buddy scheme", "low", None, False),
            ("Sign off pilot laptop feedback", "high", -7, True),
            ("Send last week's handover summary", "normal", -4, True),
            ("Book a training slot for the team", "low", -9, True),
        ],
        "Sarah": [
            ("Agree December leave cover", "normal", -2, False),
            ("Approve Q4 resource requests", "high", 0, False),
            ("Review the monthly delivery forecast", "high", 1, False),
            ("Prepare slides for the leadership briefing", "high", 3, False),
            ("Check the network upgrade timeline with Tony", "low", 4, False),
            ("Meet suppliers about managed print", "normal", 5, False),
            ("Confirm the intranet launch date with comms", "normal", 7, False),
            ("Review the department training budget", "normal", 12, False),
            ("Think about next year's project priorities", "low", None, False),
            ("Approve the laptop supplier quote", "high", -10, True),
            ("Send the September project summary", "normal", -6, True),
            ("Sign off the cyber training provider", "normal", -5, True),
            ("Book the team away day venue", "low", -12, True),
        ],
    }
    return d, projects, personal


# ---------------------------------------------------------------- Knowledge Base
# topic: (title, description, author)
TOPICS = [
    ("Software Development", "Code, repositories, build tools and coding standards.", "John"),
    ("Software Issues", "Common application faults and how to fix them.", "Marcus"),
    ("Hardware and Devices", "Laptops, monitors, docking stations and peripherals.", "Peter"),
    ("Printing", "Printers, paper, toner and print requests.", "Sarah"),
    ("Office Admin", "Everyday admin: ordering, booking and expenses.", "Hannah"),
    ("Security and Access", "Passwords, MFA and safe working practices.", "Lucy"),
]

# (topic, author, category, days ago, title, content)
POSTS = [
    ("Software Issues", "Marcus", "technical", 12,
     "Outlook stops syncing after a password change",
     "Symptom: Outlook shows 'Disconnected' or keeps asking for a password after you "
     "change your network password.\n\nFix:\n1. Close Outlook completely.\n"
     "2. Open Windows Credential Manager and remove any entries that mention "
     "outlook or office.\n3. Restart the laptop and open Outlook again.\n"
     "4. Sign in with the new password when asked.\n\nIf it still fails, create a new "
     "Outlook profile from Control Panel > Mail."),
    ("Software Issues", "Steve", "technical", 9,
     "VPN error 809 when working from home",
     "Cause: some home routers block the ports the VPN needs (UDP 500 and 4500).\n\n"
     "Fix:\n1. Check your router has 'VPN passthrough' or 'IPsec passthrough' switched on.\n"
     "2. Restart the router and the VPN client.\n"
     "3. Try a phone hotspot to confirm it is the home network.\n\n"
     "If the hotspot works but your router does not, raise a ticket and include your "
     "router model."),
    ("Software Development", "John", "technical", 14,
     "Getting access to the shared Git repository",
     "1. Ask your team leader to add you to the project group.\n"
     "2. Create an SSH key: ssh-keygen -t ed25519\n"
     "3. Add the public key to your profile on the code server.\n"
     "4. Clone the repository with the SSH address, not the web address.\n\n"
     "Never commit passwords or keys. Use the shared secrets store instead."),
    ("Software Development", "Priya", "technical", 7,
     "Coding standards for the intranet project",
     "Agreed standards:\n- Use clear names; no one-letter variables.\n"
     "- Keep functions short and give each one a single job.\n"
     "- Every change is reviewed by one other person before it is merged.\n"
     "- Add a short comment when the reason for something is not obvious."),
    ("Hardware and Devices", "Peter", "technical", 10,
     "Setting up a new laptop from the standard image",
     "1. Plug in the charger and connect to the office network.\n"
     "2. Sign in with your staff email and temporary password.\n"
     "3. Wait for the software installation to finish (about 20 minutes).\n"
     "4. Restart when asked, then set up your PIN.\n"
     "5. Check that Outlook, Teams and the VPN client open.\n\n"
     "Do not skip the restart: security updates are applied then."),
    ("Printing", "Omar", "technical", 5,
     "Printer shows 'offline' on Windows 11",
     "Often the print queue is stuck.\n1. Open Services and restart 'Print Spooler'.\n"
     "2. Delete any old jobs in the queue.\n3. Remove and re-add the printer.\n\n"
     "If several people see the same printer offline, tell Support: the device may "
     "need a restart."),
    ("Printing", "Sarah", "non-technical", 11,
     "How to order printing paper",
     "Order through Resources using your team's cost code.\n"
     "- A4 and A3 paper come in boxes of five reams.\n"
     "- Orders placed by Wednesday arrive on Friday.\n"
     "- Check the stock cupboard first so we do not over-order.\n\n"
     "Ask your team leader if you are unsure of the cost code."),
    ("Printing", "Omar", "non-technical", 4,
     "Printing confidential documents",
     "Use 'Secure print' for anything with personal or financial information. The job "
     "is held until you tap your staff card at the printer, so it never sits in the "
     "output tray. Do not leave printouts unattended."),
    ("Office Admin", "Hannah", "non-technical", 13,
     "How to book a meeting room",
     "Open your Outlook calendar, choose 'New meeting' and add the room as a location "
     "from the Rooms list.\n- Bookings are limited to two hours.\n"
     "- Cancel the room if you no longer need it.\n"
     "- For events with visitors, tell Reception the day before."),
    ("Office Admin", "Alex", "non-technical", 8,
     "How to submit expenses",
     "Claim within 30 days of spending the money.\n"
     "1. Photograph each receipt.\n2. Fill in the expense form and add the project "
     "cost code.\n3. Send it to your manager for approval.\n\n"
     "Claims without receipts are returned."),
    ("Office Admin", "John", "non-technical", 6,
     "Requesting equipment for a new starter",
     "Send the request at least ten working days before the start date. Include the "
     "person's name, job title, team and the equipment needed. Support will prepare "
     "the laptop and accounts, and Reception will arrange a pass and desk."),
    ("Security and Access", "Lucy", "non-technical", 3,
     "Spotting a phishing email: quick checklist",
     "Stop and check before you click:\n- Does the sender address match the company?\n"
     "- Is the message urgent or threatening?\n- Does it ask for a password or payment "
     "details?\n- Does a link go somewhere unexpected when you hover over it?\n\n"
     "If in doubt, do not click. Forward it to Support and delete it."),
]

# (post title, author, days ago, content)
REPLIES = [
    ("Outlook stops syncing after a password change", "Alex", 11,
     "This worked for me. Removing the old credentials was the key step."),
    ("Outlook stops syncing after a password change", "Steve", 11,
     "If it still fails, a new profile fixed it for two people on my team."),
    ("VPN error 809 when working from home", "Priya", 8,
     "Passthrough was off on my router. Switching it on fixed it straight away."),
    ("Getting access to the shared Git repository", "Alex", 13,
     "Useful, thanks. Step 4 is easy to miss."),
    ("How to order printing paper", "Alex", 10,
     "Is there a limit per order? I need extra for the training pack."),
    ("How to order printing paper", "Sarah", 10,
     "No limit, but anything over ten boxes needs approval from your team leader."),
    ("How to book a meeting room", "John", 12,
     "Worth adding: the large boardroom needs approval from Reception."),
    ("Spotting a phishing email: quick checklist", "Sarah", 2,
     "Great checklist. We will link this in the cyber awareness training."),
    ("Printer shows 'offline' on Windows 11", "Peter", 4,
     "Restarting the spooler fixed it on the second floor printer."),
]

# (post title, [people who liked it])
LIKES = [
    ("Outlook stops syncing after a password change", ["Alex", "John", "Sarah", "Priya"]),
    ("VPN error 809 when working from home", ["Alex", "Hannah", "Omar"]),
    ("Getting access to the shared Git repository", ["Alex", "Priya"]),
    ("How to order printing paper", ["Alex", "John", "Hannah", "Peter"]),
    ("How to submit expenses", ["John", "Sarah", "Steve"]),
    ("Spotting a phishing email: quick checklist", ["Alex", "John", "Sarah", "Omar", "Peter"]),
    ("Setting up a new laptop from the standard image", ["Alex", "Steve"]),
    ("How to book a meeting room", ["Sarah", "Alex"]),
    ("Printing confidential documents", ["John"]),
]


def stamp(today, days_ago, hour=10):
    moment = datetime.combine(today - timedelta(days=days_ago), datetime.min.time())
    return moment.replace(hour=hour, minute=15).strftime("%Y-%m-%d %H:%M:%S")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--date", help="Demo date as YYYY-MM-DD (default: today)")
    args = parser.parse_args()
    today = date.fromisoformat(args.date) if args.date else date.today()

    source = ROOT / db.database_connection
    backup = source.with_name(f"database.backup-{datetime.now():%Y%m%d-%H%M%S}.db")
    shutil.copy2(source, backup)
    print(f"Backup saved: {backup.name}")

    d, projects, personal = build_plan(today)

    connection = db.get_database_connection()
    try:
        with connection:
            run(connection, today, d, projects, personal)
    finally:
        connection.close()
    print_summary(today)


def run(connection, today, d, projects, personal):
    roles = dict(connection.execute("SELECT name, id FROM roles"))

    # --- employees -------------------------------------------------------
    # Remove exact duplicate accounts (same email), keeping the lowest id.
    seen = {}
    for emp_id, email in connection.execute("SELECT id, email FROM employees ORDER BY id").fetchall():
        key = email.lower()
        if key in seen:
            connection.execute("DELETE FROM project_members WHERE employee_id = ?", (emp_id,))
            connection.execute("UPDATE project_tasks SET assigned_to = NULL WHERE assigned_to = ?", (emp_id,))
            connection.execute("DELETE FROM personal_tasks WHERE employee_id = ?", (emp_id,))
            connection.execute("DELETE FROM profile_pictures WHERE employee_id = ?", (emp_id,))
            connection.execute("DELETE FROM employees WHERE id = ?", (emp_id,))
        else:
            seen[key] = emp_id

    # Email domain for everyone (admin included, nothing else about admin changes).
    connection.execute(
        "UPDATE employees SET email = REPLACE(email, ?, ?) WHERE email LIKE ?",
        (OLD_DOMAIN, NEW_DOMAIN, "%" + OLD_DOMAIN))

    # Add the extra employees (skip any that already exist).
    for first, second, username, role in NEW_PEOPLE:
        email = f"{first}.{second}{NEW_DOMAIN}".lower()
        if connection.execute("SELECT 1 FROM employees WHERE email = ?", (email,)).fetchone():
            continue
        connection.execute(
            "INSERT INTO employees (first_name, second_name, email, username, password, role_id) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (first, second, email, username, "pending", roles[role]))

    # One password for every non-admin account (each gets its own salted hash).
    rows = connection.execute(
        "SELECT e.id FROM employees e JOIN roles r ON r.id = e.role_id WHERE r.name != ?",
        (ADMIN_ROLE,)).fetchall()
    for (emp_id,) in rows:
        connection.execute("UPDATE employees SET password = ? WHERE id = ?",
                           (password_hash(DEMO_PASSWORD), emp_id))

    ids = {first: emp_id for emp_id, first in connection.execute(
        "SELECT e.id, e.first_name FROM employees e JOIN roles r ON r.id = e.role_id "
        "WHERE r.name != ?", (ADMIN_ROLE,))}

    # --- projects (replace all) -----------------------------------------
    for table in ("task_assignments", "project_tasks", "project_members", "projects"):
        connection.execute(f"DELETE FROM {table}")

    for (name, description, manager, status, start, deadline, members, tasks) in projects:
        cursor = connection.execute(
            "INSERT INTO projects (project_name, description, manager_id, status, start_date, deadline) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (name, description, ids[manager], status, d(start), d(deadline)))
        project_id = cursor.lastrowid
        for person in members:
            connection.execute(
                "INSERT INTO project_members (project_id, employee_id) VALUES (?, ?)",
                (project_id, ids[person]))
        for title, assignee, due, priority, done in tasks:
            assert assignee in members, f"{assignee} is not on {name}"
            connection.execute(
                "INSERT INTO project_tasks (project_id, title, assigned_to, due_date, completed, priority) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (project_id, title, ids[assignee], d(due), int(done), priority))

    # --- personal to-dos ---------------------------------------------------
    admin_ids = [row[0] for row in connection.execute(
        "SELECT e.id FROM employees e JOIN roles r ON r.id = e.role_id WHERE r.name = ?",
        (ADMIN_ROLE,))]
    marks = ",".join("?" * len(admin_ids)) or "NULL"
    connection.execute(f"DELETE FROM personal_tasks WHERE employee_id NOT IN ({marks})", admin_ids)
    for person, items in personal.items():
        for title, priority, due, done in items:
            connection.execute(
                "INSERT INTO personal_tasks (employee_id, title, completed, priority, due_date) "
                "VALUES (?, ?, ?, ?, ?)",
                (ids[person], title, int(done), priority, d(due)))

    # --- knowledge base (replace all) --------------------------------------
    for table in ("knowledge_post_likes", "knowledge_replies", "knowledge_posts", "knowledge_topics"):
        connection.execute(f"DELETE FROM {table}")

    topic_ids = {}
    for title, description, author in TOPICS:
        cursor = connection.execute(
            "INSERT INTO knowledge_topics (title, description, author_id, created_at) VALUES (?, ?, ?, ?)",
            (title, description, ids[author], stamp(today, 20)))
        topic_ids[title] = cursor.lastrowid

    post_ids = {}
    for topic, author, category, days_ago, title, content in POSTS:
        cursor = connection.execute(
            "INSERT INTO knowledge_posts (topic_id, author_id, title, content, category, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (topic_ids[topic], ids[author], title, content, category, stamp(today, days_ago)))
        post_ids[title] = cursor.lastrowid

    for title, author, days_ago, content in REPLIES:
        connection.execute(
            "INSERT INTO knowledge_replies (post_id, author_id, content, created_at) VALUES (?, ?, ?, ?)",
            (post_ids[title], ids[author], content, stamp(today, days_ago, hour=14)))

    for title, people in LIKES:
        for person in people:
            connection.execute(
                "INSERT OR IGNORE INTO knowledge_post_likes (post_id, employee_id) VALUES (?, ?)",
                (post_ids[title], ids[person]))


def print_summary(today):
    connection = db.get_database_connection()
    try:
        print(f"\nDemo data loaded for {today:%A %d %B %Y}.\n")
        print("Logins (password for every account except admin: password)")
        for first, email in connection.execute(
                "SELECT first_name, email FROM employees WHERE first_name IN ('Alex','John','Sarah') ORDER BY id"):
            print(f"  {first:<6} {email}")
        for table in ("employees", "projects", "project_tasks", "personal_tasks",
                      "knowledge_topics", "knowledge_posts", "knowledge_replies"):
            count = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"  {table:<18} {count}")
    finally:
        connection.close()


if __name__ == "__main__":
    main()