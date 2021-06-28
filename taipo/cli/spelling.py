import pathlib

import typer
import pandas as pd
import nlpaug.augmenter.char as nac
from sklearn.model_selection import train_test_split

from taipo.common import nlu_path_to_dataframe, dataframe_to_nlu_file


app = typer.Typer(
    name="augment",
    add_completion=False,
    help="""These commands augment a single file.""",
)

aug = nac.KeyboardAug(aug_char_min=1,
                      aug_char_max=10,
                      aug_char_p=0.3,
                      aug_word_p=0.3,
                      aug_word_min=1,
                      aug_word_max=10,
                      include_special_char=False,
                      include_numeric=False,
                      include_upper_case=False)


def add_spelling_errors(dataf, aug, text_col="text"):
    """Applies the keyboard typos to a column in the dataframe."""    
    return dataf.assign(**{text_col: lambda d: aug.augment(list(d[text_col]), n=1)})


@app.command()
def augment(file: pathlib.Path = typer.Argument(..., help="The original nlu.yml file"), 
            out: pathlib.Path = typer.Option(pathlib.Path("."), help="Folder to write misspelled file to"), 
            prefix: str = typer.Option("misspelled")):
    """
    Applies keyboard typos to an existing NLU file and saves it to disk.
    """
    dataf = nlu_path_to_dataframe(file)
    out_path = out / f"{prefix}-{file.parts[-1]}"
    
    (dataf
      .pipe(add_spelling_errors, aug=aug)
      .pipe(dataframe_to_nlu_file, write_path=out_path, label_col="label"))


@app.command()
def generate(file: pathlib.Path, prefix="misspelled"):
    """
    Generate train/validation with/without misspelling for a Rasa project. 

    Will also generate files for the `/test` directory.
    """
    dataf = nlu_path_to_dataframe(file)
    
    X_train, X_test, y_train, y_test = train_test_split(dataf['text'], dataf['label'], 
                                                    test_size=0.33, random_state=42)

    df_valid = pd.DataFrame({'text': X_test, 'label': y_test}).sort_values(['label'])
    df_train = pd.DataFrame({'text': X_train, 'label': y_train}).sort_values(['label'])

    (df_train
        .pipe(dataframe_to_nlu_file, write_path="data/nlu-train.yml", label_col="label"))

    (df_valid
        .pipe(dataframe_to_nlu_file, write_path="test/nlu-valid.yml", label_col="label"))

    (df_train
        .pipe(add_spelling_errors, aug=aug)
        .pipe(dataframe_to_nlu_file, write_path=f"data/{prefix}-nlu-train.yml", label_col="label"))

    (df_valid
        .pipe(add_spelling_errors, aug=aug)
        .pipe(dataframe_to_nlu_file, write_path=f"test/{prefix}-nlu-valid.yml", label_col="label"))

