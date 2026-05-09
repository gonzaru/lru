"""utils"""

import json
import logging
import sys

from multiprocessing.connection import wait
from pathlib import Path
from typing import Any


logger = logging.getLogger(__name__)


def is_laptop(chassis_file: str | Path = "/sys/class/dmi/id/chassis_type") -> bool:
    """Determine if the system is a laptop."""
    try:
        chassis_type = Path(chassis_file).read_text(encoding="utf-8").strip()
        # 3 Desktop, 9 Laptop, 10 Notebook
        return chassis_type in {"9", "10"}
    except (FileNotFoundError, PermissionError):
        return False


def get_json_file(file_path: str | Path) -> list[Any]:
    """Load and return JSON data."""
    path = Path(file_path)
    if not path.is_file():
        return []

    try:
        with path.open("r", encoding="utf-8") as jfile:
            data = json.load(jfile)
            return data if isinstance(data, list) else [data]
    except json.JSONDecodeError as err:
        logger.error("Failed to parse JSON file %s: %s", path, err)
        return []


def write_data_file(wfile: str | Path, wtype: str, data: str) -> None:
    """Write string data to a file."""
    if not data:
        return

    with Path(wfile).open(wtype, encoding="utf-8") as file:
        file.write(f"{data}\n")


def get_data_file(rfile: str | Path, rtype: str = "r") -> str:
    """Read string data from a file."""
    path = Path(rfile)
    if path.is_file():
        with path.open(rtype, encoding="utf-8") as file:
            return file.read().rstrip("\n")
    return ""


def check_python_version(py_major: int, py_minor: int, py_micro: int) -> bool:
    """Check if the current Python version meets the requirements."""
    return sys.version_info >= (py_major, py_minor, py_micro)


def wait_listener(listener: Any, timeout: float = 0.5) -> bool:
    """Wait for a connection on a Listener."""
    internal_socket = getattr(getattr(listener, "_listener", None), "_socket", None)
    if internal_socket:
        return bool(wait([internal_socket], timeout=timeout))
    return True
