#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""lru"""

import argparse
import os
import signal
import sys
import threading
import time

from multiprocessing.connection import Listener
from typing import Any

import draw
import learn
import log
import robot
from common import utils
import menu
import settings

logger = log.setup(settings.PROGNAME)


class LRUDaemon:
    """Managing class for the LRU daemon lifecycle."""

    def __init__(self) -> None:
        self.active_thread: threading.Thread | None = None
        self.cancel_event = threading.Event()
        self.running = False
        self.menu: dict[str, menu.MenuItem] = {}

    @staticmethod
    def write_pid_file() -> None:
        """Write the current process ID to the PID file."""
        utils.write_data_file(settings.LRU_PID, "w", str(os.getpid()))

    @staticmethod
    def get_pid() -> int | None:
        """Read the process ID from the PID file."""
        pid_str = utils.get_data_file(settings.LRU_PID)
        return int(pid_str) if pid_str.isdigit() else None

    def is_alive(self) -> bool:
        """Check if the background daemon process is running."""
        pid = self.get_pid()
        if pid is None:
            return False
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False

    def checkout(self) -> bool:
        """Ensure no previous instance is running, handling stale files."""
        if not self.is_alive():
            self.cleanup()
            return True

        msg = f"{settings.PROGNAME} is already running (PID: {self.get_pid()})"
        logger.error(msg)
        draw.status_bar(msg, show_msg=False)
        robot.speak(msg, robot.ERROR_VOICE)
        return False

    @staticmethod
    def cleanup() -> None:
        """Remove lock, pid, and message files."""
        files_to_remove = (settings.LRU_LOCK, settings.LRU_PID, settings.MESSAGE_FILE)
        for file_path in files_to_remove:
            try:
                if file_path.is_dir():
                    file_path.rmdir()
                elif file_path.is_file() or file_path.is_symlink():
                    file_path.unlink()
            except OSError as err:
                logger.error("Error removing %s: %s", file_path, err)

    def setup(self) -> None:
        """Configure signals and write necessary state files."""
        for sig in (signal.SIGHUP, signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, self.signal_handler)
        self.write_pid_file()
        settings.LRU_LOCK.mkdir(parents=True, exist_ok=True)
        self.menu = menu.discover_menu()

    def signal_handler(self, signum: int, _frame: Any) -> None:
        """Handle termination signals."""
        sig_name = signal.Signals(signum).name
        logger.error("Received signal %s. Shutting down...", sig_name)
        self.running = False

    def run_lesson_thread(self, data: dict[str, Any]) -> None:
        """Execute a lesson in a background thread."""
        lru_inst = learn.Learn(cancel_event=self.cancel_event, **data)
        try:
            name = data["name"]
            if "alphabet" in name:
                lru_inst.read_alphabet()
            elif "words" in name:
                lru_inst.read_words()
            elif "pronouns" in name:
                lru_inst.read_pronouns()
            else:
                lru_inst.read()
        except Exception as err:
            logger.error("Lesson thread error: %s", err)

    def start(self) -> None:
        """Start the main listener loop."""
        if not self.checkout():
            return

        self.setup()
        robot.welcome()
        self.running = True

        address = (settings.HOST_ADDR, settings.HOST_PORT)
        try:
            listener = Listener(address, authkey=settings.HOST_AUTHKEY)
        except Exception as err:
            logger.error("Failed to start listener: %s", err)
            self.cleanup()
            return

        try:
            while self.running:
                if not utils.wait_listener(listener, timeout=1.0):
                    continue

                with listener.accept() as conn:
                    msg = conn.recv()

                    if msg == "quit":
                        self.running = False
                        break

                    if msg in self.menu:
                        if self.active_thread and self.active_thread.is_alive():
                            self.cancel_event.set()
                            self.active_thread.join()
                        self.cancel_event.clear()

                        menu_item = self.menu[msg]
                        data = {"name": menu_item["name"], "file": menu_item["file"]}

                        self.active_thread = threading.Thread(
                            target=self.run_lesson_thread, args=(data,), daemon=True
                        )
                        self.active_thread.start()
                    else:
                        err_msg = f"Error: unknown msg {msg}"
                        logger.error(err_msg)
                        draw.status_bar(err_msg, show_msg=False)
                        robot.speak(err_msg, robot.ERROR_VOICE)
        finally:
            if self.active_thread and self.active_thread.is_alive():
                self.cancel_event.set()
                self.active_thread.join()
            robot.goodbye()
            self.cleanup()
            draw.status_bar("")
            listener.close()

    def stop(self) -> None:
        """Stop the running daemon."""
        if not self.is_alive():
            logger.error("command %s is not running", settings.PROGNAME)
            return

        pid = self.get_pid()
        if pid:
            try:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.5)
                if self.is_alive():
                    os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        self.cleanup()


def get_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="LRU: Russian language learning tool")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Commands")

    subparsers.add_parser("start", help="Start the daemon")
    subparsers.add_parser("stop", help="Stop the daemon")
    subparsers.add_parser("restart", help="Restart the daemon")
    subparsers.add_parser("status", help="Check daemon status")
    subparsers.add_parser("list", help="List available lessons")

    return parser.parse_args()


def main() -> int:
    """Main execution function."""
    daemon = LRUDaemon()
    args = get_args()

    if args.command == "start":
        daemon.start()
    elif args.command == "stop":
        daemon.stop()
    elif args.command == "restart":
        daemon.stop()
        daemon.start()
    elif args.command == "status":
        print(f"{settings.PROGNAME} is running: {daemon.is_alive()}")
    elif args.command == "list":
        m = menu.discover_menu()
        print(f"\n{'ID':<5} | {'Lesson Name':<40}")
        print("-" * 50)
        for key, item in sorted(m.items(), key=lambda x: int(x[0])):
            print(f"{key:<5} | {item['name']:<40}")
        print()
    return 0


if __name__ == "__main__":
    if not utils.check_python_version(settings.PY_MAJOR, settings.PY_MINOR, settings.PY_MICRO):
        logger.error(
            "Needs python %s.%s.%s or higher",
            settings.PY_MAJOR,
            settings.PY_MINOR,
            settings.PY_MICRO,
        )
        sys.exit(1)
    sys.exit(main())
