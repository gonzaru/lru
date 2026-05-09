"""draw"""

import shutil
import subprocess

import settings
from common import utils

_WMBAR_CMD = shutil.which("wmbarupdate")


def status_bar(line: str, show_msg: bool = True) -> None:
    """Update the status bar and optionally print the message."""
    if line:
        utils.write_data_file(settings.MESSAGE_FILE, "w", line)

    if show_msg:
        msg = utils.get_data_file(settings.MESSAGE_FILE)
        if msg:
            print(msg)

    if settings.WM_BAR and _WMBAR_CMD:
        subprocess.run([_WMBAR_CMD], check=True)
