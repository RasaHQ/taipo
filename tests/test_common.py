import copy
import re
from typing import List, Dict, Any, Tuple

import pandas as pd
import pytest
from rasa.shared.nlu.constants import (
    ENTITY_ATTRIBUTE_VALUE,
    ENTITY_ATTRIBUTE_START,
    ENTITY_ATTRIBUTE_END,
)

from taipo import common


def test_yaml_both_ways(tmp_path: str):
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
    common.dataframe_to_nlu_file(nlu_df=df, entity_col=None, write_path=path)
    df_read = common.nlu_path_to_dataframe(path)
    assert len(df_read) == 3


def test_nlu_path_to_dataframe():
    """
    Test that nlu_path_to_dataframe works with no errors.
    """
    df_read = common.nlu_path_to_dataframe("tests/data/nlu/nlu.yml")
    assert len(df_read) == 9


def test_split_uniformly():
    """
    Test that nlu_path_to_dataframe works with no errors.
    """
    df_read = common.nlu_path_to_dataframe("tests/data/nlu/nlu.yml")
    df_train, df_test = common.split_uniformly(df_read, percentage=1 / 9, seed=234)
    assert len(df_test) == 1
    assert len(df_train) == 8


@pytest.mark.parametrize(
    "text, index_tuples, expected_split, expected_extracted",
    [
        ("aba", [(0, 1), (2, 3)], ["", "b", ""], ["a", "a"]),
        ("a", [(0, 1)], ["", ""], ["a"]),
        ("a", [], ["a"], []),
    ],
)
def test_extract(
    text: str,
    index_tuples: List[Tuple[int, int]],
    expected_split: List[str],
    expected_extracted: List[str],
):
    split, extracted = common._extract(text=text, index_tuples=index_tuples)
    assert split == expected_split
    assert extracted == expected_extracted


@pytest.mark.parametrize(
    "split_text, insertion_strings, expected",
    [
        (["", ""], ["a"], "a"),
        (["b", "b"], ["a"], "bab"),
        (["b", "b", ""], ["a", "a"], "baba"),
    ],
)
def test_join_with_strings(
    split_text: List[str], insertion_strings: List[str], expected: str
):
    output = common._join_with_strings(
        split_text=split_text, insertion_strings=insertion_strings
    )
    assert output == expected


@pytest.mark.parametrize(
    "split_text, entity_strings, text",
    [
        (["", ""], ["a"], "a"),
        (["b", "b"], ["a"], "bab"),
        (["b", "b", ""], ["a", "a"], "baba"),
    ],
)
def test_join_with_entities(
    split_text: List[str], entity_strings: List[str], text: str
):

    entities = [
        {ENTITY_ATTRIBUTE_START: match.start(), ENTITY_ATTRIBUTE_END: match.end()}
        for match in re.finditer("a", text)
    ]

    split_text_modified = [("cc" if snippet else "") for snippet in split_text]
    output_text, modified_entities = common._join_with_entity_annotations(
        split_text=split_text_modified, entities=entities, entity_strings=entity_strings
    )
    expected_output_text = text.replace("b", "cc")
    assert output_text == expected_output_text

    expected_entities = [
        {ENTITY_ATTRIBUTE_START: match.start(), ENTITY_ATTRIBUTE_END: match.end()}
        for match in re.finditer("a", expected_output_text)
    ]
    assert expected_entities == modified_entities


def _generate_test_cases() -> Tuple[List[str], List[Dict[str, Any]], List[str], str]:
    test_cases = []

    # no entity
    full_text = "no entities here"
    test_cases.append(([full_text], [], [], full_text))

    # just one entity
    text_split = ["", ""]
    entity_strings = ["EEEE"]
    full_text = "EEEE"
    entities = [
        {
            ENTITY_ATTRIBUTE_START: 0,
            ENTITY_ATTRIBUTE_END: len(full_text),
            ENTITY_ATTRIBUTE_VALUE: "this could be anything",
        }
    ]
    test_cases.append((text_split, entities, entity_strings, full_text))

    # three entities
    text_split = ["", "and", "or", ""]
    entity_strings = ["EEEE", "EE", "EEEEE"]
    full_text = "EEEE and EE or EEEEE"
    entities = [
        {
            ENTITY_ATTRIBUTE_START: start,
            ENTITY_ATTRIBUTE_END: end,
            ENTITY_ATTRIBUTE_VALUE: "this could be anything",
        }
        for start, end in [(0, 4), (9, 11), (14, len(full_text))]
    ]
    test_cases.append((text_split, entities, entity_strings, full_text))

    # three entities -- but only one of them annotated
    text_split = ["", "and", "or", ""]
    entity_strings = ["EEEE", "EEEE", "EEEE"]
    full_text = "EEEE and EEEE or EEEE"
    entities = [
        {
            ENTITY_ATTRIBUTE_START: start,
            ENTITY_ATTRIBUTE_END: end,
            ENTITY_ATTRIBUTE_VALUE: "this could be anything",
        }
        for start, end in [(0, 4)]
    ]
    test_cases.append((text_split, entities, entity_strings, full_text))

    # three entities -- but only two of them annotated PLUS entities overlap
    text_split = ["", "n", "n", ""]
    entity_strings = ["E", "E EE", "E EE"]
    full_text = "E n E EE n E EE"
    entities = [
        {
            ENTITY_ATTRIBUTE_START: start,
            ENTITY_ATTRIBUTE_END: end,
            ENTITY_ATTRIBUTE_VALUE: "this could be anything",
        }
        for start, end in [(0, 1), (4, 8)]
    ]
    test_cases.append((text_split, entities, entity_strings, full_text))

    return test_cases


@pytest.mark.parametrize(
    "test_case, skip_entities",
    [
        (test_case, skip_entities)
        for test_case in _generate_test_cases()
        for skip_entities in [True, False]
    ],
)
def test_test_cases_for_apply_modifier(
    test_case: Tuple[List[str], List[Dict[str, Any]], List[str], str],
    skip_entities: bool,
):
    text_split, entities, entity_strings, full_text = test_case
    original_entities = [copy.copy(entity) for entity in entities]

    nlu_df = pd.DataFrame(
        [{"mytext": full_text, "myintent": "bla", "myentity": entities}]
    )

    modifier = lambda x: x.swapcase() + x.swapcase()

    common.apply_modifier(
        modifier=modifier,
        nlu_df=nlu_df,
        skip_entities=skip_entities,
        entity_col="myentity",
        text_col="mytext",
    )

    augmented_text = nlu_df.iloc[0]["mytext"]

    # Check text change -- if there was something to change
    if not skip_entities or "".join(text_split):
        # Note: we fixed the seed, so the augmenter should always succeed
        assert augmented_text != full_text

    # Check entities
    augmented_entities = nlu_df.iloc[0]["myentity"]
    for original_entity, augmented_entity in zip(original_entities, augmented_entities):
        original_entity_string = full_text[
            original_entity[ENTITY_ATTRIBUTE_START] : original_entity[
                ENTITY_ATTRIBUTE_END
            ]
        ]

        augmented_entity_string = augmented_text[
            augmented_entity[ENTITY_ATTRIBUTE_START] : augmented_entity[
                ENTITY_ATTRIBUTE_END
            ]
        ]

        if skip_entities:

            assert original_entity_string == augmented_entity_string

            assert len(
                list(re.finditer(f"\b{original_entity}\b", augmented_text))
            ) == len(list(re.finditer(f"\b{original_entity}\b", augmented_text)))

        else:

            expected_entity_string = modifier(original_entity_string)
            assert expected_entity_string == augmented_entity_string

            assert len(
                list(re.finditer(f"\b{original_entity_string}\b", full_text))
            ) == len(
                list(
                    re.finditer(
                        f"\b{expected_entity_string}\b",
                        augmented_text,
                    )
                )
            )
