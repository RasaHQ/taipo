import pathlib

import typer
import pandas as pd

from taipo.common import nlu_path_to_dataframe, dataframe_to_nlu_file


app = typer.Typer(
    name="util",
    add_completion=False,
    help="""Some utility commands.""",
)

@app.command()
def csv_to_yml(file: pathlib.Path = typer.Argument(..., help="The csv file to convert"), 
               out: pathlib.Path = typer.Option(pathlib.Path("."), help="The path of the output file."),
               text_col: str = typer.Option("text", help="Name of the text column."),
               label_col: str = typer.Option("label", help="Name of the label column.")):
    """
    Turns a .csv file into nlu.yml for Rasa
    """
    dataf = pd.read_csv(file)
    if out.is_dir():
        out = out / "nlu.yml"
    dataframe_to_nlu_file(dataf, write_path=out, label_col=label_col, text_col=text_col)


@app.command()
def yml_to_csv(file: pathlib.Path = typer.Argument(..., help="The csv file to convert"), 
               out: pathlib.Path = typer.Option(pathlib.Path("."), help="The path of the output file.")):
    """
    Turns a nlu.yml file into .csv
    """
    if out.is_dir():
        out = out.absolute() / f"{file.stem}.csv"
    nlu_path_to_dataframe(file).to_csv(out, index=False)
