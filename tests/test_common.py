import pytest
import pandas as pd

from taipo.common import nlu_path_to_dataframe, dataframe_to_nlu_file, entity_names


def test_yaml_both_ways(tmp_path):
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
