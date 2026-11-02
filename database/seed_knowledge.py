"""Add fictional examples with python -m database.seed_knowledge; safe to repeat."""

from contextlib import closing

from database.database import get_database_connection, get_employee_by_email
from database.knowledge import add_post, add_reply, get_replies, set_post_like
from database.knowledge_schema import create_knowledge_tables


DEMO_POSTS = [
    ("employee", "technical", "Why is PySide6 missing even though I installed it?",
     "The terminal says PySide6 is installed, but running the app from my editor still gives "
     "'No module named PySide6'. Has anyone else had this?\n\n"
     "It turned out my editor was using a different Python interpreter. Selecting the project's "
     ".venv interpreter fixed it. Sharing this in case it saves someone an afternoon.",
     "Good catch. Running python -m pip from the selected interpreter helps avoid this too."),
    ("manager", "technical", "A small Git habit that prevents a lot of merge conflicts",
     "Before starting a new page, pull the latest main branch and create a branch for your work. "
     "Keep changes focused on your own module.\n\n"
     "If you need to change shared styles or database functions, let the team know first. "
     "A short message usually saves a much longer conflict resolution session later.",
     "Agreed — especially when two pages need the same database function."),
    ("team leader", "technical", "Printer connected, but nothing comes out — quick checklist",
     "Before reinstalling anything, check the selected printer, clear any paused jobs and "
     "make sure the printer is online. Then try a Windows test page.\n\n"
     "If the test page works but your document does not, export it to PDF and try again. "
     "Please add any other quick fixes that have worked for you.",
     "Checking that the job was not sent to an old printer solved it for me."),
    ("manager", "non-technical", "Where do we order printing paper and stationery?",
     "For routine office supplies, send the office coordinator a short list with the item, "
     "quantity and delivery location. Check the stationery cupboard before placing a request.\n\n"
     "If something is needed urgently, include the date it is required rather than just writing 'urgent'.",
     "Thanks! Including the room number makes deliveries much easier to sort."),
    ("employee", "non-technical", "What makes a useful handover note?",
     "I am putting together a handover for a colleague and trying to keep it useful without "
     "writing a whole manual. My current structure is: what is done, what is next, where the files "
     "are, and who to ask.\n\n"
     "What is one thing you wish people included more often in handovers?",
     "Open questions and known problems. Knowing what is unfinished is just as useful as knowing what works."),
    ("team leader", "non-technical", "How to book a meeting room without double-booking",
     "Check the shared room calendar before sending invitations, then include the room as a "
     "resource in the booking. A meeting invitation by itself does not reserve the room.\n\n"
     "If a meeting is cancelled, release the room as well so someone else can use it.",
     "A clear meeting title and an expected finish time are helpful too."),
]

EXTRA_REPLIES = [
    ["The interpreter path in the editor should end in .venv/Scripts/python.exe on Windows.",
     "That fixed it for me too. I had installed the package into my global Python."],
    ["Small pull requests are much easier to review before merging.",
     "Please leave shared database files out of unrelated changes where possible."],
    ["A paused print queue was the cause on my machine. Resuming it was enough.",
     "If it still fails, include the printer name and exact error in your support request."],
    ["Is there a preferred paper size for routine printing?",
     "Please specify the size in the request so the coordinator can confirm availability."],
    ["A short list of file locations would help me pick up the work.",
     "I also include the next deadline and any decisions that still need an answer."],
    ["Please include any equipment needed, such as a screen or video-call setup.",
     "Releasing cancelled bookings helped us find a room this morning."],
]
for index, post in enumerate(DEMO_POSTS):
    DEMO_POSTS[index] = (*post[:4], [post[4], *EXTRA_REPLIES[index]])

DEMO_POSTS += [
    ("employee", "technical", "Why does the office Wi-Fi keep disconnecting?",
     "My laptop reconnects every few minutes while other devices seem fine. What should I check before raising a support request?",
     ["First check whether it happens near another access point as well.",
      "For me, forgetting the network and reconnecting resolved an old saved configuration.",
      "Please record the time, location and any error message if it continues."]),
    ("team leader", "technical", "How can I share an error message that is useful to support?",
     "A screenshot saying 'it does not work' is difficult to investigate. What details should we include when reporting a software problem?",
     ["Include what you tried, what you expected and what actually happened.",
      "The application version and exact steps to repeat the issue are useful too.",
      "Remove passwords and sensitive information before sharing screenshots or logs."]),
    ("manager", "technical", "Which file should I send when a spreadsheet formula breaks?",
     "A formula works on my computer but shows an error for a colleague. Is there a simple way to narrow down the cause?",
     ["Check whether the workbook links to a file only you can access.",
      "We found a missing sheet name in a copied formula last week.",
      "A small example with fictional values is easier to investigate than the entire workbook."]),
    ("employee", "technical", "My second monitor is blank. What should I try first?",
     "The monitor has power but does not show my desktop. I would like a quick checklist before requesting replacement equipment.",
     ["Check the selected input on the monitor and reseat the display cable.",
      "Windows + P lets you choose Extend or Duplicate. Mine was set to PC screen only.",
      "Trying another cable helped us confirm that the monitor itself was working."]),
    ("team leader", "technical", "How do we avoid losing changes when sharing documents?",
     "We have several copies with names like final-v2 and final-new. What has worked for your team?",
     ["Keep one shared working copy and link to it instead of emailing attachments.",
      "Use version history when the shared storage supports it.",
      "Agree on the file owner and tell them before making a major structural change."]),
    ("manager", "technical", "What should I check before a video meeting?",
     "The last meeting started late because the microphone used the wrong device. Here is a place to collect quick checks.",
     ["Test the microphone and speaker inside the meeting app before joining.",
      "Check that the app has permission to use your camera.",
      "A headset reduced echo when several people joined from the same room."]),
    ("employee", "non-technical", "What should a new starter know on their first morning?",
     "I am helping a new colleague settle in. What practical information would have made your first day easier?",
     ["A named contact and a short plan for the first morning would help.",
      "Show them where to find shared guidance and how to ask for equipment support.",
      "A quick introduction to the team makes it easier to ask questions later."]),
    ("manager", "non-technical", "How do you keep meetings focused?",
     "We sometimes finish meetings without a clear next step. What small changes have helped your team?",
     ["Share a short agenda with the decision we need to make.",
      "Finish with actions, owners and dates rather than a long summary.",
      "If a discussion needs only two people, take it outside the main meeting."]),
    ("team leader", "non-technical", "What information belongs in an equipment request?",
     "I need to request a replacement headset. What details make the request easier to handle? This is a sample discussion, not an official purchasing policy.",
     ["Include the equipment, the problem and your work location.",
      "Mention whether the item is needed for a particular date.",
      "The office coordinator can confirm the correct approval route."]),
    ("employee", "non-technical", "How can we make handovers easier before annual leave?",
     "I want colleagues to find the right information while I am away without sending a long email. What is essential?",
     ["List current work, upcoming dates and a contact for each open item.",
      "Check that the covering colleague can access the linked files.",
      "A brief conversation before you leave can clarify anything the notes miss."]),
    ("manager", "non-technical", "What makes a useful post in this Knowledge Base?",
     "We want answers that are easy for someone else to use later. What should authors include?",
     ["Use a clear title that describes the question or solution.",
      "Explain the steps that worked, including anything you tried unsuccessfully.",
      "Add context, but keep personal or confidential information out of examples."]),
    ("team leader", "non-technical", "How should we record decisions after a team meeting?",
     "We remember the discussion but sometimes disagree about the decision afterwards. What is a practical format?",
     ["Write down the decision, the reason and the next action.",
      "Add the date and who is responsible for following up.",
      "Share the note with attendees so they can point out anything misunderstood."]),
]


def seed_demo_posts():
    users = {}
    for role, email in [
        ("employee", "alex.smith@makeitall.com"),
        ("manager", "sarah.jones@makeitall.com"),
        ("team leader", "john.paul@makeitall.com"),
    ]:
        employee = get_employee_by_email(email)
        if employee is None:
            raise ValueError(f"Demo account not found: {email}. No accounts were created or changed.")
        users[role] = {"id": employee[0], "email": employee[3]}

    with closing(get_database_connection()) as connection:
        create_knowledge_tables(connection)
        participants = [
            {"id": row[0], "email": row[1]}
            for row in connection.execute("""
                SELECT e.id, e.email FROM employees e JOIN roles r ON r.id = e.role_id
                WHERE r.name != 'administrator' ORDER BY e.id LIMIT 6
            """)
        ]

    post_ids = []
    for index, (role, category, title, content, replies) in enumerate(DEMO_POSTS):
        author = users[role]
        with closing(get_database_connection()) as connection:
            existing = connection.execute(
                "SELECT id FROM knowledge_posts WHERE author_id = ? AND title = ?",
                (author["id"], title),
            ).fetchone()
        post_id = existing[0] if existing else add_post(author, None, title, content, category)
        existing_replies = {(row["author_id"], row["content"]) for row in get_replies(post_id)}
        commenters = [users["manager"] if role != "manager" else users["employee"],
                      users["team leader"], author]
        for commenter, reply in zip(commenters, replies):
            if (commenter["id"], reply) not in existing_replies:
                add_reply(commenter, post_id, reply)
        for participant in participants[:1 + index % len(participants)]:
            set_post_like(participant, post_id, True)
        post_ids.append(post_id)
    return post_ids


if __name__ == "__main__":
    print(f"Demo feed ready: {len(seed_demo_posts())} posts. Existing posts were kept.")
