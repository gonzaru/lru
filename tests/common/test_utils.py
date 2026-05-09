import json
import sys

import pytest

from common import utils


def test_is_laptop(tmpdir):
    fp = tmpdir.join("data.json")
    file = f"{fp.dirpath()}/data.json"
    with open(file, "w") as fp:
        fp.write("3")  # 3 Desktop
    assert not utils.is_laptop(file)
    with open(file, "w") as fp:
        fp.write("9")  # 9 Laptop
    assert utils.is_laptop(file)


def test_get_json_file(tmpdir):
    dictionary = {"t1": "test1"}
    json_object = json.dumps(dictionary, indent=4)
    fp = tmpdir.join("data.json")
    file = f"{fp.dirpath()}/data.json"
    with open(file, "w") as fp:
        fp.write(f"[{json_object}]")
    data = utils.get_json_file(file)
    assert data[0]["t1"] == "test1"


def test_get_json_file_malformed(tmpdir):
    fp = tmpdir.join("malformed.json")
    file = str(fp)
    with open(file, "w") as f:
        f.write('{"this is": not valid json}')
    data = utils.get_json_file(file)
    assert data == []


def test_write_data_file(tmpdir):
    data = "test data"
    fp = tmpdir.join("data.json")
    file = f"{fp.dirpath()}/data.json"
    try:
        utils.write_data_file(file, "w", data)
    except (FileNotFoundError, ValueError) as err:
        pytest.fail(str(err))
    else:
        assert True
    utils.write_data_file(file, "w", "")


def test_get_data_file(tmpdir):
    fp = tmpdir.join("data.json")
    fp.write("test data")
    file = f"{fp.dirpath()}/data.json"
    data = utils.get_data_file(file, "r")
    assert len(data) == 9


def test_check_python_version(monkeypatch):
    monkeypatch.setattr(sys, "version_info", (3, 6, 0))
    assert utils.check_python_version(3, 5, 0)
    assert utils.check_python_version(3, 6, 0)
    assert not utils.check_python_version(3, 7, 0)
