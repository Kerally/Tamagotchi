import os
import json
from pathlib import Path

# Путь к папке сейва
SAVE_FOLDER = Path.home() / "Documents" / "My Games" / "MyVirtualPet"
SAVE_FOLDER.mkdir(parents=True, exist_ok=True)
SAVE_FILE = SAVE_FOLDER / "pet_save.json"

def load_pet():
    """Загрузка питомца из JSON, если файл есть."""
    if SAVE_FILE.exists():
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
        return data
    return None

def save_pet(pet_data):
    """Сохраняем словарь питомца в JSON."""
    with open(SAVE_FILE, "w") as f:
        json.dump(pet_data, f, indent=4)
