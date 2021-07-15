# `taipo util`

```
> python -m taipo util

  Some utility commands.

Options:
  --help  Show this message and exit.

Commands:
  csv-to-yml  Turns a .csv file into nlu.yml for Rasa
  yml-to-csv  Turns a nlu.yml file into .csv
  summary     Displays summary tables for gridsearch results.
```

We host some utility methods to transform intent-based data from .csv to .yml. Be aware, these methods ignore entities!

## `taipo util csv-to-yml`

```
> python -m taipo util csv-to-yml --help
Usage: util csv-to-yml [OPTIONS] FILE

  Turns a .csv file into nlu.yml for Rasa

Arguments:
  FILE  The csv file to convert  [required]

Options:
  --out PATH        The path of the output file.  [default: .]
  --text-col TEXT   Name of the text column.  [default: text]
  --label-col TEXT  Name of the label column.  [default: intent]
  --help            Show this message and exit.
```

## `taipo util yml-to-csv`

```
> python -m taipo util csv-to-yml --help
Usage: __main__.py util yml-to-csv [OPTIONS] FILE

  Turns a nlu.yml file into .csv

Arguments:
  FILE  The csv file to convert  [required]

Options:
  --out PATH  The path of the output file.  [default: .]
  --help      Show this message and exit.
```

## `taipo util summary`

```
Usage: __main__.py util summary [OPTIONS] FOLDER

  Displays summary tables for gridsearch results.

Arguments:
  FOLDER  Folder that contains grid-result folders.  [required]

Options:
  --help      Show this message and exit.
```

### Example Usage

Let's say that you've got a folder structure like so:

```
📂 gridresults
┣━━ 📂 orig-model
┃   ┣━━ ...
┃   ┗━━ 📄 intent_report.json
┣━━ 📂 finetuned-model
┃   ┣━━ ...
┃   ┗━━ 📄 intent_report.json
┣━━ 📂 typo-orig-model
┃   ┣━━ ...
┃   ┗━━ 📄 intent_report.json
┗━━ 📂 typo-finetuned-model
    ┣━━ ...
    ┗━━ 📄 intent_report.json
```

Then you can get a convenient summary via:

```
python -m taipo util summary gridresults
```

You may get a table that looks like this:

```
┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┓
┃ folder                ┃ accuracy ┃ precision ┃ recall  ┃ f1      ┃
┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━┩
│ finetuned-model       │ 0.9022   │ 0.90701   │ 0.9022  │ 0.90265 │
│ orig-model            │ 0.90018  │ 0.90972   │ 0.90018 │ 0.90192 │
│ typo-finetuned-model  │ 0.89965  │ 0.90302   │ 0.89965 │ 0.89984 │
│ typo-orig-model       │ 0.79419  │ 0.82945   │ 0.79419 │ 0.80266 │
└───────────────────────┴──────────┴───────────┴─────────┴─────────┘
```
