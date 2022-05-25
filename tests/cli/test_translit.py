import pathlib
import itertools as it

import pandas as pd
import pytest
from rasa.shared.nlu.constants import ENTITY_ATTRIBUTE_START, ENTITY_ATTRIBUTE_END
from typer.testing import CliRunner
from transliterate.utils import get_available_language_codes

from taipo.__main__ import app
from taipo.common import nlu_path_to_dataframe

runner = CliRunner()


@pytest.mark.parametrize(
    "path_in,path_out", [("nlu.yml", "nlu.yml"), ("foobar.yml", "foobar.yml")]
)
def test_translit_augment(tmp_path, path_in, path_out):
    """Ensure basic usage of command works."""
    cmd = [
        "translit",
        "augment",
        "tests/data/nlu/nlu.yml",
        f"{tmp_path}/{path_in}",
        "--target",
        "el",
    ]
    runner.invoke(app, cmd)
    expected = nlu_path_to_dataframe("tests/data/nlu/nlu.yml").shape
    assert nlu_path_to_dataframe(f"{tmp_path}/{path_out}").shape == expected


@pytest.mark.parametrize(
    "lang",
    ["ru", "mn", "sr", "bg", "ka", "uk", "el", "mk", "l1", "hy"],
)
def test_translit_lang(tmp_path: str, lang: str):
    """Ensure that the languages listed in nlpaug indeed work."""
    cmd = [
        "translit",
        "augment",
        "tests/data/nlu/nlu.yml",
        f"{tmp_path}/nlu.yml",
        "--target",
        lang,
    ]
    runner.invoke(app, cmd)
    expected = nlu_path_to_dataframe("tests/data/nlu/nlu.yml").shape
    assert nlu_path_to_dataframe(f"{tmp_path}/nlu.yml").shape == expected


def test_translit_generate():
    """Ensure basic usage of command works."""
    files = [
        "data/nlu-train.yml",
        "data/translated-nlu-train.yml",
        "test/nlu-valid.yml",
        "test/translated-nlu-valid.yml",
    ]
    for f in files:
        if pathlib.Path(f).exists():
            pathlib.Path(f).unlink()
    cmd = [
        "translit",
        "generate",
        "data/nlu-orig.yml",
        "--prefix",
        "translated",
        "--target",
        "el",
    ]
    res = runner.invoke(app, cmd)
    for f in files:
        assert pathlib.Path(f).exists()
        pathlib.Path(f).unlink()
    assert res.exit_code == 0


@pytest.mark.parametrize(
    "source,target,cmd",
    [
        ("latin", "latin", "augment"),
        ("el", "el", "augment"),
        ("latin", "latin", "generate"),
        ("el", "el", "generate"),
    ],
)
def test_invalid_lang_settings(source, target, cmd):
    """Gotta make sure we exit."""
    cmd = [
        "translit",
        cmd,
        "data/nlu-orig.yml",
        "--prefix",
        "translated",
        "--source",
        source,
        "--target",
        target,
    ]
    res = runner.invoke(app, cmd)
    assert res.exit_code != 0
