# `taipo confirm`

```
> python -m taipo confirm --help

  Confirm labels inside of nlu.yml files.

Options:
  --help  Show this message and exit.

Commands:
  logistic    Confirm via basic sklearn pipeline.
  rasa-model  Confirm via trained Rasa pipeline.
```

![](../images/confirm.png)

## `taipo confirm logistic`

This command trains a basic logistic regression model
and runs it against one of your `nlu.yml` files.

```
> taipo confirm logistic --help
Usage: confirm logistic [OPTIONS] MODEL_PATH NLU_PATH [OUT_PATH]

  Confirm via basic sklearn pipeline.

Arguments:
  NLU_PATH    The original nlu.yml file  [required]
  [OUT_PATH]  Path to write examples file to  [default: checkthese.csv]

Options:
  --help  Show this message and exit.
```

The idea is that any intents that the model got wrong are
interesting candidates to double-check. There may be some confusing/incorrectly
labelled examples in your data.

### Example Usage

This command will take the `nlu.yml` file, train a pipeline based on it
which it will then use to try to find bad labels. Any wrongly classifier
examples will be saved in the `checkthese.csv` file.

```
> python -m taipo confirm logistic nlu.yml checkthese.csv
```

The `checkthese.csv` file also contains a confidence level, indicating
the confidence that the model had while making the prediction. When a model
shows high confidence on a wrong label, it deserves priority.


## `taipo confirm rasa-model`

This command takes a pretrained Rasa model and runs it against one of
your nlu.yml files.

```
> taipo confirm rasa-model --help
Usage: confirm rasa-model [OPTIONS] MODEL_PATH NLU_PATH [OUT_PATH]

  Confirm via trained Rasa pipeline.

Arguments:
  MODEL_PATH  Location of Rasa model.  [required]
  NLU_PATH    The original nlu.yml file  [required]
  [OUT_PATH]  Path to write examples file to  [default: checkthese.csv]

Options:
  --help  Show this message and exit.
```

The idea is that any intents that the model got wrong are
interesting candidates to double-check. There may be some confusing/incorrectly
labelled examples in your data.

### Example Usage

This command will take the `model.tar.gz` model file and run it against
the `nlu.yml` file. Any wrongly classifier examples will be saved in the
`checkthese.csv` file.

```
> python -m taipo confirm nlu.yml model.tar.gz checkthese.csv
```

The `checkthese.csv` file also contains a confidence level, indicating
the confidence that the model had while making the prediction. When a model
shows high confidence on a wrong label, it deserves priority.
