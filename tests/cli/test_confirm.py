import asyncio
import textwrap
from pathlib import Path
from typing import Tuple

import pandas as pd
import pytest
import rasa.shared.utils.io as rasa_io_utils
from rasa import model_training
from rasa.shared.core.domain import Domain
from rasa.shared.nlu.constants import (
    INTENT,
    TEXT,
)
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData
from typer.testing import CliRunner

from taipo.__main__ import app

runner = CliRunner()


def _same_text_different_intents(out_dir: Path) -> Tuple[Path, Path]:
    """Creates 10 examples with 10 different intents but the same text."""
    intents = [f"different ({idx}th) intent label each time" for idx in range(10)]
    td = TrainingData(
        training_examples=[
            Message(
                data={
                    TEXT: "same text everywhere",
                    INTENT: intent,
                }
            )
            for intent in intents
        ]
    )
    data_path = out_dir / "nlu.yml"
    rasa_io_utils.write_text_file(td.nlu_as_yaml(), str(data_path))

    domain_path = out_dir / "domain.yml"
    Domain(
        intents=intents, entities=[], slots=[], responses={}, action_names=[], forms=[]
    ).persist(str(domain_path))

    return data_path, domain_path


@pytest.fixture(scope="module")
def _rasa_model_trained_on_same_text_different_intents(
    tmp_path_factory: pytest.TempPathFactory,
) -> Tuple[str, str]:
    tmp_dir = tmp_path_factory.mktemp("tmp")

    config = textwrap.dedent(
        """
        version: "2"
        pipeline:
        - name: WhitespaceTokenizer
        - name: CountVectorsFeaturizer
        - name: DIETClassifier
    """
    )  # Note: no LogisticRegressionClassifier in 2.8.x
    config_path = tmp_dir / "config.yml"
    rasa_io_utils.write_text_file(config, config_path)

    data_dir = tmp_dir / "data"
    data_dir.mkdir(parents=True)
    data_path, domain_path = _same_text_different_intents(out_dir=data_dir)

    output_path = str(tmp_path_factory.mktemp("models"))
    result = asyncio.run(
        model_training.train_async(
            config=config_path,
            training_files=[data_path],
            domain=domain_path,
            output=output_path,
        )
    )
    return result.model, str(data_path)


@pytest.mark.parametrize("out_file_provided", [True, False])
def test_confirm_logistic(tmp_path: Path, out_file_provided: bool):
    """Ensure basic usage of command works."""

    data_path, _ = _same_text_different_intents(out_dir=tmp_path)

    cmd = [
        "confirm",
        "logistic",
        str(data_path),
    ]
    if out_file_provided:
        out_file = tmp_path / "report.csv"
        cmd += [str(out_file)]
    else:
        out_file = "checkthese.csv"

    result = runner.invoke(app, cmd)
    assert result.exit_code == 0
    assert len(pd.read_csv(out_file)) == 9  # because one is classified "correctly"


@pytest.mark.parametrize("out_file_provided", [True, False])
def test_confirm_rasa_model(
    _rasa_model_trained_on_same_text_different_intents: Tuple[str, str],
    tmp_path: Path,
    out_file_provided: bool,
):
    """Ensure basic usage of command works."""

    model_path, data_path = _rasa_model_trained_on_same_text_different_intents

    cmd = [
        "confirm",
        "rasa-model",
        model_path,
        data_path,
    ]
    if out_file_provided:
        out_file = tmp_path / "report.csv"
        cmd += [str(out_file)]
    else:
        out_file = "checkthese.csv"

    result = runner.invoke(app, cmd)
    assert result.exit_code == 0
    assert len(pd.read_csv(out_file)) == 9  # because one is classified "correctly"
