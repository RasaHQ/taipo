import pathlib
import random
from typing import Optional

import pandas as pd
import typer
from nlpaug.augmenter.char import KeyboardAug
from rasa.shared.nlu.constants import ENTITIES, TEXT

from taipo import common

KEYBOARD_AUG_DEFAULTS = dict(
    aug_char_min=1,
    aug_char_p=0.3,
    aug_word_p=0.3,
    aug_word_min=1,
    include_special_char=False,
    include_numeric=False,
    include_upper_case=False,
)

app = typer.Typer(
    name="augment",
    add_completion=False,
    help="""Commands to simulate keyboard typos.""",
)


def apply_keyboard_augmenter(
    nlu_df: pd.DataFrame,
    aug: KeyboardAug,
    skip_entities: bool,
    seed: Optional[int] = None,
    text_col: str = TEXT,
    entity_col: str = ENTITIES,
) -> None:
    """Applies keyboard augmenter from `https://github.com/makcedward/nlpaug`.

    Note: The given seed will be used to **modify the global random seed** because
      augmenter lib does not use proper rngs.

    Args:
        nlu_df: dataframe loaded via `common.nlu_path_to_dataframe`
        aug: keyboard augmenter
        skip_entities: If set to `True`, then the modification will only be
          applied separately to all substrings that do not contain a string that
          coincides with a string that has been annotated as an entity somewhere
          (i.e. even there is no annotation, the string will be ignored if an
          annotation appears in a different text)
        seed: used to seed the augmenter; **modifies the global random seed!**
        text_col: column in `nlu_df` containing texts; will be modified in-place
        entity_col: column in `entity_col` containing entity annotations; will be
          modified in-place
    """
    random.seed(seed)
    return common.apply_modifier(
        modifier=lambda text: aug.augment(text, n=1),
        nlu_df=nlu_df,
        text_col=text_col,
        entity_col=entity_col,
        skip_entities=skip_entities,
    )


@app.command()
def augment(
    file: pathlib.Path = typer.Argument(..., help="The original nlu.yml file"),
    out: pathlib.Path = typer.Argument(..., help="Path to write misspelled file to"),
    char_max: int = typer.Option(3, help="Max number of chars to change per line"),
    word_max: int = typer.Option(3, help="Max number of words to change per line"),
    lang: str = typer.Option("en", help="Language for keyboard layout"),
    seed_aug: int = typer.Option(None, help="The seed value to augment the data"),
):
    """Applies typos to an NLU file and saves it to disk.

    For each given (non-empty) nlu example in the given nlu data, the output will
    contain exactly one corresponding example, which contains typos. Hence, this
    method does *not* add examples to the given nlu data (but replace all examples).
    """
    dataf = common.nlu_path_to_dataframe(file)
    aug = KeyboardAug(
        aug_char_max=char_max,
        aug_word_max=word_max,
        lang=lang,
        **KEYBOARD_AUG_DEFAULTS,
    )
    apply_keyboard_augmenter(nlu_df=dataf, aug=aug, skip_entities=True, seed=seed_aug)
    common.dataframe_to_nlu_file(nlu_df=dataf, write_path=out)


@app.command()
def generate(
    file: pathlib.Path = typer.Argument(..., help="The original nlu.yml file"),
    seed_split: int = typer.Option(42, help="The seed value to split the data"),
    seed_aug: int = typer.Option(None, help="The seed value to augment the data"),
    test_size: int = typer.Option(33, help="Percentage of data to keep as test data"),
    prefix: str = typer.Option("misspelled", help="Prefix to add to all the files"),
    char_max: int = typer.Option(3, help="Max number of chars to change per line"),
    word_max: int = typer.Option(3, help="Max number of words to change per line"),
    lang: str = typer.Option("en", help="Language for keyboard layout"),
    out_path: pathlib.Path = typer.Option(
        "./",
        help="Directory where the data and test subdirectories will be created.",
    ),
):
    """Generate train/validation data with/without misspelling.

    Will also generate files for the `/test` directory.
    """
    aug = KeyboardAug(
        aug_char_max=char_max,
        aug_word_max=word_max,
        lang=lang,
        **KEYBOARD_AUG_DEFAULTS,
    )
    dataf = common.nlu_path_to_dataframe(file)
    df_train, df_valid = common.split_uniformly(
        dataf,
        percentage=test_size,
        seed=seed_split,
    )
    # out_path = pathlib.Path(out_dir)

    for df, sub_folder, suffix in [
        (df_train, "data", "train"),
        (df_valid, "test", "valid"),
    ]:

        split_path = out_path / sub_folder
        split_path.mkdir(parents=True)

        common.dataframe_to_nlu_file(
            df_train,
            write_path=split_path / f"nlu-{suffix}.yml",
        )
        apply_keyboard_augmenter(df_train, aug=aug, skip_entities=True, seed=seed_aug)
        if seed_aug is not None:
            seed_aug += 1  # don't create same misspellings in test :)

        common.dataframe_to_nlu_file(
            df_train,
            write_path=split_path / f"{prefix}-nlu-{suffix}.yml",
        )
