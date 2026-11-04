from subprocess import run
import json
import os

FOLDERPATH = os.path.expanduser("~/.config/hypr/")

def command(com):
    try:
        result = run(
            com,
            shell=True,
            capture_output=True,
            text=True  # Automatically decodes stdout to a string
        )

        if result.returncode != 0:
            return None

        # Fixed: Added json.loads
        return json.loads(result.stdout.strip())

    except Exception:
        return None


def launch(app = 0):
    python_path = os.path.join(FOLDERPATH, "venv/bin/python")
    app_path = None
    match app:
        case 0:
            app_path = os.path.join(FOLDERPATH, "apps/calendarApp.py")
    run([python_path, app_path])