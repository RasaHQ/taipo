import pathlib

import typer
import pandas as pd
from transliterate import get_translit_function
from sklearn.model_selection import train_test_split

from taipo.common import nlu_path_to_dataframe, dataframe_to_nlu_file, entity_names


app = typer.Typer(
    name="augment",
    add_completion=False,
    help="""Commands to generate transliterations.""",
)


class Translitor:
    def __init__(self, lang, reversed, ents):
        self.translitor = get_translit_function(lang)
        self.mapper = {e: i for i, e in enumerate(ents)}
        self.reversed = reversed

    def hide_ents(self, s):
        for k, v in self.mapper.items():
            s = s.replace(k, str(v))
        return s

    def show_ents(self, s):
        for k, v in self.mapper.items():
            s = s.replace(str(v), k)
        return s

    def translit(self, s):
        return self.show_ents(
            self.translitor(self.hide_ents(s), reversed=self.reversed)
        )


def add_transliteration(dataf, lang, reversed, text_col="text"):
    """Applies the translitertion to a column in the dataframe."""
    ents = entity_names(list(dataf["text"]))
    tl = Translitor(lang=lang, reversed=reversed, ents=ents)
    return dataf.assign(**{text_col: lambda d: [tl.translit(e) for e in d["text"]]})


@app.command()
def augment(
    file: pathlib.Path = typer.Argument(..., help="The original nlu.yml file"),
    out: pathlib.Path = typer.Argument(..., help="Path to write misspelled file to"),
    target: str = typer.Option("latin", help="Alphabet to map to."),
    source: str = typer.Option("latin", help="Alphabet to map from."),
    lang: str = typer.Option("en", help="Language for keyboard layout"),
):
    """
    Applies translitertion to an NLU file and saves it to disk.
    """
    if target == source == "latin":
        typer.echo("Error! Either --target or --source needs to be set.")
        typer.Exit(1)
    lang = target if target != "latin" else source
    reversed = target == "latin"
    dataf = nlu_path_to_dataframe(file)
    (
        dataf.pipe(add_transliteration, lang=lang, reversed=reversed).pipe(
            dataframe_to_nlu_file, write_path=out, label_col="intent"
        )
    )


@app.command()
def generate(
    file: pathlib.Path = typer.Argument(..., help="The original nlu.yml file"),
    seed: int = typer.Option(42, help="The seed value to split the data"),
    test_size: int = typer.Option(33, help="Percentage of data to keep as test data"),
    prefix: str = typer.Option("translit", help="Prefix to add to all the files"),
    target: str = typer.Option("latin", help="Alphabet to map to."),
    source: str = typer.Option("latin", help="Alphabet to map from."),
    lang: str = typer.Option("en", help="Language for keyboard layout"),
):
    """
    Generate train/validation data with/without translitertion.

    Will also generate files for the `/test` directory.
    """
    lang = target if target != "latin" else source
    reversed = target == "latin"
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
        df_train.pipe(add_transliteration, lang=lang, reversed=reversed).pipe(
            dataframe_to_nlu_file,
            write_path=f"data/{prefix}-nlu-train.yml",
            label_col="intent",
        )
    )

    (
        df_valid.pipe(add_transliteration, lang=lang, reversed=reversed).pipe(
            dataframe_to_nlu_file,
            write_path=f"test/{prefix}-nlu-valid.yml",
            label_col="intent",
        )
    )
