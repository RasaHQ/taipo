import pathlib

import typer
from nlpaug.augmenter.char import KeyboardAug

from taipo import common
from taipo.cli import keyboard


app = typer.Typer(
    name="augment",
    add_completion=False,
    help="""These commands augment a single file.""",
)


@app.command()
def augment(
    file: pathlib.Path = typer.Argument(..., help="The original nlu.yml file"),
    out: pathlib.Path = typer.Option(
        pathlib.Path("."), help="Folder to write misspelled file to"
    ),
    prefix: str = typer.Option("misspelled"),
):
    """
    Applies typos to an NLU file and saves it to disk.
    """
    nlp_df = common.nlu_path_to_dataframe(file)
    out_path = out / f"{prefix}-{file.parts[-1]}"
    common.apply_keyboard_augmenter(nlp_df=nlp_df, aug=aug)
    common.dataframe_to_nlu_file(nlp_df=nlp_df, write_path=out_path)


@app.command()
def generate(
    file: pathlib.Path = typer.Argument(..., help="The original nlu.yml file"),
    seed: int = typer.Option(42, help="The seed value to split the data."),
    test_size: int = typer.Option(33, help="Percentage of data to keep as test data."),
    prefix: str = typer.Option("misspelled"),
    seed_aug: int = typer.Option(None, help="The seed value to augment the data"),
    out_dir: pathlib.Path = typer.Argument(
        pathlib.Path("./"),
        help="Directory where the data and " "test subdirectories will be " "created.",
    ),
):
    """Generate train/validation data with/without misspelling.

    Will also generate files for the `/test` directory.
    """
    dataf = common.nlu_path_to_dataframe(file)
    df_train, df_valid = common.split_uniformly(dataf, percentage=test_size, seed=seed)

    aug = KeyboardAug(
        aug_char_max=10, aug_word_max=10, **keyboard.KEYBOARD_AUG_DEFAULTS
    )

    for df, folder, suffix in [
        (df_train, "data", "train"),
        (df_valid, "test", "valid"),
    ]:
        common.dataframe_to_nlu_file(
            df,
            write_path=out_dir / folder / f"nlu-{suffix}.yml",
        )

        keyboard.apply_keyboard_augmenter(
            df, aug=aug, skip_entities=False, seed=seed_aug
        )
        seed_aug += 1  # don't create same misspellings in test :)

        common.dataframe_to_nlu_file(
            df,
            write_path=out_dir / folder / f"{prefix}-nlu-{suffix}.yml",
        )
