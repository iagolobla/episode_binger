# Episode Binger

## Overview 
This package allows you to take a bunch of episodes with same openings/endings and join them together into one big file with one opening, all the episodes with no openings or endings and one final ending.

## Installation
Download the package and then, from the root folder run `python setup.py install`. Then the package should be installed as episode_binger.

## Requirements
For this project to run you must have ffmpeg installed in your computer, not only the python module but the software itself. More information about that here: https://github.com/kkroening/ffmpeg-python/tree/master#installing-ffmpeg.

## Recommendations

* Use mp4 format: That's the format I've been testing during development.
* If you get an error when executing, try more than once: There's some randomness involved with the algorithms so the performance can rely on that sometimes.

## Documentation
All the docs are located in the docs folder of this project. You can visit it in this link: https://iagolobla.github.io/episode_binger/

## Quick Start
You can try this short program as an example:

```
import episode_binger

eb = episode_binger.Episode_Binger()

# Add episodes to episode_binger
eb.add_episode("./input_data/Episode1.mp4")
eb.add_episode("./input_data/Episode2.mp4")
eb.add_episode("./input_data/Episode3.mp4")
eb.add_episode("./input_data/Episode4.mp4")
eb.add_episode("./input_data/Episode5.mp4")
eb.add_episode("./input_data/Episode6.mp4")

# Blind search for an opening and an ending
eb.find_opening_ending()

# Find opening and ending in every episode
eb.locate_opening_ending_every_episode()

# Create macro episode
eb.create_macro_episode("Six_Episodes.mp4")
```

If you execute that, the file "Six_Episodes.mp4" should be a macro-episode.