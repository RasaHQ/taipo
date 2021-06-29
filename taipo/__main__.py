import typer

from taipo.cli.keyboard import app as keyboard_app
from taipo.cli.util import app as util_app


app = typer.Typer(
    name="taipo",
    add_completion=False,
    help="""
    This app generates augmented datasets for Rasa nlu files. The hope is
    that such datasets can cause the models to train for robustness.
    """,
)

app.add_typer(keyboard_app, name="keyboard")
app.add_typer(util_app, name="util")

if __name__ == "__main__":
    app()
