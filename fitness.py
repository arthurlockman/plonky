from __future__ import division

import sys
import os

import magenta
import magenta.music as mm
import tensorflow as tf
from magenta.models.melody_rnn import melody_rnn_config_flags
from magenta.models.melody_rnn import melody_rnn_model
from magenta.models.melody_rnn import melody_rnn_sequence_generator

FLAGS = tf.app.flags.FLAGS

tf.app.flags.DEFINE_string(
    'run_dir', None,
    'Path to the directory where the latest checkpoint will be loaded from.')
tf.app.flags.DEFINE_string(
    'checkpoint_file', None,
    'Path to the checkpoint file. run_dir will take priority over this flag.')
tf.app.flags.DEFINE_string(
    'bundle_file', '/home/peter/Projects/magenta/bundles/lookback_rnn.mag',
    'Path to the bundle file. If specified, this will take priority over '
    'run_dir and checkpoint_file, unless save_generator_bundle is True, in '
    'which case both this flag and either run_dir or checkpoint_file are '
    'required')
tf.app.flags.DEFINE_boolean(
    'save_generator_bundle', False,
    'If true, instead of generating a sequence, will save this generator as a '
    'bundle file in the location specified by the bundle_file flag')
tf.app.flags.DEFINE_string(
    'bundle_description', None,
    'A short, human-readable text description of the bundle (e.g., training '
    'data, hyper parameters, etc.).')
tf.app.flags.DEFINE_string(
    'output_dir', '/tmp/melody_rnn/generated',
    'The directory where MIDI files will be saved to.')
tf.app.flags.DEFINE_integer(
    'num_outputs', 10,
    'The number of melodies to generate. One MIDI file will be created for '
    'each.')
tf.app.flags.DEFINE_integer(
    'num_steps', 128,
    'The total number of steps the generated melodies should be, priming '
    'melody length + generated steps. Each step is a 16th of a bar.')
tf.app.flags.DEFINE_string(
    'primer_melody', '',
    'A string representation of a Python list of '
    'magenta.music.Melody event values. For example: '
    '"[60, -2, 60, -2, 67, -2, 67, -2]". If specified, this melody will be '
    'used as the priming melody. If a priming melody is not specified, '
    'melodies will be generated from scratch.')
tf.app.flags.DEFINE_string(
    'primer_midi', '',
    'The path to a MIDI file containing a melody that will be used as a '
    'priming melody. If a primer melody is not specified, melodies will be '
    'generated from scratch.')
tf.app.flags.DEFINE_float(
    'qpm', None,
    'The quarters per minute to play generated output at. If a primer MIDI is '
    'given, the qpm from that will override this flag. If qpm is None, qpm '
    'will default to 120.')
tf.app.flags.DEFINE_integer(
    'steps_per_quarter', 4, 'What precision to use when quantizing the melody.')
tf.app.flags.DEFINE_float(
    'temperature', 1.0,
    'The randomness of the generated melodies. 1.0 uses the unaltered softmax '
    'probabilities, greater than 1.0 makes melodies more random, less than 1.0 '
    'makes melodies less random.')
tf.app.flags.DEFINE_integer(
    'beam_size', 1,
    'The beam size to use for beam search when generating melodies.')
tf.app.flags.DEFINE_integer(
    'branch_factor', 1,
    'The branch factor to use for beam search when generating melodies.')
tf.app.flags.DEFINE_integer(
    'steps_per_iteration', 1,
    'The number of melody steps to take per beam search iteration.')
tf.app.flags.DEFINE_string(
    'log', 'ERROR',
    'The threshold for what messages will be logged DEBUG, INFO, WARN, ERROR, '
    'or FATAL.')
# tf.app.flags.DEFINE_string(
#     'hparams', "{'batch_size':64,'rnn_layer_sizes':[64,64]}",
#     'something')
setattr(FLAGS, 'config', 'lookback_rnn')
setattr(FLAGS, 'hparams', "{'batch_size':64,'rnn_layer_sizes':[64,64]}")
# setattr(FLAGS, 'run_dir', 'logdir/20000')


def get_checkpoint():
    """Get the training dir or checkpoint path to be used by the model."""
    if ((FLAGS.run_dir or FLAGS.checkpoint_file) and
            FLAGS.bundle_file and not FLAGS.save_generator_bundle):
        raise magenta.music.SequenceGeneratorException(
            'Cannot specify both bundle_file and run_dir or checkpoint_file')
    if FLAGS.run_dir:
        train_dir = os.path.join(os.path.expanduser(FLAGS.run_dir), 'train')
        return train_dir
    elif FLAGS.checkpoint_file:
        return os.path.expanduser(FLAGS.checkpoint_file)
    else:
        return None


def get_bundle():
    """Returns a generator_pb2.GeneratorBundle object based read from bundle_file.

  Returns:
    Either a generator_pb2.GeneratorBundle or None if the bundle_file flag is
    not set or the save_generator_bundle flag is set.
  """
    if FLAGS.save_generator_bundle:
        return None
    if FLAGS.bundle_file is None:
        return None
    bundle_file = os.path.expanduser(FLAGS.bundle_file)
    return magenta.music.read_bundle_file(bundle_file)


def _steps_to_seconds(steps, qpm):
    """Converts steps to seconds.

  Uses the current flag value for steps_per_quarter.

  Args:
    steps: number of steps.
    qpm: current qpm.

  Returns:
    Number of seconds the steps represent.
  """
    return steps * 60.0 // qpm // FLAGS.steps_per_quarter


class FitnessFunction:
    def __init__(self):
        tf.logging.set_verbosity(FLAGS.log)

        config = melody_rnn_config_flags.config_from_flags()
        self.generator = melody_rnn_sequence_generator.MelodyRnnSequenceGenerator(
            model=melody_rnn_model.MelodyRnnModel(config),
            details=config.details,
            steps_per_quarter=FLAGS.steps_per_quarter,
            checkpoint=get_checkpoint(),
            bundle=get_bundle())
        if FLAGS.save_generator_bundle:
            bundle_filename = os.path.expanduser(FLAGS.bundle_file)
            if FLAGS.bundle_description is None:
                tf.logging.warning('No bundle description provided.')
            tf.logging.info('Saving generator bundle to %s', bundle_filename)
            self.generator.create_bundle_file(bundle_filename, FLAGS.bundle_description)
        else:
            self.generator.initialize()

    def evaluate_fitness(self, midi_sequence_file):
        tf_sequence = magenta.music.midi_file_to_sequence_proto(midi_sequence_file)
        quantized_sequence = mm.quantize_note_sequence(
            tf_sequence, 4)
        extracted_melodies, _ = mm.extract_melodies(
            quantized_sequence, min_bars=0,
            min_unique_pitches=1, gap_bars=float('inf'),
            ignore_polyphonic_notes=True)
        l = len(extracted_melodies)
        if l == 0:
            print("No melodies found")
        elif l > 1:
            sys.exit("too many melodies found")

        if extracted_melodies and extracted_melodies[0]:
            melody = extracted_melodies[0]
        else:
            return None, None
        return self.generator._model.melody_log_likelihood(melody), len(extracted_melodies[0])

def main(unused_argv):
    ff = FitnessFunction()
    print ff.evaluate_fitness('test.mid')


if __name__ == '__main__':
    tf.app.run(main)
