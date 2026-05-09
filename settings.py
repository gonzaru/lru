"""settings"""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
USER = os.getenv("USER", "unknown_user")
HOME = Path(os.getenv("HOME", "/tmp"))

# Networking
HOST_ADDR = "localhost"
HOST_PORT = 23821
HOST_AUTHKEY: bytes = b"lru host authkey"
HOST_ADDR_CTL = "localhost"
HOST_PORT_CTL = 23822
HOST_AUTHKEY_CTL: bytes = b"lru host authkey control"

# App State
PROGNAME = "lru"
LRU_LOCK = Path(f"/tmp/{USER}-lru.lock")
LRU_PID = Path(f"/tmp/{USER}-lru.pid")
MESSAGE_FILE = Path(f"/tmp/{USER}-lru-message.txt")

# RHVoice Config
RHVOICE_BIN_PATH = HOME / "opt" / "RHVoice" / "bin"
RHVOICE = RHVOICE_BIN_PATH / "RHVoice-test"
RHVOICE_LIB = HOME / "opt" / "RHVoice" / "lib"
RHVOICE_OPTS = "-p"

# System Requirements
PY_MAJOR = 3
PY_MINOR = 10
PY_MICRO = 0

# App Features
SPEAK_ROBOT = os.path.exists(RHVOICE)
VERB_DIR_PATH = BASE_DIR / "files" / "verbs" / "present"
VERB_FILE_EXTENSION = "json"
WM_BAR = bool(os.getenv("DISPLAY"))
