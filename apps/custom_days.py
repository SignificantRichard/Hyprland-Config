import os
import json

class CustomDaysManager:
    def __init__(self, json_path):
        self.json_path = json_path
        self.custom_days = {}
        self.load()

    def load(self):
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, "r") as f:
                    data = json.load(f)
                    # Normalize simple strings to dict format: {"title": "..."}
                    for key, val in data.items():
                        if isinstance(val, str):
                            self.custom_days[key] = {"title": val}
                        else:
                            self.custom_days[key] = val
            except Exception as e:
                print(f"Error loading custom days from {self.json_path}: {e}")
        else:
            print(f"Custom days file not found at: {self.json_path}")

    def get_event(self, year, month, day):
        """
        Looks up event for a given date.
        Checks YYYY-MM-DD first, then recurring MM-DD.
        """
        full_key = f"{year:04d}-{month:02d}-{day:02d}"
        recurring_key = f"{month:02d}-{day:02d}"

        return self.custom_days.get(full_key) or self.custom_days.get(recurring_key)