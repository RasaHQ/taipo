import pytest
import pandas as pd

from taipo.common import (
    nlu_path_to_dataframe,
    dataframe_to_nlu_file,
    entity_names,
    replace_ent_assignment,
)


def test_yaml_both_ways(tmp_path):
    """
    Generate a dataframe, save it as yml and read it back again.
    """
    df = pd.DataFrame(
        [
            {"text": "i really really like this", "intent": "positive"},
            {"text": "i enjoy this", "intent": "positive"},
            {"text": "this is not my thing", "intent": "negative"},
        ]
    )
    path = f"{tmp_path}/temp_nlu.yml"
    dataframe_to_nlu_file(df, write_path=path)
    df_read = nlu_path_to_dataframe(path)
    assert len(df_read) == 3


def test_nlu_path_to_dataframe():
    """
    Test that nlu_path_to_dataframe works with no errors.
    """
    df_read = nlu_path_to_dataframe("tests/data/nlu/nlu.yml")
    assert len(df_read) == 8


@pytest.mark.parametrize(
    "going_in, going_out",
    [
        ("[python](proglang)", ["proglang"]),
        ("[python](proglang) and [r](proglang)", ["proglang"]),
        ("[python](proglang) and [pandas](package)", ["proglang", "package"]),
        ("there be no entities", []),
    ],
)
def test_entity_names(going_in, going_out):
    assert entity_names([going_in]) == going_out


@pytest.mark.parametrize(
    "going_in, going_out",
    [
        ("[python](proglang)", "python"),
        ("[python](proglang) and [r](proglang)", "python and r"),
        ("[python](proglang) and [pandas](package)", "python and pandas"),
        ("there be no entities", "there be no entities"),
        (
            "[python](proglang) and [r](proglang) and [pandas](package)",
            "python and r and pandas",
        ),
        (
            "[python](proglang) and [r](proglang) and [pandas](package) and [numpy](package)",
            "python and r and pandas and numpy",
        ),
        (
            "[python](proglang) and [r](proglang) and [pandas](package) and [numpy](package) and [jupyter](package)",
            "python and r and pandas and numpy and jupyter",
        ),
        (
            "[python](proglang) and [r](proglang) and [pandas](package) and [numpy](package) and [scipy](package)",
            "python and r and pandas and numpy and scipy",
        ),
        (
            "[python](proglang) and [r](proglang) and [pandas](package) and [numpy](package) and [scipy](package) and [jupyter](package)",
            "python and r and pandas and numpy and scipy and jupyter",
        ),
        (
            "[python](proglang) and [r](proglang) and [pandas](package) and [numpy](package) and [scipy](package) and [jupyter](package) and [matplotlib](package)",
            "python and r and pandas and numpy and scipy and jupyter and matplotlib",
        ),
        (
            "[python](proglang) and [r](proglang) and [pandas](package) and [numpy](package) and [scipy](package) and [jupyter](package) and [matplotlib](package) and [jupyter_contrib](package)",
            "python and r and pandas and numpy and scipy and jupyter and matplotlib and jupyter_contrib",
        ),
        (
            "[python](proglang) and [r](proglang) and [pandas](package) and [numpy](package) and [scipy](package) and [jupyter](package) and [matplotlib](package) and [jupyter_contrib](package) and [ipython](package)",
            "python and r and pandas and numpy and scipy and jupyter and matplotlib and jupyter_contrib and ipython",
        ),
    ],
)
def test_replace_ent_assignment(going_in, going_out):
    """
    Parts of this test were written with Github 's copilot tool.
    Anybody care to guess which examples were written by the maintainer?
    """
    assert replace_ent_assignment([going_in]) == [going_out]
