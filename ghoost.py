#!/usr/bin/env python3
"""
Ghoost - your personal AI-style manager.

Run it with NO arguments to get a simple, friendly menu - just type
the number of what you want to do and answer the questions.

Power users can also use it straight from the command line:
    python ghoost.py add-task "Buy groceries" --priority high --category home
    python ghoost.py list-tasks
    python ghoost.py done 1
    python ghoost.py add-note "Remember to call mom" --tags family
    python ghoost.py search-notes "mom"
    python ghoost.py add-reminder "Pay rent" 2026-07-01
    python ghoost.py reminders
    python ghoost.py dashboard

Everything is stored locally in ghoost_data.json - nothing leaves
your computer.
"""

import json
import os
import sys
from datetime import datetime, date

DATA_FILE = "ghoost_data.json"

PRIORITIES = {"1": "high", "2": "medium", "3": "low"}
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
PRIORITY_LABEL = {"high": "[HIGH]", "medium": "[MED] ", "low": "[LOW] "}


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}

    data.setdefault("tasks", [])
    data.setdefault("notes", [])
    data.setdefault("reminders", [])
    data.setdefault("next_id", {"task": 1, "note": 1, "reminder": 1})
    return data


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def next_id(data, kind):
    nid = data["next_id"].get(kind, 1)
    data["next_id"][kind] = nid + 1
    return nid


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

def add_task(data, text, priority="medium", category="general", due=None):
    if priority not in PRIORITY_ORDER:
        priority = "medium"
    task = {
        "id": next_id(data, "task"),
        "text": text,
        "done": False,
        "priority": priority,
        "category": category or "general",
        "due": due,
        "created": datetime.now().isoformat(timespec="seconds"),
    }
    data["tasks"].append(task)
    save_data(data)
    return task


def list_tasks(data, category=None, show_done=False):
    tasks = data["tasks"]
    if category:
        tasks = [t for t in tasks if t["category"].lower() == category.lower()]
    if not show_done:
        tasks = [t for t in tasks if not t["done"]]
    return sorted(
        tasks,
        key=lambda t: (
            t["done"],
            PRIORITY_ORDER.get(t["priority"], 1),
            t.get("due") or "9999-99-99",
        ),
    )


def find_task(data, task_id):
    for task in data["tasks"]:
        if task["id"] == task_id:
            return task
    return None


def complete_task(data, task_id):
    task = find_task(data, task_id)
    if task:
        task["done"] = True
        save_data(data)
    return task


def delete_task(data, task_id):
    for i, task in enumerate(data["tasks"]):
        if task["id"] == task_id:
            data["tasks"].pop(i)
            save_data(data)
            return True
    return False


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------

def add_note(data, text, tags=None):
    note = {
        "id": next_id(data, "note"),
        "text": text,
        "tags": tags or [],
        "created": datetime.now().isoformat(timespec="seconds"),
    }
    data["notes"].append(note)
    save_data(data)
    return note


def search_notes(data, keyword):
    keyword = (keyword or "").lower()
    if not keyword:
        return data["notes"]
    return [
        n for n in data["notes"]
        if keyword in n["text"].lower() or any(keyword in t.lower() for t in n["tags"])
    ]


# ---------------------------------------------------------------------------
# Reminders
# ---------------------------------------------------------------------------

def add_reminder(data, text, due):
    reminder = {
        "id": next_id(data, "reminder"),
        "text": text,
        "due": due,
        "done": False,
        "created": datetime.now().isoformat(timespec="seconds"),
    }
    data["reminders"].append(reminder)
    save_data(data)
    return reminder


def complete_reminder(data, reminder_id):
    for r in data["reminders"]:
        if r["id"] == reminder_id:
            r["done"] = True
            save_data(data)
            return r
    return None


def upcoming_reminders(data, days=30):
    today = date.today()
    upcoming = []
    for r in data["reminders"]:
        if r["done"]:
            continue
        try:
            due_date = datetime.fromisoformat(r["due"]).date()
        except (ValueError, TypeError):
            continue
        delta = (due_date - today).days
        if delta <= days:
            upcoming.append((r, delta))
    return sorted(upcoming, key=lambda x: x[1])


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def print_task(task):
    status = "x" if task["done"] else " "
    due = f" (due {task['due']})" if task.get("due") else ""
    label = PRIORITY_LABEL.get(task["priority"], "")
    print(f"  [{status}] #{task['id']} {label} {task['text']}  ({task['category']}){due}")


def print_note(note):
    tags = f"  #{' #'.join(note['tags'])}" if note["tags"] else ""
    print(f"  #{note['id']} ({note['created'][:10]}): {note['text']}{tags}")


def print_reminder(reminder, delta=None):
    status = "x" if reminder["done"] else " "
    flag = ""
    if delta is not None:
        if delta < 0:
            flag = "  (OVERDUE)"
        elif delta == 0:
            flag = "  (TODAY)"
        else:
            flag = f"  (in {delta}d)"
    print(f"  [{status}] #{reminder['id']} due {reminder['due']}: {reminder['text']}{flag}")


def print_dashboard(data):
    print("=" * 52)
    print(" GHOOST - your personal manager")
    print("=" * 52)

    open_tasks = list_tasks(data, show_done=False)
    print(f"\nOpen tasks ({len(open_tasks)} total, showing top 5):")
    if open_tasks:
        for t in open_tasks[:5]:
            print_task(t)
    else:
        print("  Nothing on your plate. Nice.")

    upcoming = upcoming_reminders(data, days=14)
    print("\nReminders in the next 14 days:")
    if upcoming:
        for r, delta in upcoming:
            print_reminder(r, delta)
    else:
        print("  None.")

    print(f"\nNotes saved: {len(data['notes'])}")
    print("=" * 52)


# ---------------------------------------------------------------------------
# Interactive menu - the easy way to use Ghoost
# ---------------------------------------------------------------------------

MENU = """
What would you like to do?
  1) View dashboard
  2) Add a task
  3) List open tasks
  4) Mark a task as done
  5) Delete a task
  6) Add a note
  7) Search notes
  8) Add a reminder
  9) View upcoming reminders
  10) Mark a reminder as done
  0) Quit
"""


def ask(prompt, default=None):
    suffix = f" [{default}]" if default else ""
    try:
        value = input(f"{prompt}{suffix}: ").strip()
    except EOFError:
        return default
    return value or default


def interactive_menu():
    data = load_data()
    print_dashboard(data)

    while True:
        print(MENU)
        choice = ask("Choose an option", "1")

        if choice == "1":
            print_dashboard(data)

        elif choice == "2":
            text = ask("What's the task?")
            if not text:
                continue
            print("  Priority: 1) High  2) Medium  3) Low")
            p = ask("  Priority", "2")
            priority = PRIORITIES.get(p, "medium")
            category = ask("  Category", "general")
            due = ask("  Due date (YYYY-MM-DD, optional)", "")
            task = add_task(data, text, priority, category, due or None)
            print(f"Added task #{task['id']}.")

        elif choice == "3":
            category = ask("Filter by category (leave blank for all)", "")
            tasks = list_tasks(data, category or None)
            if not tasks:
                print("  No open tasks.")
            for t in tasks:
                print_task(t)

        elif choice == "4":
            tid = ask("Task ID to mark done")
            if tid and tid.isdigit() and complete_task(data, int(tid)):
                print("Done! Nicely done.")
            else:
                print("Couldn't find that task.")

        elif choice == "5":
            tid = ask("Task ID to delete")
            if tid and tid.isdigit() and delete_task(data, int(tid)):
                print("Deleted.")
            else:
                print("Couldn't find that task.")

        elif choice == "6":
            text = ask("Note text")
            if not text:
                continue
            tags = ask("Tags (comma separated, optional)", "")
            tag_list = [t.strip() for t in tags.split(",") if t.strip()]
            note = add_note(data, text, tag_list)
            print(f"Saved note #{note['id']}.")

        elif choice == "7":
            keyword = ask("Search keyword (leave blank for all notes)", "")
            results = search_notes(data, keyword)
            if not results:
                print("  No matching notes.")
            for n in results:
                print_note(n)

        elif choice == "8":
            text = ask("What's the reminder?")
            due = ask("Due date (YYYY-MM-DD)")
            if text and due:
                r = add_reminder(data, text, due)
                print(f"Added reminder #{r['id']}.")
            else:
                print("Need both a description and a due date.")

        elif choice == "9":
            upcoming = upcoming_reminders(data, days=365)
            if not upcoming:
                print("  No reminders set.")
            for r, delta in upcoming:
                print_reminder(r, delta)

        elif choice == "10":
            rid = ask("Reminder ID to mark done")
            if rid and rid.isdigit() and complete_reminder(data, int(rid)):
                print("Reminder cleared.")
            else:
                print("Couldn't find that reminder.")

        elif choice == "0":
            print("Goodbye! Your data is saved in ghoost_data.json.")
            break

        else:
            print("Not a valid option, try again.")


# ---------------------------------------------------------------------------
# Command-line interface - for power users / scripting
# ---------------------------------------------------------------------------

HELP = __doc__


def parse_flag(args, name, default=None):
    if name in args:
        i = args.index(name)
        if i + 1 < len(args):
            value = args[i + 1]
            del args[i:i + 2]
            return value
        del args[i]
    return default


def main():
    args = sys.argv[1:]

    if not args:
        interactive_menu()
        return

    data = load_data()
    command = args[0]
    rest = args[1:]

    if command in ("-h", "--help", "help"):
        print(HELP)

    elif command == "add-task" and rest:
        priority = parse_flag(rest, "--priority", "medium")
        category = parse_flag(rest, "--category", "general")
        due = parse_flag(rest, "--due", None)
        text = " ".join(rest)
        task = add_task(data, text, priority, category, due)
        print(f"Added task #{task['id']}: {text}")

    elif command == "list-tasks":
        category = parse_flag(rest, "--category", None)
        show_all = "--all" in rest
        tasks = list_tasks(data, category, show_done=show_all)
        if not tasks:
            print("No tasks found.")
        for t in tasks:
            print_task(t)

    elif command == "done" and rest:
        if complete_task(data, int(rest[0])):
            print(f"Marked task #{rest[0]} as done.")
        else:
            print(f"Task #{rest[0]} not found.")

    elif command == "delete-task" and rest:
        if delete_task(data, int(rest[0])):
            print(f"Deleted task #{rest[0]}.")
        else:
            print(f"Task #{rest[0]} not found.")

    elif command == "add-note" and rest:
        tags_raw = parse_flag(rest, "--tags", "")
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else []
        text = " ".join(rest)
        note = add_note(data, text, tags)
        print(f"Saved note #{note['id']}.")

    elif command == "search-notes":
        results = search_notes(data, " ".join(rest))
        if not results:
            print("No matching notes.")
        for n in results:
            print_note(n)

    elif command == "add-reminder" and len(rest) >= 2:
        due = rest[-1]
        text = " ".join(rest[:-1])
        r = add_reminder(data, text, due)
        print(f"Added reminder #{r['id']}: {text} (due {due})")

    elif command == "reminders":
        upcoming = upcoming_reminders(data, days=365)
        if not upcoming:
            print("No reminders set.")
        for r, delta in upcoming:
            print_reminder(r, delta)

    elif command == "dashboard":
        print_dashboard(data)

    else:
        print(HELP)


if __name__ == "__main__":
    main()
