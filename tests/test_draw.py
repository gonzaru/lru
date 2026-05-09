from unittest.mock import patch
import draw
import settings


def test_status_bar():
    """Test that status_bar writes to the message file."""
    with patch("common.utils.write_data_file") as mock_write:
        with patch("common.utils.get_data_file", return_value="test message"):
            draw.status_bar("test message", show_msg=False)
            mock_write.assert_called_once_with(settings.MESSAGE_FILE, "w", "test message")
