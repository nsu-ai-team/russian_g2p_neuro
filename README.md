# russian_g2p_neuro
Experiments with grapheme2phoneme for Russian based on the artificial neural networks

## Getting Started

### Prerequisites

You should have a Python installed on your machine (we tested with Python 2.7 and Python 3.6). Also, you need the **Phonetisaurus GRP** https://github.com/AdolfVonKleist/Phonetisaurus and some Pyhton libraries listed in requirements.txt. If you do not have these Python libraries, run in Terminal

```
pip install -r requirements.txt
```

As for the **Phonetisaurus GRP**, for its installation you have to follow instructions from https://github.com/AdolfVonKleist/Phonetisaurus/blob/master/README.md

### Installing and Usage

#### Linux / MacOS
To install this project on your local machine, you should run the following commands in Terminal:

```
cd YOUR_FOLDER
git clone https://github.com/nsu-ai/russian_g2p_neuro.git
```

The project is now in YOUR_FOLDER.

This project contains three scripts:

- do_experiments.py
- compare_lexicons.py
- prepared_dict.py

Main script is `do_experiments.py`. Using this script you can:

1) create trainable G2P model;
2) estimate created G2P model by crossvalidation;
3) generate a new pronouncing dictionary for specified word list with created G2P model.

For this you need to specify:

- `-s`, or `--src`, a source word list;
- `-d`, or `--dst`, a new pronouncing dictionary which will be generated as a working result of script;
- `-t`, or `--train`, an existing pronouncing dictionary for training (by default the `data/ru_training.dic` is used);
- `-p`, or `--pmass`, % of total probability mass constraint for pronouncing generating, that allows to generate alternative phonetical transcriptions (by default 0.85 is using);
- `-n`, or `--ngram`, maximal N-gram size for probability phonetical models (by default 5 is used);
- `--cv`, a folds quantity for crossvalidation (by default 10 is used);
- `--seed`, a random seed (by default 0 is used).

The source word list is a simple text file. Each line of this file contains single word, for which pronouncing will be generated. Any word can consist only of alphabetical characters or some punctuation symbols, such as dash and single quote. No other characters are allowed (there shall not be digits, spaces etc.).

The existing pronouncing dictionary for training is a text file also, but it has a more complicated structure. Each line contains single word and its phonetical transcription, at that word and all phonemes are separated each other by spaces. For example, you can see the `data/ru_training.dic` (our pronouncing dictionary for Russian) or the CMUDict https://github.com/cmusphinx/cmudict/blob/master/cmudict.dict (the Carnegie Mellon Pronouncing Dictionary for English).

Example of script using described script:

```
python do_experiments.py \
    -s /home/user/language_models/russian/ngram/ruscorpora_vocabulary.txt \
    -t data/ru_training.dic \
    -d /home/user/language_models/russian/ngram/ruscorpora_phonetic_vocabulary_ngram10.txt \
    --ngram 10 --pmass 0.9 --cv 5 --seed 10
```

