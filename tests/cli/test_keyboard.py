import pathlib

import pytest
from typer.testing import CliRunner

from taipo.__main__ import app
from taipo.common import nlu_path_to_dataframe

runner = CliRunner()


@pytest.mark.parametrize(
    "path_in,path_out", [("nlu.yml", "nlu.yml"), ("foobar.yml", "foobar.yml")]
)
def test_keyboard(tmp_path, path_in, path_out):
    """Ensure basic usage of command works."""
    cmd = [
        "keyboard",
        "augment",
        "tests/data/nlu/nlu.yml",
        "--out",
        f"{tmp_path}/{path_in}",
    ]
    result = runner.invoke(app, cmd)
    expected = nlu_path_to_dataframe("tests/data/nlu/nlu.yml").shape
    print(f"{tmp_path}/{path_in}", f"{tmp_path}/{path_out}")
    assert result.exit_code == 0
    assert nlu_path_to_dataframe(f"{tmp_path}/{path_out}").shape == expected


def test_keyboard_generate():
    """Ensure basic usage of command works."""
    cmd = ["keyboard", "generate", "data/nlu-orig.yml", "--prefix", "typod"]
    result = runner.invoke(app, cmd)
    assert result.exit_code == 0
    assert pathlib.Path("data/nlu-train.yml").exists()
    assert pathlib.Path("data/typod-nlu-train.yml").exists()
    assert pathlib.Path("test/nlu-valid.yml").exists()
    assert pathlib.Path("test/typod-nlu-valid.yml").exists()
