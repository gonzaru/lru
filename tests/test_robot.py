import robot
import settings
import pytest
from unittest.mock import patch


def test_speak_missing_binary(monkeypatch):
    monkeypatch.setattr(settings, "RHVOICE", "/non/existent/path")
    monkeypatch.setattr(settings, "SPEAK_ROBOT", True)
    try:
        robot.speak("hello")
    except SystemExit:
        pytest.fail("robot.speak raised SystemExit on missing binary")


def test_random_voice():
    voice = robot.random_voice()
    assert isinstance(voice, str)
    assert any(voice in v["all"] for v in robot.VOICES.values())


def test_speak_enabled(monkeypatch):
    monkeypatch.setattr(settings, "SPEAK_ROBOT", True)
    with patch("subprocess.run") as mock_run:
        robot.speak("тест", "Elena")
        assert mock_run.called
        cmd = mock_run.call_args[0][0]
        assert "Elena" in cmd


def test_speak_disabled(monkeypatch):
    monkeypatch.setattr(settings, "SPEAK_ROBOT", False)
    with patch("subprocess.run") as mock_run:
        robot.speak("тест")
        assert not mock_run.called


def test_welcome(monkeypatch):
    monkeypatch.setattr(settings, "SPEAK_ROBOT", True)
    with patch("robot.speak") as mock_speak:
        with patch("draw.status_bar") as mock_draw:
            robot.welcome()
            assert mock_speak.called
            assert mock_draw.called


def test_goodbye(monkeypatch):
    monkeypatch.setattr(settings, "SPEAK_ROBOT", True)
    with patch("robot.speak") as mock_speak:
        with patch("draw.status_bar") as mock_draw:
            robot.goodbye()
            assert mock_speak.called
            assert mock_draw.called


def test_is_enable():
    settings.SPEAK_ROBOT = True
    assert robot.is_enable() is True
    settings.SPEAK_ROBOT = False
    assert robot.is_enable() is False


def test_enable_disable_toggle():
    robot.enable()
    assert settings.SPEAK_ROBOT is True
    robot.disable()
    assert settings.SPEAK_ROBOT is False
    robot.toggle()
    assert settings.SPEAK_ROBOT is True
    robot.toggle()
    assert settings.SPEAK_ROBOT is False


def test_toggle_icon():
    robot.enable()
    assert robot.toggle_icon() == ""
    robot.disable()
    assert robot.toggle_icon() == "✗♪"
