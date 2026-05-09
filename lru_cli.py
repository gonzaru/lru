#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""lru-cli"""

import argparse
import sys
from multiprocessing.connection import Client

import log
from settings import (
    HOST_ADDR,
    HOST_PORT,
    HOST_AUTHKEY,
    HOST_ADDR_CTL,
    HOST_PORT_CTL,
    HOST_AUTHKEY_CTL,
)

logger = log.setup("lru-cli")


def lru_send(host: str, port: int, authkey: bytes, message: str) -> int:
    """Send a message to the LRU listener."""
    if not all((host, port, authkey, message)):
        logger.error("missing parameters")
        return 1

    try:
        with Client((host, port), authkey=authkey) as conn:
            conn.send(message)
        return 0
    except ConnectionRefusedError:
        if port == HOST_PORT:
            logger.error("Daemon not running. Start it with './lru start'")
        else:
            logger.error("No active lesson to control.")
        return 1
    except Exception as err:
        logger.error("Unexpected error: %s", err)
        return 1


def main() -> int:
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(description="LRU IPC Client")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Navigation and control")

    # Command: play ID
    lesson_parser = subparsers.add_parser("play", help="Start a lesson by ID")
    lesson_parser.add_argument("id", type=str, help="The numeric ID of the lesson")

    # Command: ctl {next, prev, ...}
    control_parser = subparsers.add_parser("ctl", help="Control an active lesson")
    control_parser.add_argument(
        "action",
        choices=["next", "prev", "repeat", "close", "toggle_robot", "verb"],
        help="Control action",
    )

    # Command: quit
    subparsers.add_parser("quit", help="Shut down the LRU daemon")

    args = parser.parse_args()

    if args.command == "play":
        return lru_send(HOST_ADDR, HOST_PORT, HOST_AUTHKEY, args.id)
    elif args.command == "ctl":
        return lru_send(HOST_ADDR_CTL, HOST_PORT_CTL, HOST_AUTHKEY_CTL, args.action)
    elif args.command == "quit":
        return lru_send(HOST_ADDR, HOST_PORT, HOST_AUTHKEY, "quit")

    return 1


if __name__ == "__main__":
    sys.exit(main())
