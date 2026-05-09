# LRU: Russian language learning tool

LRU is a tool designed to help you learn Russian vocabulary, alphabet, and grammar through Text-to-Speech (TTS) and interactive CLI feedback.

## Features

- **Daemon Style**: Runs in the background and responds to IPC commands.
- **Concurrency**: Supports non-blocking operations; stop or switch lessons instantly.
- **Dynamic Discovery**: Automatically scans the `files/` directory for new lessons.
- **TTS Integration**: Uses `RHVoice` for high-quality speech.

## Prerequisites

- **Python**: 3.10 or higher.
- **RHVoice**: (Optional) Must be installed for speech features.
- **dmenu**: (Optional) Required for the graphical selector (`lru-wm`).

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/gonzaru/lru
   cd lru
   ```

2. (Optional) Install development dependencies:
   ```bash
   pip install -r requirements-test.txt
   ```

## Configuration

You can customize ports, paths, and default features by editing `settings.py`.

## Usage

You can use the provided local wrappers (`./lru` and `./lru-cli`) or the Python scripts directly.

### 1. Manage the Daemon
```bash
./lru start    # Start the daemon
./lru stop     # Stop the daemon
./lru status   # Check if daemon is running
./lru list     # List all discovered lessons with their IDs
```

### 2. Play a Lesson
Find the ID of the lesson you want to play using `./lru list`, then:
```bash
./lru-cli play 3
```

**Optional: Graphical Selection (dmenu)**
If you use a Window Manager, you can use the selector script:
```bash
./lru-wm
```
This opens a searchable `dmenu` list. Simply select a lesson to start it immediately.

### 3. Control an Active Lesson
While a lesson is playing, use the `ctl` subcommand:
```bash
./lru-cli ctl next          # Move to next word
./lru-cli ctl prev          # Move to previous word
./lru-cli ctl repeat        # Repeat current word
./lru-cli ctl verb          # Conjugate the current verb (if available)
./lru-cli ctl toggle_robot  # Toggle TTS voice
./lru-cli ctl close         # Stop active lesson
```

### 4. Shutdown
To completely shut down the daemon from the CLI:
```bash
./lru-cli quit
```

## Development

Use the provided `Makefile` for common development tasks:

- **Full Cleanup & Check**: `make all`
- **Run Tests**: `make test`
- **Linting**: `make check`
- **Type Checking**: `make hinting`

## License
The GNU General Public License v3.0
