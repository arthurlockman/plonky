# Plonky
Plonky is an intelligent soloist.

## Installation/Setup

Pycharm is the recommended IDE for developement. Start by installing that. If you are using docker, you don't need to worry about setting up dependencies. Otherwise, continue reading to learn about getting Plonky up and running.

## Manually Setup

Install magenta: [https://github.com/tensorflow/magenta/#installation](https://github.com/tensorflow/magenta/#installation)

Make sure you source you magenta conda environment on every new terminal you start. Also make sure pycharm knows about it by setting the interpreter in the project settings. [More info on that here](https://docs.continuum.io/anaconda/ide_integration#pycharm).

Install some other packages:

    pip install music21 bistream pygame matplotlib numpy
    
Get or train your own magenta model. The easiest thing is to just download one from magenta's github, and change the line of code in `fitness.py` that looks like this:

    tf.app.flags.DEFINE_string(
        'bundle_file', '/home/peter/Projects/magenta/bundles/attention_rnn.mag',
        
Have that point to the .mag file you downloaded. Use the full path, and make sure this line of code is commented out:

    setattr(FLAGS, 'run_dir', 'logdir/20000')

## Running and Training

The easiest way to train Plonky is to use our Docker image. To build an image and run a container, 
change directories to the project root and run:

    docker run -it -v .:/plonky arthurlockman/plonky

This will build the docker image, and run a new container with the project root mapped to `/plonky`.
