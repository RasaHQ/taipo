# `taipo util`

```
> python -m taipo util

  Some utility commands.

Options:
  --help  Show this message and exit.

Commands:
  csv-to-yml  Turns a .csv file into nlu.yml for Rasa
  yml-to-csv  Turns a nlu.yml file into .csv
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
