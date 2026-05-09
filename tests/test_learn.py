import learn
import pytest
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock


class TestClass:
    def test__init__(self):
        data = {"name": "food", "file": "files/food/vegetables.json"}
        lru_inst = learn.Learn(cancel_event=None, **data)
        assert lru_inst.name == "food"
        assert str(lru_inst.file) == "files/food/vegetables.json"

    def test_play_robustness(self, monkeypatch):
        lru = learn.Learn(cancel_event=None, name="test", file="test.json")
        monkeypatch.setattr("robot.speak", lambda *args: None)
        monkeypatch.setattr("draw.status_bar", lambda *args: None)
        bad_list: list[Any] = [{"ru": "test", "en": "test"}, "not a dict"]

        class MockConn:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

            @staticmethod
            def recv():
                return "close"

        class MockListener:
            def __init__(self, *args, **kwargs):
                pass

            @staticmethod
            def accept():
                return MockConn()

            def close(self):
                pass

            @staticmethod
            def fileno():
                return 0

        monkeypatch.setattr("learn.Listener", MockListener)
        monkeypatch.setattr("common.utils.wait_listener", lambda *args, **kwargs: True)

        try:
            lru.play(bad_list)
        except Exception as e:
            pytest.fail(f"lru.play crashed with bad data: {e}")

    def test_read_alphabet(self, monkeypatch):
        lru = learn.Learn(name="alphabet", file="dummy.json")
        mock_data = [{"upper": "А", "lower": "а"}, {"upper": "Б", "lower": "б"}]
        monkeypatch.setattr("common.utils.get_json_file", lambda x: mock_data)
        monkeypatch.setattr("robot.speak", MagicMock())
        monkeypatch.setattr("draw.status_bar", MagicMock())

        lru.read_alphabet()
        assert True

    def test_read_words(self, monkeypatch):
        lru = learn.Learn(name="words noun", file="dummy.json")
        mock_data = [
            {"ru": "дом", "en": "house", "type": "noun"},
            {"ru": "быстро", "en": "fast", "type": "adverb"},
        ]
        monkeypatch.setattr("common.utils.get_json_file", lambda x: mock_data)

        mock_play = MagicMock()
        monkeypatch.setattr("learn.Learn.play", mock_play)
        monkeypatch.setattr("robot.speak", MagicMock())
        monkeypatch.setattr("draw.status_bar", MagicMock())

        lru.read_words()
        called_list = mock_play.call_args[0][0]
        assert len(called_list) == 1
        assert called_list[0]["ru"] == "дом"

    def test_read(self, monkeypatch):
        lru = learn.Learn(name="verbs all", file="dummy.json")
        mock_data = [{"ru": "быть", "en": "to be"}]
        monkeypatch.setattr("common.utils.get_json_file", lambda x: mock_data)

        mock_play = MagicMock()
        monkeypatch.setattr("learn.Learn.play", mock_play)
        monkeypatch.setattr("robot.speak", MagicMock())
        monkeypatch.setattr("draw.status_bar", MagicMock())

        lru.read()
        assert mock_play.called

    def test_read_pronouns_personal(self, monkeypatch):
        lru = learn.Learn(name="pronouns personal nominative", file="dummy.json")
        mock_data = [{"ru": "Я", "en": "I"}, {"ru": "Он,Она,Оно", "en": "he,she,it"}]
        monkeypatch.setattr("common.utils.get_json_file", lambda x: mock_data)
        monkeypatch.setattr("robot.speak", MagicMock())
        monkeypatch.setattr("draw.status_bar", MagicMock())

        lru.read_pronouns()
        assert True

    def test_read_pronouns_possessive(self, monkeypatch):
        lru = learn.Learn(name="pronouns possessive nominative", file="dummy.txt")
        mock_content = "мой,моя,моё\nтвой,твоя,твоё"
        monkeypatch.setattr("common.utils.get_data_file", lambda x: mock_content)
        monkeypatch.setattr("robot.speak", MagicMock())
        monkeypatch.setattr("draw.status_bar", MagicMock())

        lru.read_pronouns()
        assert True

    def test_play_navigation(self, monkeypatch):
        lru = learn.Learn(name="test", file="test.json")
        word_list = [{"ru": "word1", "en": "en1"}, {"ru": "word2", "en": "en2"}]

        commands = ["next", "prev", "repeat", "close"]

        def mock_recv_sequence():
            return commands.pop(0)

        class MockConn:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

            @staticmethod
            def recv():
                return mock_recv_sequence()

        class MockListener:
            def __init__(self, *args, **kwargs):
                pass

            @staticmethod
            def accept():
                return MockConn()

            def close(self):
                pass

            @staticmethod
            def fileno():
                return 0

        monkeypatch.setattr("learn.Listener", MockListener)
        monkeypatch.setattr("common.utils.wait_listener", lambda *args, **kwargs: True)
        monkeypatch.setattr("robot.speak", MagicMock())
        monkeypatch.setattr("draw.status_bar", MagicMock())

        lru.play(word_list)
        assert True

    def test__read_verb(self, monkeypatch):
        lru = learn.Learn(name="test", file="test.json")
        mock_data = [
            {"pronoun": "Я", "verb": "бегу"},
            {"pronoun": "Мы", "verb": "бежим"},
        ]
        monkeypatch.setattr("common.utils.get_json_file", lambda x: mock_data)
        monkeypatch.setattr("robot.speak", MagicMock())
        monkeypatch.setattr("draw.status_bar", MagicMock())

        lru._read_verb("бежать", Path("dummy.json"))
        assert True
