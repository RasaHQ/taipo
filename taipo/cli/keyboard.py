import pathlib

import typer
import pandas as pd
import nlpaug.augmenter.char as nac
from sklearn.model_selection import train_test_split

from taipo.common import (
    nlu_path_to_dataframe,
    dataframe_to_nlu_file,
    entity_names,
    curly_entity_names,
)


app = typer.Typer(
    name="augment",
    add_completion=False,
    help="""Commands to simulate keyboard typos.""",
)


def add_spelling_errors(dataf, aug, text_col="text"):
    """Applies the keyboard typos to a column in the dataframe."""
    texts = list(dataf["text"])
    names = entity_names(texts) + curly_entity_names(texts)
    print(names)
    aug.stopwords = names
    return dataf.assign(**{text_col: lambda d: aug.augment(list(d[text_col]), n=1)})


@app.command()
def augment(
    file: pathlib.Path = typer.Argument(..., help="The original nlu.yml file"),
    out: pathlib.Path = typer.Argument(..., help="Path to write misspelled file to"),
    char_max: int = typer.Option(3, help="Max number of chars to change per line"),
    word_max: int = typer.Option(3, help="Max number of words to change per line"),
    lang: str = typer.Option("en", help="Language for keyboard layout"),
):
    """
    Applies typos to an NLU file and saves it to disk.
    """
    aug = nac.KeyboardAug(
        aug_char_min=1,
        aug_char_max=char_max,
        aug_char_p=0.3,
        aug_word_p=0.3,
        aug_word_min=1,
        aug_word_max=word_max,
        include_special_char=False,
        include_numeric=False,
        include_upper_case=False,
        lang=lang,
    )
    dataf = nlu_path_to_dataframe(file)
    (
        dataf.pipe(add_spelling_errors, aug=aug).pipe(
            dataframe_to_nlu_file, write_path=out, label_col="intent"
        )
    )


@app.command()
def generate(
    file: pathlib.Path = typer.Argument(..., help="The original nlu.yml file"),
    seed: int = typer.Option(42, help="The seed value to split the data"),
    test_size: int = typer.Option(33, help="Percentage of data to keep as test data"),
    prefix: str = typer.Option("misspelled", help="Prefix to add to all the files"),
    char_max: int = typer.Option(3, help="Max number of chars to change per line"),
    word_max: int = typer.Option(3, help="Max number of words to change per line"),
    lang: str = typer.Option("en", help="Language for keyboard layout"),
):
    """
    Generate train/validation data with/without misspelling.

    Will also generate files for the `/test` directory.
    """
    aug = nac.KeyboardAug(
        aug_char_min=1,
        aug_char_max=char_max,
        aug_char_p=0.3,
        aug_word_p=0.3,
        aug_word_min=1,
        aug_word_max=word_max,
        include_special_char=False,
        include_numeric=False,
        include_upper_case=False,
        lang=lang,
    )
    dataf = nlu_path_to_dataframe(file)

    X_train, X_test, y_train, y_test = train_test_split(
        dataf["text"], dataf["intent"], test_size=test_size / 100, random_state=seed
    )

    df_valid = pd.DataFrame({"text": X_test, "intent": y_test}).sort_values(["intent"])
    df_train = pd.DataFrame({"text": X_train, "intent": y_train}).sort_values(
        ["intent"]
    )

    (
        df_train.pipe(
            dataframe_to_nlu_file, write_path="data/nlu-train.yml", label_col="intent"
        )
    )

    (
        df_valid.pipe(
            dataframe_to_nlu_file, write_path="test/nlu-valid.yml", label_col="intent"
        )
    )

    (
        df_train.pipe(add_spelling_errors, aug=aug).pipe(
            dataframe_to_nlu_file,
            write_path=f"data/{prefix}-nlu-train.yml",
            label_col="intent",
        )
    )

    (
        df_valid.pipe(add_spelling_errors, aug=aug).pipe(
            dataframe_to_nlu_file,
            write_path=f"test/{prefix}-nlu-valid.yml",
            label_col="intent",
        )
    )
