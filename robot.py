"""robot"""

import logging
import os
import random
import subprocess

import draw
import settings


logger = logging.getLogger(settings.PROGNAME)

VOICES: dict[str, dict[str, tuple[str, ...] | str]] = {
    "russian": {
        "all": (
            "Aleksandr",
            "Elena",
            "Anna",
            "Irina",
            "Arina",
            "Yuriy",
            "Pavel",
            "Victoria",
        ),
        "default": "Aleksandr",
    },
    "ukrainian": {
        "all": ("Anatol", "Natalia", "Volodymyr"),
        "default": "Anatol",
    },
    "english": {
        "all": ("Alan", "Bdl", "Clb", "Slt"),
        "default": "Alan",
    },
}

DEFAULT_LANG = "russian"
EN_VOICE = "Alan"
ERROR_VOICE = "Alan"

WELCOME_LIST: tuple[str, ...] = (
    "добро пожаловать",
    "за здоровье",
    "здравствуйте",
    "как ваши дела?",
    "как дела?",
    "как поживаешь?",
    "привет",
)

GOODBYE_LIST: tuple[str, ...] = (
    "большое спасибо",
    "до свидания",
    "до скорой встречи",
    "очень приятно",
    "пока",
    "приятно познакомиться",
    "рад тебя видеть",
    "спасибо",
    "счастливого пути",
    "увидимся",
    "удачи",
    "хорошего дня",
)


def random_voice() -> str:
    """Select a random voice based on default language."""
    voices = VOICES[DEFAULT_LANG]["all"]
    return random.choice(voices)


def is_enable() -> bool:
    """Check if robot text-to-speech is enabled."""
    return bool(settings.SPEAK_ROBOT)


def speak(word: str, voice: str = "") -> None:
    """Execute RHVoice subprocess."""
    if not is_enable():
        return

    svoice = voice or random_voice()

    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = str(settings.RHVOICE_LIB)

    cmd = [str(settings.RHVOICE), settings.RHVOICE_OPTS, svoice]

    try:
        subprocess.run(
            cmd,
            input=word.encode("utf-8"),
            env=env,
            check=True,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        logger.error("command '%s' not found", settings.RHVOICE)
        return
    except subprocess.CalledProcessError as err:
        logger.error("RHVoice failed to speak: %s", err)


def welcome() -> None:
    """Trigger welcome sequence."""
    msg = random.choice(WELCOME_LIST)
    draw.status_bar(msg.capitalize())
    speak(msg)


def goodbye() -> None:
    """Trigger goodbye sequence."""
    msg = random.choice(GOODBYE_LIST)
    draw.status_bar(msg.capitalize())
    speak(msg)


def enable() -> None:
    """Enable robot text-to-speech."""
    settings.SPEAK_ROBOT = True


def disable() -> None:
    """Disable robot text-to-speech."""
    settings.SPEAK_ROBOT = False


def toggle() -> None:
    """Toggle robot text-to-speech."""
    settings.SPEAK_ROBOT = not is_enable()


def toggle_icon() -> str:
    """Return status bar icon indicating mute state."""
    return "" if is_enable() else "✗♪"
