# taipo

> taipo is a mispelling of typo, it means [evil spirit](https://en.wiktionary.org/wiki/taipo)

This project contains augmentation techniques to aid in the domain of mispellings
in NLP. In particular it hosts a suite of tools to generate spelling errors for Rasa. 
The hope is that algorithms can be trained on these errors and that they become 
more robust as a result.

Feedback on Non-English languages is especially appreciated!

```
rasa train nlu --nlu data/nlu-train.yml         # 0.9789016248897846
rasa test nlu --nlu test/nlu-valid.yml          # 0.8969441247922261
rasa test nlu --nlu test/nlu-valid-spelling.yml # 0.7396752333461194

rasa train nlu --nlu data/nlu-train-spelling.yml --finetune --epoch-fraction 0.1 --fixed-model-name spelling-epoch-1
rasa test nlu --nlu test/nlu-valid-spelling.yml # 0.786088735455824

rasa train nlu --nlu data/nlu-train-spelling.yml --finetune models/nlu-20210628-131700.tar.gz  --epoch-fraction 0.2 --fixed-model-name spelling-epoch-2
rasa test nlu --nlu test/nlu-valid-spelling.yml # 0.8163917657588544

rasa train nlu --nlu data/nlu-train-spelling.yml --finetune models/nlu-20210628-131700.tar.gz  --epoch-fraction 0.3 --fixed-model-name spelling-epoch-3
rasa test nlu --nlu test/nlu-valid-spelling.yml # 0.8248305843242552
```

## Roadmap

- Implement relevant tools from [nlpaug](https://github.com/makcedward/nlpaug) or [typo](https://pypi.org/project/typo/).
- Implement a Greek character translator.

