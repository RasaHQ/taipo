from pathlib import Path

from py._path.local import LocalPath
from typer.testing import CliRunner
import pandas as pd
from taipo.__main__ import app
from taipo.common import nlu_path_to_dataframe

runner = CliRunner()


def test_csv_yml(tmp_path: Path):
    """Ensure basic usage of command works."""
    cmd = [
        "util",
        "csv-to-yml",
        "tests/data/nlu/nlu.csv",
        "--out",
        f"{tmp_path}/nlu.yml",
    ]
    runner.invoke(app, cmd)
    assert (
        nlu_path_to_dataframe("tests/data/nlu/nlu.yml").shape[0]
        == nlu_path_to_dataframe(f"{tmp_path}/nlu.yml").shape[0]
    )


def test_csv_yml_just_path(tmp_path: Path):
    """Ensure command works when only a path is passed."""
    cmd = ["util", "csv-to-yml", "tests/data/nlu/nlu.csv", "--out", f"{tmp_path}"]
    runner.invoke(app, cmd)
    assert (
        nlu_path_to_dataframe("tests/data/nlu/nlu.yml").shape[0]
        == nlu_path_to_dataframe(f"{tmp_path}/nlu.yml").shape[0]
    )


def test_csv_yml_no_path():
    """Ensure command works when only a path is passed."""
    # FIXME: this should not actually write to the repositories root dir (tempdir
    #  fixture as cwd does not work)
    cmd = ["util", "csv-to-yml", "tests/data/nlu/nlu.csv"]
    runner.invoke(app, cmd)
    assert (
        nlu_path_to_dataframe("tests/data/nlu/nlu.yml").shape[0]
        == nlu_path_to_dataframe(f"nlu.yml").shape[0]
    )


def test_yml_csv(tmp_path: Path):
    """Ensure basic usage of command works."""
    cmd = [
        "util",
        "yml-to-csv",
        "tests/data/nlu/nlu.yml",
        "--out",
        f"{tmp_path}/foobar.csv",
    ]
    runner.invoke(app, cmd)
    assert (
        pd.read_csv(f"{tmp_path}/foobar.csv", sep="|").shape[0]
        == pd.read_csv(f"tests/data/nlu/nlu.csv", sep="|").shape[0]
    )


def test_yml_csv_just_path(tmp_path: Path):
    """Ensure command works when only a path is passed."""
    cmd = ["util", "yml-to-csv", "tests/data/nlu/nlu.yml", "--out", f"{tmp_path}"]
    runner.invoke(app, cmd)
    assert (
        pd.read_csv(f"{tmp_path}/nlu.csv", sep="|").shape[0]
        == pd.read_csv(f"tests/data/nlu/nlu.csv", sep="|").shape[0]
    )


def test_yml_csv_no_path():
    """Ensure command works when no path is passed."""
    # FIXME: this should not actually write to the repositories root dir (tempdir
    #  fixture as cwd does not work)
    cmd = ["util", "yml-to-csv", "tests/data/nlu/nlu.yml"]
    runner.invoke(app, cmd)
    assert (
        pd.read_csv(f"nlu.csv", sep="|").shape[0]
        == pd.read_csv(f"tests/data/nlu/nlu.csv", sep="|").shape[0]
    )
