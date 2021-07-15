import pathlib
from rich import console

import typer
import pandas as pd
from clumper import Clumper
from rich.table import Table
from rich.console import Console

from taipo.common import nlu_path_to_dataframe, dataframe_to_nlu_file


app = typer.Typer(
    name="util",
    add_completion=False,
    help="""Some utility commands.""",
)


@app.command()
def csv_to_yml(
    file: pathlib.Path = typer.Argument(..., help="The csv file to convert"),
    out: pathlib.Path = typer.Option(
        pathlib.Path("."), help="The path of the output file."
    ),
    text_col: str = typer.Option("text", help="Name of the text column."),
    label_col: str = typer.Option("intent", help="Name of the label column."),
):
    """
    Turns a .csv file into nlu.yml for Rasa
    """
    dataf = pd.read_csv(file)
    if out.is_dir():
        out = out / "nlu.yml"
    dataframe_to_nlu_file(dataf, write_path=out, label_col=label_col, text_col=text_col)


@app.command()
def yml_to_csv(
    file: pathlib.Path = typer.Argument(..., help="The csv file to convert"),
    out: pathlib.Path = typer.Option(
        pathlib.Path("."), help="The path of the output file."
    ),
):
    """
    Turns a nlu.yml file into .csv
    """
    if out.is_dir():
        out = out.absolute() / f"{file.stem}.csv"
    nlu_path_to_dataframe(file).to_csv(out, index=False)


@app.command()
def summary(
    folder: pathlib.Path = typer.Argument(
        ..., help="Folder that contains grid-result folders."
    ),
):
    """
    Displays summary tables for gridsearch results.
    """
    stringify = lambda d: str(round(d, 5))

    data = (
        Clumper.read_json(f"{folder}/*/intent_report.json", add_path=True)
        .select("read_path", "accuracy", "weighted avg")
        .mutate(
            folder=lambda d: pathlib.Path(d["read_path"]).parts[-2],
            precision=lambda d: stringify(d["weighted avg"]["precision"]),
            recall=lambda d: stringify(d["weighted avg"]["recall"]),
            f1=lambda d: stringify(d["weighted avg"]["f1-score"]),
        )
        .drop("read_path", "weighted avg")
        .sort(lambda d: -d["accuracy"])
        .mutate(accuracy=lambda d: stringify(d["accuracy"]))
        .collect()
    )

    table = Table()
    table.add_column("folder", style="cyan")
    table.add_column("accuracy")
    table.add_column("precision")
    table.add_column("recall")
    table.add_column("f1")
    for d in data:
        table.add_row(d["folder"], d["accuracy"], d["precision"], d["recall"], d["f1"])

    console = Console()
    console.print(table)
