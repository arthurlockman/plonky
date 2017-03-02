# Plonky
Plonky is an intelligent soloist.

## Development

Pycharm is the recommended IDE for development. Start by installing that. If you are using docker, you don't need to worry about setting up dependencies. Otherwise, continue reading to learn about getting Plonky up and running.

Please submit any issues or bugs through the GitHub issue tracker.

## Manual Setup

Install magenta: [https://github.com/tensorflow/magenta/#installation](https://github.com/tensorflow/magenta/#installation)

Make sure you source you magenta conda environment on every new terminal you start. Also make sure pycharm knows about it by setting the interpreter in the project settings. [More info on that here](https://docs.continuum.io/anaconda/ide_integration#pycharm).

Install some other packages:

    pip install music21 bistream pygame matplotlib numpy
    
Get or train your own magenta model. The easiest thing is to just download one from magenta's github, and change the line of code in `fitness.py` that looks like this:

    tf.app.flags.DEFINE_string(
        'bundle_file', '/home/peter/Projects/magenta/bundles/attention_rnn.mag',
        
Have that point to the .mag file you downloaded. Use the full path, and make sure this line of code is commented out:

    setattr(FLAGS, 'run_dir', 'logdir/20000')

## Setup with Docker

The easiest way to train Plonky is to use our Docker image. To build an image and run a container, 
change directories to the project root and run:

    docker run -it -v /path/to/your/plonky/root:/plonky arthurlockman/plonky

This will build the docker image, and run a new container with the project root mapped to `/plonky`.


### PyCharm Integration

It is possible to use Docker as your interpreter in your PyCharm project. Detailed instructions for this can be found [here](https://blog.jetbrains.com/pycharm/2015/12/using-docker-in-pycharm/), on the JetBrains blog. Please note that the instructions are slightly different if you are on a Mac. You will need to run a separate process in the terminal while your PyCharm instance is running:

    socat TCP-LISTEN:8099,reuseaddr,fork,bind=localhost UNIX-CONNECT:/var/run/docker.sock

This allows PyCharm to communicate with docker. You then give PyCharm `localhost:8099` as the docker address in the project interpreter settings, and you should be good to go.

### Caveats

There are a few things to be aware of when using the docker image for running Plonky. The first is that performance will be poorer than running outside of docker. You will also not be able to use manual training out of the box. There is a discussion on how to enable sound in Docker containers [here](https://github.com/jessfraz/dockerfiles/issues/85) which may be of some use to you.

## Running

To run, simply use:

    python plonky.py [--debug] [--resume] [--manual] [--backing (/path/to/backing.xml)] [--play] [--render] [--generations (number of generations)]

The flags are detailed below:

* `--debug` Allows for attaching a debugger.
* `--resume` Resumes the most recent training session.
* `--manual` Runs Plonky in a manual training mode. If not supplied, it will use the automatic fitness function.
* `--backing` For manual mode, specify a backing track to play along with the solos.
* `--play` Play the last generation.
* `--render` Render the last generation.
* `--generations` The number of generations to run.