import pathlib
import re

import pytest
from typer.testing import CliRunner

from taipo.__main__ import app
from taipo.common import nlu_path_to_dataframe

runner = CliRunner()


@pytest.mark.parametrize(
    "path_in,path_out", [("nlu.yml", "nlu.yml"), ("foobar.yml", "foobar.yml")]
)
def test_keyboard_augment(tmp_path, path_in, path_out):
    """Ensure basic usage of command works."""
    cmd = [
        "keyboard",
        "augment",
        "tests/data/nlu/nlu.yml",
        f"{tmp_path}/{path_in}",
    ]
    runner.invoke(app, cmd)
    expected = nlu_path_to_dataframe("tests/data/nlu/nlu.yml").shape
    assert nlu_path_to_dataframe(f"{tmp_path}/{path_out}").shape == expected


def test_keyboard_augment_keeps_annotations(tmp_path):
    """Ensure the format of entity annotations is kept correctly."""
    cmd = [
        "keyboard",
        "augment",
        "tests/data/nlu/nlu.yml",
        f"{tmp_path}/nlu.yml",
    ]
    runner.invoke(app, cmd)
    df_in = nlu_path_to_dataframe("tests/data/nlu/nlu.yml")
    df_out = nlu_path_to_dataframe(f"{tmp_path}/nlu.yml")
    annotation_pattern = r"\[\w+\]\(\w+\)"
    for text_in, text_out in zip(df_in.text, df_out.text):
        annotations_in = re.findall(annotation_pattern, text_in)
        annotations_out = re.findall(annotation_pattern, text_out)
        assert len(annotations_in) == len(annotations_out)


@pytest.mark.parametrize(
    "lang", ["de", "en", "es", "fr", "he", "it", "nl", "pl", "th", "uk"]
)
def test_keyboard_lang(tmp_path, lang):
    """
    Ensure that the languages listed in nlpaug indeed work.
    https://github.com/makcedward/nlpaug/tree/master/nlpaug/res/char/keyboard
    """
    cmd = [
        "keyboard",
        "augment",
        "tests/data/nlu/nlu.yml",
        f"{tmp_path}/nlu.yml",
        "--lang",
        lang,
    ]
    runner.invoke(app, cmd)
    expected = nlu_path_to_dataframe("tests/data/nlu/nlu.yml").shape
    assert nlu_path_to_dataframe(f"{tmp_path}/nlu.yml").shape == expected


def test_keyboard_generate():
    """Ensure basic usage of command works."""
    files = [
        "data/nlu-train.yml",
        "data/typod-nlu-train.yml",
        "test/nlu-valid.yml",
        "test/typod-nlu-valid.yml",
    ]
    for f in files:
        if pathlib.Path(f).exists():
            pathlib.Path(f).unlink()
    cmd = ["keyboard", "generate", "data/nlu-orig.yml", "--prefix", "typod"]
    res = runner.invoke(app, cmd)
    for f in files:
        assert pathlib.Path(f).exists()
        pathlib.Path(f).unlink()
    assert res.exit_code == 0
