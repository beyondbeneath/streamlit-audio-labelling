# streamlit-audio-labelling
An interface written in Streamlit to aid in the fast human labelling (annotation) of audio files, typically in a multiclass setting. Here we demonstrate the labelling of 20 frog species, a prototype developed for the [FrogID](https://www.frogid.net.au/) project of the [Australian Museum](https://australian.museum/).

## Installation

Setup a virtual environment and install requirements:

```
virtualenv .ve
pip install -r requirements.txt
```

Now activate the environment and run the app:

```
source .ve/bin/activate
streamlit run Intro.py
```

## Screenshot

<img src="https://github.com/beyondbeneath/streamlit-audio-labelling/blob/main/screenshot.png" width=600px>

## Notes

* You'll need to have the audio files contained in `data/3s` directory. In this example, they are named in the format `{fileId}-{chunkId}.wav`
* The file `data/syd-frogs.txt` is a reference of each record used, and is a tsv of the form `id, url, validated_frog_names, not_a_frog_type`
* The file `data/labels.json` is the current labelled data, and is what would be the output of this process which you can use for an ML input, it is multi-class and multi-label (i.e., one chunk can have multiple labels, since it's entirely possible for 2 things (frogs, insects, human-related noises) to be present in any given chunk). You can rename this file or delete it entirely to start from the state of no labels.
* `config.py` contains the superset of frog species, plus other available categories
* Some of the other functionality is a bit broken - attempts to use Streamlit sessions to maintain state across the pages, including experimental pages to show current labelling statistics and so on

## Contact

* Code - [Geoff Sims](mailto:geoffrey.sims@gmail.com)
* Project - [Jen Cork](mailto:jennifer.cork@australian.museum) or [GitHub profile](https://github.com/jencork)
