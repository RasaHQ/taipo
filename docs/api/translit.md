# `taipo translit`

```
> python -m taipo translit

  Commands to generate transliterations.

Options:
  --help  Show this message and exit.

Commands:
  augment   Applies translitertion to an NLU file and saves it to disk.
  generate  Generate train/validation data with/without translitertion.
```

![](../images/translit.png)

These tools are able to transliterate to and from a latin alphabet. It
uses [transliterate](https://github.com/barseghyanartur/transliterate) as
a backend and supports (`ru`, `mn`, `sr`, `bg`, `ka`, `uk`, `el`, `mk`, `l1`, `hy`).

## `taipo translit augment`

Transliterates a single NLU file to and from a latin alphabet.

```
> python -m taipo translit augment --help

  Applies translitertion to an NLU file and saves it to disk.

Arguments:
  FILE  The original nlu.yml file  [required]
  OUT   Path to write misspelled file to  [required]

Options:
  --target TEXT  Alphabet to map to.  [default: latin]
  --source TEXT  Alphabet to map from.  [default: latin]
  --lang TEXT    Language for keyboard layout  [default: en]
  --help         Show this message and exit.
```

### Example Usage

This example generates a new `greek-nlu.yml` file from `nlu.yml`.

```
python -m taipo keyboard augment data/nlu.yml data/greek-nlu.yml --target el
```

This example generates works the other way around. It assumes a Greek alphabet as
a starting point and transliterates it to the latin alphabet.

```
python -m taipo keyboard augment data/greek-nlu.yml data/latin-nlu.yml --source el
```

## `taipo translit generate`

The generate command takes a single NLU file and populates your data/test folders
with relevant files to run benchmarks. Will also perform train/validation splitting.

```
> python -m taipo translit generate --help

  Generate train/validation data with/without translitertion.

  Will also generate files for the `/test` directory.

Arguments:
  FILE  The original nlu.yml file  [required]

Options:
  --seed INTEGER       The seed value to split the data  [default: 42]
  --test-size INTEGER  Percentage of data to keep as test data  [default: 33]
  --prefix TEXT        Prefix to add to all the files  [default: translit]
  --target TEXT        Alphabet to map to.  [default: latin]
  --source TEXT        Alphabet to map from.  [default: latin]
  --lang TEXT          Language for keyboard layout  [default: en]
  --help               Show this message and exit.
```

### Example Usage

This command will take the original `nlu-orig.yml` file and will use it to populate
the `/test` and `/data` folders. In this case it will generate characters from the
Greek alphabet.

```
> python -m taipo translit generate data/nlu-orig.yml --prefix greek --target el
```

The following files will now be on disk.

```
📂 rasa-project
┣━━ 📂 data
┃   ┣━━ 📄 nlu-train.yml                ( 667 items)
┃   ┗━━ 📄 greek-nlu-train.yml          ( 667 items)
┣━━ 📂 tests
┃   ┣━━ 📄 nlu-valid.yml                ( 333 items)
┃   ┗━━ 📄 greek-nlu-valid.yml          ( 333 items)
┗━━ 📄 nlu-orig.yml                     (1000 items)
```
