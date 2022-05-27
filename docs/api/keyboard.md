# `taipo keyboard`

```
> python -m taipo keyboard

  Commands to simulate keyboard typos.

Options:
  --help  Show this message and exit.

Commands:
  augment   Applies typos to an NLU file and saves it to disk.
  generate  Generate train/validation data with/without misspelling.
```

![](../images/keyboard.png)

These tools are able to simulate keyboard typos. It uses [nlpaug](https://github.com/makcedward/nlpaug)
as a backend and supports keyboard layouts of 10 languages
(`de`, `en`, `es`, `fr`, `he`, `it`, `nl`, `pl`, `th`, `uk`). For
more details on the mapping see [here](https://github.com/makcedward/nlpaug/tree/master/nlpaug/res/char/keyboard).

## `taipo keyboard augment`

The augment command generates a single misspelled NLU file.

```
python -m taipo keyboard augment --help
Usage: keyboard augment [OPTIONS] FILE OUT

  Applies typos to an NLU file and saves it to disk.

Arguments:
  FILE  The original nlu.yml file  [required]
  OUT   Path to write misspelled file to  [required]

Options:
  --char-max INTEGER  Max number of chars to change per line  [default: 3]
  --word-max INTEGER  Max number of words to change per line  [default: 3]
  --lang TEXT         Language for keyboard layout  [default: en]
  --seed-aug INTEGER  The seed value to augment the data
  --help              Show this message and exit.
```

### Example Usage

This example generates a new `bad-spelling-nlu.yml` file from `nlu.yml`.

```
python -m taipo keyboard augment data/nlu.yml data/bad-spelling-nlu.yml
```

This example generates does the same thing but assumes a Dutch keyboard layout.

```
python -m taipo keyboard augment data/nlu.yml data/bad-spelling-nlu.yml --lang nl
```

## `taipo keyboard generate`

The generate command takes a single NLU file and populates your data/test folders
with relevant files to run benchmarks. Will also perform train/validation splitting.

```
> python -m taipo keyboard generate --help
Usage: keyboard generate [OPTIONS] FILE

  Generate train/validation data with/without misspelling.

  Will also generate files for the `/test` directory.

Arguments:
  FILE  The original nlu.yml file  [required]

Options:
  --seed-split INTEGER  The seed value to split the data  [default: 42]
  --seed-aug INTEGER    The seed value to augment the data
  --test-size INTEGER   Percentage of data to keep as test data  [default: 33]
  --prefix TEXT         Prefix to add to all the files  [default: misspelled]
  --char-max INTEGER    Max number of chars to change per line  [default: 3]
  --word-max INTEGER    Max number of words to change per line  [default: 3]
  --lang TEXT           Language for keyboard layout  [default: en]
  --out-path PATH       Directory where the data and test subdirectories will
                        be created.  [default: ./]
  --help                Show this message and exit.
```

### Example Usage

This command will take the original `nlu-orig.yml` file and will use it to populate
the `/test` and `/data` folders.

```
> python -m taipo keyboard generate data/nlu-orig.yml
```

The current disk state is now:

```
📂 rasa-project
┣━━ 📂 data
┃   ┣━━ 📄 nlu-train.yml                ( 667 items)
┃   ┗━━ 📄 misspelled-nlu-train.yml     ( 667 items)
┣━━ 📂 tests
┃   ┣━━ 📄 nlu-valid.yml                ( 333 items)
┃   ┗━━ 📄 misspelled-nlu-valid.yml     ( 333 items)
┗━━ 📄 nlu-orig.yml                     (1000 items)
```
