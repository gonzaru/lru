"""menu"""

import os
from pathlib import Path
from typing import TypedDict
import settings


class MenuItem(TypedDict):
    """Represents a lesson entry in the menu."""

    name: str
    file: str


def discover_menu() -> dict[str, MenuItem]:
    """Dynamically discover vocabulary files and build the MENU."""
    base_files_dir = settings.BASE_DIR / "files"
    items: list[MenuItem] = []

    for root, _, files in os.walk(base_files_dir):
        for file in files:
            file_path = Path(root) / file

            is_json = file.endswith(".json")
            is_possessive_txt = file.endswith(".txt") and "possessive" in str(file_path)

            if is_json or is_possessive_txt:
                if "verbs/present" in str(file_path) and file != "all.json":
                    continue

                if file in ("all.json", "common_100.json"):
                    pass

                rel_path = file_path.relative_to(base_files_dir)
                parts = list(rel_path.with_suffix("").parts)

                if len(parts) >= 2 and parts[-1] == parts[-2]:
                    parts.pop()

                name = " ".join(parts)
                items.append({"name": name, "file": str(file_path.resolve())})

    items.sort(key=lambda x: x["name"])

    menu: dict[str, MenuItem] = {}
    for i, item in enumerate(items, start=1):
        menu[str(i)] = item

    return menu


MENU = discover_menu()
