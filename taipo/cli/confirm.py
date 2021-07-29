import os
import warnings


# Turn off annoying Tensorflow logs
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import typer
import pathlib
import numpy as np
import pandas as pd
import tensorflow as tf  # noqa
from rich.progress import Progress
from rich import print
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from rasa.cli.utils import get_validated_path
from rasa.core.interpreter import RasaNLUInterpreter
from rasa.model import get_model, get_model_subdirectories

from taipo.common import nlu_path_to_dataframe, replace_ent_assignment


app = typer.Typer(
    name="confirm",
    add_completion=False,
    help="""Confirm labels inside of nlu.yml files.""",
)


def load_interpreter(model_path):
    """Loads a Rasa interpreter."""
    path_str = str(model_path)
    model = get_validated_path(path_str, "model")
    model_path = get_model(model)
    _, nlu_model = get_model_subdirectories(model_path)
    return RasaNLUInterpreter(nlu_model)


@app.command()
def rasa_model(
    model_path: pathlib.Path = typer.Argument(..., help="Location of Rasa model."),
    nlu_path: pathlib.Path = typer.Argument(..., help="The original nlu.yml file"),
    out_path: pathlib.Path = typer.Argument(
        "checkthese.csv", help="Path to write examples file to"
    ),
):
    """Confirm via trained Rasa pipeline."""
    warnings.filterwarnings("ignore")

    # Load required components.
    print("[green]Loading Interpreter.")
    interpreter = load_interpreter(model_path)
    print("[green]Loading NLU file.")
    df = nlu_path_to_dataframe(nlu_path).assign(
        clean_text=lambda d: replace_ent_assignment(d["text"])
    )

    # Make predictions.
    parsed_examples = []
    with Progress() as progress:
        task = progress.add_task("[green]Making predictions...", total=df.shape[0])
        for text in df["clean_text"]:
            parsed_examples.append(interpreter.interpreter.parse(text)["intent"])
            progress.update(task, advance=1)
    pred_df = pd.DataFrame(parsed_examples)

    # Save the suggestions
    (
        df.assign(pred_intent=pred_df["name"], confidence=pred_df["confidence"])
        .loc[lambda d: d["intent"] != d["pred_intent"]]
        .sort_values("confidence", ascending=False)[
            ["text", "intent", "pred_intent", "confidence"]
        ]
        .to_csv(out_path, index=False)
    )
    print("[green]Done.")


@app.command()
def logistic(
    nlu_path: pathlib.Path = typer.Argument(..., help="The original nlu.yml file"),
    out_path: pathlib.Path = typer.Argument(
        "checkthese.csv", help="Path to write examples file to"
    ),
):
    """Confirm via basic sklearn pipeline."""
    df = nlu_path_to_dataframe(nlu_path).assign(
        clean_text=lambda d: replace_ent_assignment(d["text"])
    )

    print("[green]Training basic pipeline.")
    mod = make_pipeline(
        CountVectorizer(),
        LogisticRegression(solver="liblinear", class_weight="balanced"),
    )

    mod.fit(df["clean_text"], df["intent"])

    print("[green]Checking labels.")
    # Save the suggestions
    (
        df.assign(
            pred_intent=mod.predict(df["clean_text"]),
            confidence=np.max(mod.predict_proba(df["clean_text"]), axis=1),
        )
        .loc[lambda d: d["intent"] != d["pred_intent"]]
        .sort_values("confidence", ascending=False)[
            ["text", "intent", "pred_intent", "confidence"]
        ]
        .to_csv(out_path, index=False)
    )
    print("[green]Done.")
