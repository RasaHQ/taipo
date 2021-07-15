# `taipo confirm`

```
> python -m taipo confirm --help

  Confirms labels via a trained model.

Arguments:
  NLU_PATH    The nlu.yml file to check.  [required]
  MODEL_PATH  The Rasa model to use.  [required]
  OUT_PATH    CSV output path.  [required]

Options:
  --help  Show this message and exit.
```


![](../images/confirm.png)

The confirm command takes a pretrained Rasa model and runs it against one of
your nlu.yml files. The idea is that any intents that the model got wrong are
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
