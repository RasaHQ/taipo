import asyncio
import copy
import re
from typing import List, Dict, Optional, Tuple, Set, Callable

import numpy as np
import pandas as pd
import rasa.shared.utils.io as rasa_io_utils
from rasa.shared.importers.importer import TrainingDataImporter
from rasa.shared.nlu.constants import (
    INTENT,
    ENTITIES,
    TEXT,
    ENTITY_ATTRIBUTE_START,
    ENTITY_ATTRIBUTE_END,
)
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData
from sklearn.model_selection import train_test_split


def split_uniformly(
    df: pd.DataFrame, percentage: int, seed: Optional[int]
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Splits the given nlu dataframe uniformly at random into train and test.

    Args:
        df: some dataframe
        percentage: percentage of given data used for test split (as an int)
        seed: used to seed the random number generator
    """
    indices = np.arange(len(df))
    train_indices, test_indices = train_test_split(
        indices, test_size=percentage / 100, random_state=seed
    )
    return df.iloc[train_indices].copy(), df.iloc[test_indices].copy()


def nlu_path_to_dataframe(path: str) -> pd.DataFrame:
    """Converts a single nlu file with intents into a dataframe.

    Args:
        path: path to nlu data
    Returns:
        dataframe with the loaded nlu data, containing columns for text, intent,
        and entities.
    """
    importer = TrainingDataImporter.load_from_dict(
        training_data_paths=[path], domain_path=None
    )
    nlu_data = asyncio.run(importer.get_nlu_data())

    df = pd.DataFrame(
        {
            TEXT: [message.get(TEXT) for message in nlu_data.nlu_examples],
            INTENT: [message.get(INTENT) for message in nlu_data.nlu_examples],
            ENTITIES: [message.get(ENTITIES, []) for message in nlu_data.nlu_examples],
        }
    )
    df = df[df[TEXT].apply(len) > 0].copy()  # drop empty texts
    return df


def dataframe_to_nlu_file(
    nlu_df: pd.DataFrame,
    write_path: str,
    text_col: str = TEXT,
    intent_col: Optional[str] = INTENT,
    entity_col: Optional[str] = ENTITIES,
) -> None:
    """Converts a single nlu dataframe into an nlu file for Rasa.

    Args:
        nlu_df: dataframe loaded via `nlu_path_to_dataframe`
        write_path: path where to store the resulting nlu file
        text_col: column in `nlu_df` containing just the text
        intent_col: (optional) column in `nlu_df` containing the intent annotation
        entity_col: (optional) column in `nlu_df` containing the entity annotation

    Usage:

    ```python
    import pandas as pd
    from taipo.common import dataframe_to_nlu_file
    df = pd.DataFrame([
        {"text": "i really really like this", "intent": "positive"},
        {"text": "i enjoy this", "intent": "positive"},
        {"text": "this is not my thing", "intent": "negative"}
    ])
    dataframe_to_nlu_file(df, write_path="path/to/nlu.yml")
    ```

    This will yield a file with the following contents:

    ```yaml
    version: 2.0
    nlu:
    - intent: negative
      examples: |
      - this is not my thing
    - intent: positive
      examples: |
      - i really really like this
      - i enjoy this
    ```
    """
    num_messages = len(nlu_df)
    intents = [""] * num_messages if intent_col is None else nlu_df[intent_col]
    entities = [[]] * num_messages if entity_col is None else nlu_df[entity_col]

    messages = [
        Message(data={TEXT: text, INTENT: intent, ENTITIES: entity_list})
        for text, intent, entity_list in zip(nlu_df[text_col], intents, entities)
    ]
    nlu_data = TrainingData(training_examples=messages)
    rasa_io_utils.write_text_file(nlu_data.nlu_as_yaml(), write_path)


def apply_modifier(
    modifier: Callable[[str], str],
    nlu_df: pd.DataFrame,
    text_col: str,
    entity_col: str,
    skip_entities: bool,
) -> None:
    """Applies the modification to all texts and aims to retain annotations.

    Applies the given text modifier separately to substrings of each message text.
    - If `skip_entities` is `True`, then we try to keep all appearances of entities
      intact: That is, the substrings that we modify independently are
      the substrings between strings that are either annotated as entities or
      substrings that coincide with strings that have been annotated as strings in
      any text.

    - If `skip_entities` is `False`, then we still try to keep annotations intact:
      Hence, the substrings that we modify independently include the substrings
      that are annotated as entities as well as these annotated substrings themselves.

    Args:
        modifier: function that maps a given text to some arbitrary text
        nlu_df: dataframe loaded via `common.nlu_path_to_dataframe`
        text_col: column in `nlu_df` containing texts
        entity_col: column in `entity_col` containing entity annotations
        skip_entities: If set to `True`, then the modification will only be
          applied separately to all substrings that do not contain a string that
          coincides with a string that has been annotated as an entity somewhere
          (i.e. even there is no annotation, the string will be ignored if an
          annotation appears in a different text)
    """
    if skip_entities:
        # Entities might be annotated only in a few examples, but we want to skip them
        # wherever they appear. Hence, we construct the following pattern:
        all_entity_strings = _collected_annotated_strings(
            nlu_df=nlu_df, text_col=text_col, entity_col=entity_col
        )
        entity_pattern: Optional[re.Pattern] = None
        if len(all_entity_strings):
            # Reminder: `|` is evaluated from left to right. Hence, we sort the entity
            # strings from longest to shortest to avoid problems with entity strings
            # that include other entity strings.
            entity_pattern = re.compile(
                "|".join(
                    f"(\b{re.escape(entity_str)}\b)"
                    for entity_str in sorted(
                        all_entity_strings, key=lambda s: len(s), reverse=True
                    )
                )
            )

    augmented_texts = [None for _ in range(len(nlu_df))]
    augmented_entities = [None for _ in range(len(nlu_df))]
    for idx, (text, entities) in enumerate(zip(nlu_df[text_col], nlu_df[entity_col])):

        # separate the annotated strings from the rest
        text_snippets, annotated_strings = _extract(
            text=str(text),
            index_tuples=[
                (entity[ENTITY_ATTRIBUTE_START], entity[ENTITY_ATTRIBUTE_END])
                for entity in entities
            ],
        )

        if skip_entities:

            # hide all appearances of substrings that have been annotated as
            # entity somewhere
            modified_text_snippets = []
            for snippet in text_snippets:

                if entity_pattern:
                    entity_like_locations = [
                        (match.start(), match.end())
                        for match in re.finditer(entity_pattern, snippet)
                    ]
                else:
                    entity_like_locations = []

                sub_snippets, entity_like_strings = _extract(
                    text=snippet, index_tuples=entity_like_locations
                )
                modified_sub_snippets = [modifier(snippet) for snippet in sub_snippets]

                modified_snippet = _join_with_strings(
                    split_text=modified_sub_snippets,
                    insertion_strings=entity_like_strings,
                )

                modified_text_snippets.append(modified_snippet)

        else:  # do not skip entities

            modified_text_snippets = [modifier(snippet) for snippet in text_snippets]
            # modify the annotated strings!
            annotated_strings = [modifier(snippet) for snippet in annotated_strings]

        augmented_text, augmented_entity = _join_with_entity_annotations(
            split_text=modified_text_snippets,
            entities=entities,
            entity_strings=annotated_strings,
        )

        augmented_texts[idx] = augmented_text
        augmented_entities[idx] = augmented_entity

    nlu_df[text_col] = augmented_texts
    nlu_df[entity_col] = augmented_entities


def _collected_annotated_strings(
    nlu_df: pd.DataFrame,
    text_col: str,
    entity_col: str,
) -> Set[str]:
    return set(
        text[entity[ENTITY_ATTRIBUTE_START] : entity[ENTITY_ATTRIBUTE_END]]
        for text, entity_list in zip(nlu_df[text_col], nlu_df[entity_col])
        for entity in entity_list
    )


def _extract(
    text: str, index_tuples: List[Tuple[int, int]]
) -> Tuple[List[str], List[str]]:
    remaining_text = text
    extracted = []
    text_snippets = []
    # Note: assumes ranges given by tuples don't overlap
    for start, end in sorted(index_tuples, reverse=True):
        text_snippets.append(remaining_text[end:])
        extracted.append(remaining_text[start:end])
        remaining_text = remaining_text[:start]
    text_snippets.append(remaining_text)
    return list(reversed(text_snippets)), list(reversed(extracted))


def _join_with_strings(split_text: List[str], insertion_strings: List[str]) -> str:
    full_list = [None for _ in range(len(split_text) + len(insertion_strings))]
    full_list[::2] = split_text
    full_list[1::2] = insertion_strings
    return "".join(full_list)


def _join_with_entity_annotations(
    split_text: str,
    entities: List[Dict[str, int]],
    entity_strings: List[str],
) -> Tuple[str, List[Dict[str, int]]]:

    if len(split_text) - 1 != len(entities):
        raise ValueError(
            f"Number of possible insertion points ({len(split_text) - 1}) does not "
            f"match the number of given entities ({len(entities)})."
        )

    if len(entity_strings) != len(entities):
        raise ValueError(
            f"Number of entity strings ({len(entity_strings)}) does not "
            f"match the number of given entities ({len(entities)})."
        )

    full_list = [None] * (len(split_text) + len(entities))
    split_idx = 0
    entity_idx = 0
    running_length = 0
    new_entities = []
    for idx in range(len(full_list)):
        if idx % 2 == 0:
            full_list[idx] = split_text[split_idx]
            split_idx += 1
        else:
            full_list[idx] = entity_strings[entity_idx]
            # adapt indices of inserted entity to be sure (in case the
            # augmentation does not just substitute but add noise)
            entity = copy.copy(entities[entity_idx])
            entity[ENTITY_ATTRIBUTE_START] = running_length
            entity[ENTITY_ATTRIBUTE_END] = running_length + len(full_list[idx])
            new_entities.append(entity)
            entity_idx += 1
        running_length += len(full_list[idx])

    return "".join(full_list), new_entities
