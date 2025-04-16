import json
import os

folder_path = os.path.dirname(os.path.abspath(__file__))
theme_file_path = os.path.join(folder_path, "theme.json")


def get_modes():
    if os.path.exists(theme_file_path):
        with open(theme_file_path) as f:
            theme = json.load(f)
            light = {**theme, **theme["colorSchemes"]["light"]}
            dark = {**theme, **theme["colorSchemes"]["dark"]}

            return {"light": light, "dark": dark, "mode": theme.get("mode", "light")}
    else:
        return {"light": {}, "dark": {}, "mode": "light"}
