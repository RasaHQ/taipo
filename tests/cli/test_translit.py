import os
import pathlib

import pytest
from typer.testing import CliRunner

from taipo.__main__ import app
from taipo.common import nlu_path_to_dataframe

runner = CliRunner()


@pytest.mark.parametrize(
    "path_in,path_out", [("nlu.yml", "nlu.yml"), ("foobar.yml", "foobar.yml")]
)
def test_translit_augment(tmp_path: pathlib.Path, path_in: str, path_out: str):
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
    ["ru", "mn", "sr", "bg", "ka", "uk", "el", "mk", "hy"],
)
def test_translit_lang(tmp_path: pathlib.Path, lang: str):
    """Ensure that the languages listed in nlpaug indeed work."""
    cmd = [
        "translit",
        "augment",
        "tests/data/nlu/nlu.yml",
        f"{tmp_path}/nlu.yml",
        "--source",
        "l1",
        "--target",
        lang,
    ]
    runner.invoke(app, cmd)
    expected = nlu_path_to_dataframe("tests/data/nlu/nlu.yml").shape
    assert nlu_path_to_dataframe(f"{tmp_path}/nlu.yml").shape == expected

    cmd = [
        "translit",
        "augment",
        f"{tmp_path}/nlu.yml",
        f"{tmp_path}/nlu2.yml",
        "--source",
        lang,
        "--target",
        "l1",
    ]
    runner.invoke(app, cmd)
    expected = nlu_path_to_dataframe(f"{tmp_path}/nlu.yml").shape
    assert nlu_path_to_dataframe(f"{tmp_path}/nlu2.yml").shape == expected


def test_translit_generate(tmp_path: str):
    """Ensure basic usage of command works."""
    files = [
        os.path.join(tmp_path, f)
        for f in [
            "data/nlu-train.yml",
            "data/translated-nlu-train.yml",
            "test/nlu-valid.yml",
            "test/translated-nlu-valid.yml",
        ]
    ]

    cmd = [
        "translit",
        "generate",
        "tests/data/nlu/nlu.yml",
        "--prefix",
        "translated",
        "--target",
        "el",
        "--out-path",
        tmp_path,
    ]
    res = runner.invoke(app, cmd)
    assert res.exit_code == 0
    for f in files:
        assert pathlib.Path(f).exists()


@pytest.mark.parametrize(
    "source,target,cmd",
    [
        ("l1", "l1", "augment"),
        ("el", "el", "augment"),
        ("l1", "l1", "generate"),
        ("el", "el", "generate"),
        ("unknown", "hy", "augment"),
        ("unknown", "hy", "generate"),
    ],
)
def test_invalid_lang_settings(source: str, target: str, cmd: str):
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
