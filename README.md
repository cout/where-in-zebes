Where in Zebes?
===============

Where in Zebes? (WIZ) is a program for estimating the probability of
finding a "good" item in that each location in a seed produced by the
VARIA Randomizer for Super Metroid.

It currently only works for SMRAT2020 seeds, but could easily be
modified to work with other seeds.

An autotracker is available that works with Retroarch.  To use it,
enable Network Commands in retroarch and pass the `--autotrack` flag to
zebbo.

The interface is curses-based, but a web-based interface is planned.

Setup
-----

    make

Usage
-----

    ./zebbo.py [--autotrack]
