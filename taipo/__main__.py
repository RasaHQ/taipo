import typer

from taipo.cli.spelling import app as spelling_app


app = typer.Typer(
    name="taipo",
    add_completion=False,
    help="""
    This app generates augmented datasets for Rasa nlu files. The hope is
    that such datasets can cause the models to train for robustness.
    """,
)

app.add_typer(spelling_app, name="spelling")

if __name__ == "__main__":
    app()
