import pathlib

import typer

from taipo.cli.keyboard import app as keyboard_app
from taipo.cli.translit import app as translit_app
from taipo.cli.util import app as util_app
from taipo.cli.confirm import confirm as confirm_func


app = typer.Typer(
    name="taipo",
    add_completion=False,
    help="""
    This app contains tools for data quality in Rasa. It can generate
    augmented data but it can also check for bad labels. The hope is
    this tool contributes to data that leads to more robust models.
    """,
)

app.add_typer(keyboard_app, name="keyboard")
app.add_typer(translit_app, name="translit")
app.add_typer(util_app, name="util")


@app.command()
def confirm(
    nlu_path: pathlib.Path = typer.Argument(..., help="The nlu.yml file to check."),
    model_path: pathlib.Path = typer.Argument(..., help="The Rasa model to use."),
    out_path: pathlib.Path = typer.Argument(..., help="CSV output path."),
):
    """Confirms labels via a trained model."""
    confirm_func(nlu_path=nlu_path, model_path=model_path, out_path=out_path)


if __name__ == "__main__":
    app()
