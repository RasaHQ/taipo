import pathlib

import pandas as pd
import typer
from rasa.shared.nlu.constants import (
    TEXT,
    ENTITIES,
)
from transliterate import get_translit_function
from transliterate.utils import get_available_language_codes

from taipo import common

app = typer.Typer(
    name="augment",
    add_completion=False,
    help="""Commands to generate transliterations.""",
)


def apply_transliteration(
    nlu_df: pd.DataFrame,
    source: str,
    target: str,
    skip_entities: bool,
    text_col: str = TEXT,
    entity_col: str = ENTITIES,
) -> None:
    """Applies the transliteration to a column in the dataframe.

    Args:
        nlu_df: dataframe loaded via `common.nlu_path_to_dataframe`
        source: source code used in the texts contained in the `text_col` of `nlu_df`;
           either `source` or `target` have to be `l1`
        target: target code to be used; either `source` or `target` have to be `l1`
        skip_entities: If set to `True`, then the modification will only be
          applied separately to all substrings that do not contain a string that
          coincides with a string that has been annotated as an entity somewhere
          (i.e. even there is no annotation, the string will be ignored if an
          annotation appears in a different text)
        seed: used to seed the augmenter; modifies the global random seed!
        text_col: column in `nlu_df` containing texts; will be modified in-place
        entity_col: column in `entity_col` containing entity annotations; will be
          modified in-place
    """
    if "l1" not in [target, source]:
        raise ValueError("Either source or target need to be latin, i.e. `l1`.")
    reversed_ = target == "latin"
    lang = source if reversed_ else target
    translit_function = get_translit_function(lang)
    common.apply_modifier(
        modifier=lambda text: translit_function(text, reversed=reversed_),
        nlu_df=nlu_df,
        text_col=text_col,
        entity_col=entity_col,
        skip_entities=skip_entities,
    )


@app.command()
def augment(
    file: pathlib.Path = typer.Argument(..., help="The original nlu.yml file"),
    out: pathlib.Path = typer.Argument(..., help="Path to write misspelled file to"),
    target: str = typer.Option("l1", help="Alphabet to map to."),
    source: str = typer.Option("l1", help="Alphabet to map from."),
):
    """Applies translitertion to an NLU file and saves it to disk."""
    if target == source:
        typer.echo(
            "Error! Either --target or --source needs to be set. Cannot be the same."
        )
        raise typer.Exit(1)
    if "l1" not in [target, source]:
        typer.echo("Either target or source need to be latin.")
        raise typer.Exit(1)
    available_codes = get_available_language_codes()
    if source not in available_codes:
        typer.echo(f"Source code {source} not available. Found only {available_codes}.")
        raise typer.Exit(1)
    if target not in available_codes:
        typer.echo(f"Target code {source} not available. Found only {available_codes}.")
        raise typer.Exit(1)

    dataf = common.nlu_path_to_dataframe(file)
    apply_transliteration(dataf, source=source, target=target, skip_entities=True)
    common.dataframe_to_nlu_file(dataf, write_path=out)


@app.command()
def generate(
    file: pathlib.Path = typer.Argument(..., help="The original nlu.yml file"),
    seed: int = typer.Option(42, help="The seed value to split the data"),
    test_size: int = typer.Option(33, help="Percentage of data to keep as test data"),
    prefix: str = typer.Option("translit", help="Prefix to add to all the files"),
    target: str = typer.Option("l1", help="Alphabet to map to."),
    source: str = typer.Option("l1", help="Alphabet to map from."),
    out_path: pathlib.Path = typer.Option(
        "./",
        help="Directory where the data and test subdirectories will be created.",
    ),
):
    """
    Generate train/validation data with/without translitertion.

    Will also generate files for the `/test` directory.
    """
    if target == source:
        typer.echo(
            "Error! Either --target or --source needs to be set. Cannot be the same."
        )
        raise typer.Exit(1)

    dataf = common.nlu_path_to_dataframe(file)
    df_train, df_valid = common.split_uniformly(dataf, percentage=test_size, seed=seed)

    for df, sub_folder, suffix in [
        (df_train, "data", "train"),
        (df_valid, "test", "valid"),
    ]:
        split_path = out_path / sub_folder
        split_path.mkdir(parents=True)

        common.dataframe_to_nlu_file(df, write_path=split_path / f"nlu-{suffix}.yml")
        apply_transliteration(
            nlu_df=df, source=source, target=target, skip_entities=True
        )
        common.dataframe_to_nlu_file(
            df, write_path=split_path / f"{prefix}-nlu" f"-{suffix}.yml"
        )
