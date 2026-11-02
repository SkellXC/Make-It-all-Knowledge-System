"""One place for every status colour in the app.

Meaning (keep to this everywhere):
  green  = done            blue  = in progress     grey = not started / to do
  red    = overdue / error amber = due today/soon  slate = upcoming (not urgent)
"""

# Workflow status
DONE = "#22c55e"
IN_PROGRESS = "#3b82f6"
NOT_STARTED = "#9ca3af"

# Deadline urgency
OVERDUE = "#ef4444"
DUE_SOON = "#f59e0b"
UPCOMING = "#64748b"
NO_DATE = "#d1d5db"

# Darker / paler versions for text and tinted cards (readable on white)
OVERDUE_TEXT = "#b3261e"
OVERDUE_TINT = "#fce8e6"
DONE_TEXT = "#2e7d32"
DONE_TINT = "#e8f5e9"

# Empty progress-bar track and navigation accent
TRACK = "#d8e0e5"
ACCENT = "#476da6"