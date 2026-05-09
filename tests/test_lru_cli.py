import lru_cli
from unittest.mock import patch


def test_lru_send_fail():
    assert lru_cli.lru_send("localhost", 9999, b"key", "msg") == 1


def test_cli_args_play():
    with patch("sys.argv", ["lru_cli", "play", "1"]):
        with patch("lru_cli.lru_send", return_value=0) as mock_send:
            assert lru_cli.main() == 0
            mock_send.assert_called_with(
                lru_cli.HOST_ADDR, lru_cli.HOST_PORT, lru_cli.HOST_AUTHKEY, "1"
            )


def test_cli_args_ctl():
    with patch("sys.argv", ["lru_cli", "ctl", "next"]):
        with patch("lru_cli.lru_send", return_value=0) as mock_send:
            assert lru_cli.main() == 0
            mock_send.assert_called_with(
                lru_cli.HOST_ADDR_CTL, lru_cli.HOST_PORT_CTL, lru_cli.HOST_AUTHKEY_CTL, "next"
            )
