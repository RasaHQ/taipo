import os
import pathlib
import re

import pytest
from typer.testing import CliRunner

from taipo.__main__ import app
from taipo.common import nlu_path_to_dataframe

runner = CliRunner()


@pytest.mark.parametrize(
    "path_in,path_out", [("nlu.yml", "nlu-out.yml"), ("foobar.yml", "foobar-out.yml")]
)
def test_keyboard_augment(tmp_path: pathlib.Path, path_in: str, path_out: str):
    """Ensure basic usage of command works."""
    cmd = [
        "keyboard",
        "augment",
        "tests/data/nlu/nlu.yml",
        f"{tmp_path}/{path_out}",
    ]
    result = runner.invoke(app, cmd)
    assert result.exit_code == 0
    expected = nlu_path_to_dataframe("tests/data/nlu/nlu.yml").shape
    assert nlu_path_to_dataframe(f"{tmp_path}/{path_out}").shape == expected


def test_keyboard_augment_keeps_annotations(tmp_path: pathlib.Path):
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
    annotation_pattern = r"(\[\w+\]\(\w+\))|(\[\w+\]\{\w+\})"
    for text_in, text_out in zip(df_in.text, df_out.text):
        annotations_in = re.findall(annotation_pattern, text_in)
        annotations_out = re.findall(annotation_pattern, text_out)
        assert len(annotations_in) == len(annotations_out)


@pytest.mark.parametrize(
    "lang", ["de", "en", "es", "fr", "he", "it", "nl", "pl", "th", "uk"]
)
def test_keyboard_lang(tmp_path: pathlib.Path, lang: str):
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


def test_keyboard_generate(tmp_path: pathlib.Path):
    """Ensure basic usage of command works."""
    expected_output_files = [
        os.path.join(tmp_path, f)
        for f in [
            "data/nlu-train.yml",
            "data/typod-nlu-train.yml",
            "test/nlu-valid.yml",
            "test/typod-nlu-valid.yml",
        ]
    ]

    orig_nlu_file = "./tests/data/nlu/nlu.yml"

    cmd = [
        "keyboard",
        "generate",
        orig_nlu_file,
        "--prefix",
        "typod",
        "--out-path",
        tmp_path,
    ]
    res = runner.invoke(app, cmd)
    assert res.exit_code == 0
    for f in expected_output_files:
        assert pathlib.Path(f).exists()
