import lru
from unittest.mock import patch


def test_daemon_init():
    daemon = lru.LRUDaemon()
    assert daemon.running is False
    assert daemon.active_thread is None


def test_get_pid(tmp_path, monkeypatch):
    import settings

    pid_file = tmp_path / "lru.pid"
    monkeypatch.setattr(settings, "LRU_PID", pid_file)

    daemon = lru.LRUDaemon()
    assert daemon.get_pid() is None

    pid_file.write_text("1234")
    assert daemon.get_pid() == 1234


def test_is_alive(monkeypatch):
    daemon = lru.LRUDaemon()
    monkeypatch.setattr(daemon, "get_pid", lambda: 999999)  # Unlikely PID
    assert daemon.is_alive() is False


def test_cleanup(tmp_path, monkeypatch):
    import settings

    lock = tmp_path / "lock"
    pid = tmp_path / "pid"
    msg = tmp_path / "msg"
    lock.mkdir()
    pid.write_text("1")
    msg.write_text("test")

    monkeypatch.setattr(settings, "LRU_LOCK", lock)
    monkeypatch.setattr(settings, "LRU_PID", pid)
    monkeypatch.setattr(settings, "MESSAGE_FILE", msg)

    daemon = lru.LRUDaemon()
    daemon.cleanup()

    assert not lock.exists()
    assert not pid.exists()
    assert not msg.exists()


def test_get_args():
    with patch("sys.argv", ["lru", "start"]):
        args = lru.get_args()
        assert args.command == "start"
