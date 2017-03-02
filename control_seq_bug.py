import magenta
import magenta.music as mm
import tensorflow as tf
from magenta.models.improv_rnn import improv_rnn_config_flags
from magenta.models.improv_rnn import improv_rnn_model
from magenta.models.improv_rnn import improv_rnn_sequence_generator

FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_string(
    'bundle_file', None,
    'Path to the bundle file. If specified, this will take priority over '
    'run_dir, unless save_generator_bundle is True, in which case both this '
    'flag and run_dir are required')
setattr(FLAGS, 'config', 'chord_pitches_improv')
setattr(FLAGS, 'bundle_file', '/home/peter/Projects/magenta/bundles/chord_pitches_improv.mag')


def get_bundle():
    import os
    bundle_file = os.path.expanduser(FLAGS.bundle_file)
    return magenta.music.read_bundle_file(bundle_file)


if __name__ == '__main__':
    config = improv_rnn_config_flags.config_from_flags()
    generator = improv_rnn_sequence_generator.ImprovRnnSequenceGenerator(
        model=improv_rnn_model.ImprovRnnModel(config),
        details=config.details,
        steps_per_quarter=config.steps_per_quarter,
        bundle=get_bundle())
    generator.initialize()

    repeated_chords = ['C', 'E', 'F', 'G']

    backing_chords = magenta.music.ChordProgression(repeated_chords)

    melody_as_array = [60, 60, 60, 60]
    melody = magenta.music.Melody(melody_as_array)
    print(generator._model.melody_log_likelihood(melody, backing_chords))
