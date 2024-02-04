# Auditory Oddball framework in Python 

This Jupyter notebook provides a basic framework for [Oddball Experimentation](https://en.wikipedia.org/wiki/Oddball_paradigm) using the [Pygame](https://www.pygame.org/wiki/about) package. It presents participants with a sequence of repetitive stimuli, which are infrequently interrupted by a deviant stimulus, so that the participant's reaction to this "oddball" stimulus can be recorded and analyzed.

The motivation for this repo came when I was setting up real-life neuroscience experiments for my [DL-EEG-TES thesis](https://github.com/alexispomares/DL-EEG-TES), and I couldn't find any good Python package to design an auditory oddball paradigm. So I built my own and open-sourced for the neuroscientific community, hope it helps some of you. :)

# How to Use
Ensure that you have correctly installed the Pygame module, and simply run the `src/auditory_oddball.ipynb` notebook. You will be prompted to introduce the Participant ID once at the beginning of the session. After that you can start, pause, stop, or resume it as needed to run your Oddball Experiment. A number of parameters can be specified to achieve any desired paradigm:

- `n_beeps=30`             — Total number of auditory stimuli, per run
- `n_runs=10`              — Total number of runs, per experimental session
- `beep_duration=50`       — Sound duration, in milliseconds
- `silence_duration=1000`  — Interval between sounds, in milliseconds
- `standard_freq=400`      — Main frequency of normal sounds, in Hz
- `oddball_freq=1000`      — Main frequency of odd sounds, in Hz
- `ratio_oddball=0.2`      — Proportion of oddball/standard sounds

<br/>

![Auditory Oddball Recording](/img/auditory-oddball-recording.gif)
