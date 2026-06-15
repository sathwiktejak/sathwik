# sathwik

## Ghoost - Personal AI Manager

Ghoost is a personal manager that runs from the command line. It tracks tasks (with priority, category, and due dates), notes (with tags), and reminders, all stored locally in ghoost_data.json. Nothing leaves your computer.

### Easiest way to use it

Run it with no arguments and follow the on-screen menu:

```
python ghoost.py
```

### Command-line usage

```
python ghoost.py add-task "Buy groceries" --priority high --category home --due 2026-06-20
python ghoost.py list-tasks
python ghoost.py list-tasks --category home
python ghoost.py list-tasks --all
python ghoost.py done 1
python ghoost.py delete-task 1
python ghoost.py add-note "Remember to call mom" --tags family
python ghoost.py search-notes "mom"
python ghoost.py add-reminder "Pay rent" 2026-07-01
python ghoost.py reminders
python ghoost.py dashboard
```

Priorities are high, medium, or low. Tasks default to medium priority and the "general" category if not specified.
