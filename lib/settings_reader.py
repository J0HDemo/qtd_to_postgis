"""
JSON settings reader

Reads default processing settings from JSON file (settings.json)

© 2024 Kirill Romashchenko
"""

class Reader:
    """
    Reader class. Reads settings.json, returns settings dictionary
    via the get_settings method
    """
    def __init__(self) -> None:
        """Reader's constructor class. Class instance reads settings.json,
        returns settings dictionary"""
        import json
        import os

        self.parent_folder = (os.path.abspath(os.path.join(os.getcwd(), os.pardir)))
        try:
            with open(f"settings.json") as settings_file:
                json_data = settings_file.read()
        except FileNotFoundError:
            with open(f"{self.parent_folder}/settings.json") as settings_file:
                json_data = settings_file.read()

        self.settings = json.loads(json_data)

    def get_settings(self) -> dict:
        """Returns settings dictionary"""
        return self.settings