# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Generate melodies from a trained checkpoint of an improv RNN model."""

import os

import magenta
import magenta.music as mm
import tensorflow as tf
from magenta.models.improv_rnn import improv_rnn_config_flags
from magenta.models.improv_rnn import improv_rnn_model
from magenta.models.improv_rnn import improv_rnn_sequence_generator
from magenta.protobuf import music_pb2

CHORD_SYMBOL = music_pb2.NoteSequence.TextAnnotation.CHORD_SYMBOL

# Velocity at which to play chord notes when rendering chords.
CHORD_VELOCITY = 50

FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_string(
    'run_dir', None,
    'Path to the directory where the latest checkpoint will be loaded from.')
tf.app.flags.DEFINE_string(
    'bundle_file', None,
    'Path to the bundle file. If specified, this will take priority over '
    'run_dir, unless save_generator_bundle is True, in which case both this '
    'flag and run_dir are required')
tf.app.flags.DEFINE_boolean(
    'save_generator_bundle', False,
    'If true, instead of generating a sequence, will save this generator as a '
    'bundle file in the location specified by the bundle_file flag')
tf.app.flags.DEFINE_string(
    'bundle_description', None,
    'A short, human-readable text description of the bundle (e.g., training '
    'data, hyper parameters, etc.).')
tf.app.flags.DEFINE_string(
    'output_dir', '/tmp/improv_rnn/generated',
    'The directory where MIDI files will be saved to.')
tf.app.flags.DEFINE_integer(
    'num_outputs', 10,
    'The number of lead sheets to generate. One MIDI file will be created for '
    'each.')
tf.app.flags.DEFINE_integer(
    'steps_per_chord', 16,
    'The number of melody steps to take per backing chord. Each step is a 16th '
    'of a bar, so if backing_chords = "C G Am F" and steps_per_chord = 16, '
    'four bars will be generated.')
tf.app.flags.DEFINE_string(
    'primer_melody', '[60, -2]',
    'A string representation of a Python list of '
    'magenta.music.Melody event values. For example: '
    '"[60, -2, 60, -2, 67, -2, 67, -2]". If specified, this melody will be '
    'used as the priming melody. If a priming melody is not specified, '
    'melodies will be generated from scratch.')
tf.app.flags.DEFINE_string(
    'backing_chords', 'C G Am F C G F C',
    'A string representation of a chord progression, with chord symbols '
    'separated by spaces. For example: "C Dm7 G13 Cmaj7". The duration of each '
    'chord, in steps, is specified by the steps_per_chord flag.')
tf.app.flags.DEFINE_string(
    'primer_midi', '',
    'The path to a MIDI file containing a melody that will be used as a '
    'priming melody. If a primer melody is not specified, melodies will be '
    'generated from scratch.')
tf.app.flags.DEFINE_boolean(
    'render_chords', False,
    'If true, the backing chords will also be rendered as notes in the output '
    'MIDI files.')
tf.app.flags.DEFINE_float(
    'qpm', None,
    'The quarters per minute to play generated output at. If a primer MIDI is '
    'given, the qpm from that will override this flag. If qpm is None, qpm '
    'will default to 120.')
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
    'log', 'INFO',
    'The threshold for what messages will be logged DEBUG, INFO, WARN, ERROR, '
    'or FATAL.')
setattr(FLAGS, 'config', 'chord_pitches_improv')
setattr(FLAGS, 'bundle_file', '/home/peter/Projects/magenta/bundles/chord_pitches_improv.mag')


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


class FitnessFunction:

    def __init__(self, chords):
        """Saves bundle or runs generator based on flags."""
        tf.logging.set_verbosity(FLAGS.log)

        config = improv_rnn_config_flags.config_from_flags()
        self.generator = improv_rnn_sequence_generator.ImprovRnnSequenceGenerator(
            model=improv_rnn_model.ImprovRnnModel(config),
            details=config.details,
            steps_per_quarter=config.steps_per_quarter,
            bundle=get_bundle())
        self.generator.initialize()

        repeated_chords = []
        for my_chord in chords:
            root = my_chord.root[:-1].replace('-', 'b')
            name = root + my_chord.shape
            for _ in range(my_chord.beats * 4):
                repeated_chords.append(name)

        # TODO: why must this be here? https://groups.google.com/a/tensorflow.org/forum/#!topic/magenta-discuss/nlfd1xkrq6Q
        repeated_chords.append('C')

        self.backing_chords = magenta.music.ChordProgression(repeated_chords)

    def evaluate_fitness(self, melody_as_array):
        melody = magenta.music.Melody(melody_as_array)
        return self.generator._model.melody_log_likelihood(melody, self.backing_chords), len(melody)
