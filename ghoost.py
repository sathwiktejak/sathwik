"""
Ghoost - a simple personal AI manager.

Keeps track of your tasks, notes, and reminders from the command line.
All data is stored locally in ghoost_data.json.

Usage:
    python ghoost.py add-task "Buy groceries"
    python ghoost.py list-tasks
    python ghoost.py done 1
    python ghoost.py add-note "Remember to call mom"
    python ghoost.py list-notes
    python ghoost.py add-reminder "Pay rent" 2026-07-01
    python ghoost.py list-reminders
"""

import json
import os
import sys
from datetime import datetime

DATA_FILE = "ghoost_data.json"


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"tasks": [], "notes": [], "reminders": []}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add_task(data, text):
    task = {
        "id": len(data["tasks"]) + 1,
        "text": text,
        "done": False,
        "created": datetime.now().isoformat(timespec="seconds"),
    }
    data["tasks"].append(task)
    save_data(data)
    print(f"Added task #{task['id']}: {text}")


def list_tasks(data):
    if not data["tasks"]:
        print('No tasks yet. Add one with: add-task "..."')
        return
    for task in data["tasks"]:
        status = "x" if task["done"] else " "
        print(f"[{status}] #{task['id']} {task['text']}")


def complete_task(data, task_id):
    for task in data["tasks"]:
        if task["id"] == task_id:
            task["done"] = True
            save_data(data)
            print(f"Marked task #{task_id} as done.")
            return
    print(f"Task #{task_id} not found.")


def add_note(data, text):
    note = {
        "id": len(data["notes"]) + 1,
        "text": text,
        "created": datetime.now().isoformat(timespec="seconds"),
    }
    data["notes"].append(note)
    save_data(data)
    print(f"Saved note #{note['id']}")


def list_notes(data):
    if not data["notes"]:
        print('No notes yet. Add one with: add-note "..."')
        return
    for note in data["notes"]:
        print(f"#{note['id']} ({note['created']}): {note['text']}")


def add_reminder(data, text, due):
    reminder = {
        "id": len(data["reminders"]) + 1,
        "text": text,
        "due": due,
        "created": datetime.now().isoformat(timespec="seconds"),
    }
    data["reminders"].append(reminder)
    save_data(data)
    print(f"Added reminder #{reminder['id']}: {text} (due {due})")


def list_reminders(data):
    if not data["reminders"]:
        print('No reminders yet. Add one with: add-reminder "..." YYYY-MM-DD')
        return
    today = datetime.now().date()
    for reminder in data["reminders"]:
        due_date = datetime.fromisoformat(reminder["due"]).date()
        overdue = " (OVERDUE)" if due_date < today else ""
        print(f"#{reminder['id']} due {reminder['due']}: {reminder['text']}{overdue}")


def print_help():
    print(__doc__)


def main():
    data = load_data()
    args = sys.argv[1:]

    if not args:
        print_help()
        return

    command = args[0]

    if command == "add-task" and len(args) > 1:
        add_task(data, " ".join(args[1:]))
    elif command == "list-tasks":
        list_tasks(data)
    elif command == "done" and len(args) > 1:
        complete_task(data, int(args[1]))
    elif command == "add-note" and len(args) > 1:
        add_note(data, " ".join(args[1:]))
    elif command == "list-notes":
        list_notes(data)
    elif command == "add-reminder" and len(args) > 2:
        add_reminder(data, " ".join(args[1:-1]), args[-1])
    elif command == "list-reminders":
        list_reminders(data)
    else:
        print_help()


if __name__ == "__main__":
    main()
