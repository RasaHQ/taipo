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


@pytest.mark.parametrize(
    "path_in,path_out", [("nlu.yml", "nlu.yml"), ("foobar.yml", "foobar.yml")]
)
def test_keyboard_generate(tmp_path, path_in, path_out):
    """Ensure basic usage of command works."""
    cmd = [
        "keyboard",
        "augment",
        "tests/data/nlu/nlu.yml",
    ]
    result = runner.invoke(app, cmd)
    assert result.exit_code == 0
    assert nlu_path_to_dataframe(f"{tmp_path}/{path_out}").shape == expected
