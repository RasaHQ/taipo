# Getting Started

The original goal of `taipo` was to augment NLU data such that we can train
Rasa models to be robust against misspellings. This guide will show you how
to train models that are robust against spelling errors.

## Installation

You can install this experiment via pip.

```
python -m pip install "taipo @ git+https://github.com/RasaHQ/taipo.git"
```

This will install the `taipo` command line interface in your virtualenv.
You can confirm the installation went fine by running:

```
python -m taipo
```

## Generating Spelling Errors

Let's say that you've gotten a Rasa project. Your folder
structure would look something like:

```
📂 rasa-project-dir
┣━━ 📂 actions
┣━━ 📂 data
┃   ┣━━ 📄 nlu.yml
┃   ┣━━ 📄 rules.yml
┃   ┗━━ 📄 stories.yml
┣━━ 📂 models
┣━━ 📂 tests
┣━━ 📄 config.yml
┣━━ 📄 credentials.yml
┣━━ 📄 domain.yml
┗━━ 📄 endpoints.yml
```

The idea is that we will generate a variant of `nlu.yml` that contains spelling errors.
This way, we might be able to train our models to be robust against it.

A straightforward way to do this is via;

```
python -m taipo keyboard augment data/nlu.yml data/typo-nlu.yml
```

This will generate a new file that contains typos.

```
📂 rasa-project-dir
┣━━ 📂 actions
┣━━ 📂 data
┃   ┣━━ 📄 nlu.yml
┃   ┣━━ 📄 typo-nlu.yml
┃   ┣━━ 📄 rules.yml
┃   ┗━━ 📄 stories.yml
┣━━ 📂 models
┣━━ 📂 tests
┣━━ 📄 config.yml
┣━━ 📄 credentials.yml
┣━━ 📄 domain.yml
┗━━ 📄 endpoints.yml
```

When you inspect the `typo-nlu.yml` file you'll notice that we copied each
example from the original `nlu.yml` file but added some typos. These typos
are based on the keyboard layout. The base setting assumes the US layout but
you can configure some non-English layouts as well. Check the [API docs](../api/keyboard/) for
more info.

When you now train your nlu model, it will also train on these misspelled items.

```
python -m rasa train
```

You will notice that training takes a fair bit longer because we're training
on twice as much data now.

## Finetuning

If you're worried about the long training time, you may prefer to use the fine-tuning
feature instead. If you're unfamiliar with the technique, you may appreciate this
algorithm whiteboard video.

<iframe width="100%" height="480" src="https://www.youtube-nocookie.com/embed/FipRjQRaCz8" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

To train the system with finetuning you can first train your NLU model on
the original data.

```
rasa train nlu --nlu nlu/nlu.yml --fixed-model-name orig
```

Once this model is trained, you can finetune it on the misspelled data.

```
rasa train nlu --nlu nlu/nlu.yml \
               --finetune models/orig.tar.gz \
               --epoch-fraction 0.1 \
               --fixed-model-name finetuned
```

## Benchmarking

Training against misspelled data is nice, but we'd also like to quantify the effect
that typos have on our system. This guide assumes that you have a `tests/nlu-valid.yml`
file which can be used as a validation dataset. Let's make a misspelled variant of this
dataset first.

```
python -m taipo keyboard augment tests/nlu-valid.yml tests/typo-nlu-valid.yml
```

We can now run our two models `models/orig.tar.gz` and `models/finetuned.tar.gz` against
both of these datasets.


```
rasa test nlu -u tests/nlu-valid.yml --model models/orig.tar.gz --out gridresults/orig-model
rasa test nlu -u tests/nlu-valid.yml --model models/finetuned.tar.gz --out gridresults/finetuned-model
rasa test nlu -u tests/typo-nlu-valid.yml --model models/orig.tar.gz --out gridresults/typo-orig-model
rasa test nlu -u tests/typo-nlu-valid.yml --model models/finetuned.tar.gz --out gridresults/typo-finetuned-model
```

This results in 4 folders that contain your benchmarked results. You could use
[rasalit](https://github.com/RasaHQ/rasalit#overview) to visualise these but you
can also use a utility function from the command line. Let's say that you've got
a folder structure like so:

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

## Feedback

This project is part of ongoing research. In general NLP algorithms have proven to be brittle
against typos and we wanted to make it easy for our community to investigate this. Feedback
on the tool, as well as any interesting typo-related findings, is much appreciated.

Feel free to mention any bugs on [Github](https://github.com/RasaHQ/taipo/issues/new) and any
other feedback on [the rasa forum](https://forum.rasa.com/). You can poke
`@koaning` on the Rasa forum if you have any typo-related insights. Especially insights from
non-English languages would be much appreciated!
