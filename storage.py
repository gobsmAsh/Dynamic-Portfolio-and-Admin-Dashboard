
import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")


def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def get_next_id(items):
    if not items:
        return 1

    return max(item["id"] for item in items) + 1
