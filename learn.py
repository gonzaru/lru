"""learn"""

import random
import threading
import time

from multiprocessing.connection import Listener
from pathlib import Path
from typing import Any

import draw
import robot
import settings
from common import utils


class Learn:
    """Handles parsing and presenting vocabulary sets."""

    def __init__(self, *, cancel_event: threading.Event | None = None, **data: str):
        self.name = data["name"]
        self.file = Path(data["file"])
        self.cancel_event = cancel_event

    def is_cancelled(self) -> bool:
        """Check if the current lesson has been cancelled."""
        return self.cancel_event is not None and self.cancel_event.is_set()

    def read_alphabet(self) -> None:
        """Present the alphabet learning sequence."""
        draw.status_bar(f"<{self.name}>")
        robot.speak(self.name, robot.EN_VOICE)

        word_list = utils.get_json_file(self.file)
        robot_voice = robot.random_voice()

        for word in word_list:
            if self.is_cancelled():
                break
            if not isinstance(word, dict):
                continue
            upper_case = word.get("upper", "")
            lower_case = word.get("lower", "")
            draw.status_bar(f"{upper_case},{lower_case}")
            robot.speak(upper_case, robot_voice)
            time.sleep(0.2)

        draw.status_bar(f"</{self.name}>")

    def read_words(self) -> None:
        """Process general word sequences."""
        draw.status_bar(f"<{self.name}>")
        robot.speak(self.name, robot.EN_VOICE)

        word_list = utils.get_json_file(self.file)

        if self.name == "words all":
            random.shuffle(word_list)
        else:
            word_type = self.name.split(" ")[1] if " " in self.name else ""
            word_list = [w for w in word_list if w.get("type") == word_type]

        self.play(word_list)
        draw.status_bar(f"</{self.name}>")

    def read(self) -> None:
        """General reading logic for generic components."""
        draw.status_bar(f"<{self.name}>")
        robot.speak(self.name, robot.EN_VOICE)

        word_list = utils.get_json_file(self.file)
        if self.name == "verbs all":
            random.shuffle(word_list)

        self.play(word_list)
        draw.status_bar(f"</{self.name}>")

    def read_pronouns(self) -> None:
        """Process and present specific pronoun rules."""
        draw.status_bar(f"<{self.name}>")
        robot.speak(self.name, robot.EN_VOICE)
        robot_voice = robot.random_voice()

        if "personal" in self.name:
            word_list = utils.get_json_file(self.file)
            for word in word_list:
                if self.is_cancelled():
                    break
                if not isinstance(word, dict):
                    continue
                ru_text = word.get("ru", "")
                en_text = word.get("en", "")

                if "," in ru_text:
                    draw.status_bar(f"{ru_text.replace(',', '/')} ({en_text})")
                    for per in ru_text.split(","):
                        if self.is_cancelled():
                            break
                        robot.speak(per, robot_voice)
                else:
                    draw.status_bar(f"{ru_text} ({en_text})")
                    robot.speak(ru_text, robot_voice)
                time.sleep(0.2)

        elif "possessive" in self.name:
            file_content = utils.get_data_file(self.file)
            word_list = [w for w in file_content.split("\n") if w and not w.startswith("#")]

            for word in word_list:
                if self.is_cancelled():
                    break
                draw.status_bar(word.replace(",", "/"))
                for pos in word.split(","):
                    if self.is_cancelled():
                        break
                    cleaned_pos = pos.replace("(pl)", "").replace("(nom/gen)", "")
                    robot.speak(cleaned_pos, robot_voice)
                time.sleep(0.2)

        draw.status_bar(f"</{self.name}>")

    def play(self, word_list: list[dict[str, Any]]) -> None:
        """Main interaction loop waiting for CLI input."""
        word_list = [w for w in word_list if isinstance(w, dict)]
        if not word_list:
            return

        word_list_size = len(word_list)
        address = (settings.HOST_ADDR_CTL, settings.HOST_PORT_CTL)

        try:
            listener = Listener(address, authkey=settings.HOST_AUTHKEY_CTL)
        except Exception as err:
            draw.status_bar(f"Listener error: {err}")
            return

        try:
            msg = None
            keep_voice = False
            robot_voice = ""
            i = 0

            while True:
                if self.is_cancelled():
                    break

                if not keep_voice:
                    robot_voice = robot.random_voice()

                current_word = word_list[i]
                ru_text = current_word.get("ru", "")
                en_text = current_word.get("en", "")
                word_type = current_word.get("type", "")

                verb_file = (
                    Path(settings.VERB_DIR_PATH) / f"{ru_text}.{settings.VERB_FILE_EXTENSION}"
                )
                verb_icon = "✗↓" if word_type == "verb" and not verb_file.is_file() else ""
                word_type_str = f" {{{word_type}}}" if self.name == "words all" else ""

                draw.status_bar(
                    f"{robot.toggle_icon()}{ru_text.replace('+', '')} "
                    f"({en_text}){verb_icon}{word_type_str} "
                    f"[{i + 1}/{word_list_size}]"
                )

                if msg not in ("verb", "toggle_robot"):
                    robot.speak(ru_text, robot_voice)

                msg = None
                while not self.is_cancelled():
                    if utils.wait_listener(listener, timeout=0.5):
                        with listener.accept() as conn:
                            msg = conn.recv()
                        break

                if self.is_cancelled() or msg == "close":
                    break

                if msg == "prev":
                    i = (i - 1) % word_list_size
                elif msg == "next":
                    i = (i + 1) % word_list_size
                elif msg == "toggle_robot":
                    robot.toggle()
                elif msg == "verb" and word_type == "verb":
                    self._read_verb(ru_text, verb_file, robot_voice)

                keep_voice = msg == "repeat"
        finally:
            listener.close()

    def _read_verb(self, verb: str, file_path: Path, voice: str = "") -> None:
        """Helper to read verb declensions."""
        if not file_path.is_file():
            return

        draw.status_bar(f"[{verb}]")
        robot.speak(verb, voice)
        word_list = utils.get_json_file(file_path)

        for word in word_list:
            if self.is_cancelled():
                break
            if not isinstance(word, dict):
                continue
            pronoun = word.get("pronoun", "")
            verb_form = word.get("verb", "")

            draw.status_bar(f"{pronoun.replace(',', '/')} {verb_form}")

            if "," in pronoun:
                parts = pronoun.split(",")
                for p in parts:
                    if self.is_cancelled():
                        break
                    robot.speak(p.strip(), voice)
                robot.speak(verb_form, voice)
            else:
                robot.speak(f"{pronoun} {verb_form}", voice)

            time.sleep(0.2)
