<img src="icon.png" width="125" height="125" align="right" /> <img src="logo.svg" width=125 height=125 align="right">

# taipo

> taipo is a mispelling of typo, it means [evil spirit](https://en.wiktionary.org/wiki/taipo)

This project contains augmentation techniques to aid in the domain of mispellings
in NLP. In particular it hosts a suite of tools to generate spelling errors for Rasa NLU files.
The hope is that algorithms can be trained on these errors and that they become
more robust as a result.

Feedback on Non-English languages is *especially* appreciated!

## Install

You can install this experiment via pip.

```
python -m pip install "taipo @ git+https://github.com/RasaHQ/taipo.git"
```

## Usage

Taipo comes with a small suite of sub-commands.

```
> python -m taipo

  This app generates augmented datasets for Rasa nlu files. The hope is that
  such datasets can cause the models to train for robustness.

Options:
  --help  Show this message and exit.

Commands:
  keyboard  Commands to simulate keyboard typos.
  util      Some utility commands.
```

### `taipo keyboard`

These tools are able to simulate keyboard typos. It supports keyboard
layouts of 10 languages (`de`, `en`, `es`, `fr`, `he`, `it`, `nl`, `pl`, `th`, `uk`). For
more details on the mapping see [here](https://github.com/makcedward/nlpaug/tree/master/nlpaug/res/char/keyboard).

```
> python -m taipo keyboard

  Commands to simulate keyboard typos.

Options:
  --help  Show this message and exit.

Commands:
  augment   Applies typos to an NLU file and saves it to disk.
  generate  Generate train/validation data with/without misspelling.
```

### `taipo util`

We host some utility methods to transform intent-based data from .csv to .yml.
Be aware, these methods ignore entities!

```
> python -m taipo util

  Some utility commands.

Options:
  --help  Show this message and exit.

Commands:
  csv-to-yml  Turns a .csv file into nlu.yml for Rasa
  yml-to-csv  Turns a nlu.yml file into .csv
```


## Roadmap

- Implement a Greek character translator, [see forum inspiration](https://forum.rasa.com/t/phonetics-featurizer/42132/17).
