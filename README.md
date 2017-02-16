# Plonky
Plonky is an intelligent jazz soloist.

## Installation/Setup

Use pycharm please.
Clone this repo, then open it in pycharm.

do this:

    sudo -H pip install music21 numpy

## Running and Training

The easiest way to train Plonky is to use our Docker image. To build an image and run a container, 
change directories to the project root and run:

    docker build -t plonky .
    docker run -it -v .:/plonky plonky

This will build the docker image, and run a new container with the project root mapped to `/plonky`.
