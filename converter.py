import music21
from copy import deepcopy

# Each number is midi pitch relative to the tonic of the chord
# Each chord shape has 14 possible things, mapping to genjam's 1-14
chord_shapes = {
    'maj': [0, 4, 7, 12, 16, 19, 24, 0, 4, 7, 12, 16, 19, 24],
    'min': [0, 3, 7, 12, 15, 19, 24, 0, 3, 7, 12, 15, 19, 24],
    'maj7': [0, 2, 4, 7, 9, 11, 12, 14, 16, 19, 21, 23, 24, 26],
    '7': [0, 2, 4, 7, 9, 10, 12, 14, 16, 19, 21, 22, 24, 26],
    'min7': [0, 2, 3, 5, 7, 10, 12, 14, 15, 17, 19, 22, 24, 25],
    'min7b5': [0, 3, 5, 6, 8, 10, 12, 15, 17, 18, 20, 22, 24, 27],
    'dim': [0, 2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 18, 20],
    '+': [0, 2, 4, 6, 8, 9, 11, 12, 14, 16, 18, 20, 21, 23],
    '7+': [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26],
    '7#11': [0, 2, 4, 6, 7, 9, 10, 12, 14, 16, 18, 19, 21, 22],
    '7#9': [0, 1, 3, 4, 6, 8, 10, 12, 13, 15, 16, 18, 20, 22],
    '7b9': [0, 1, 3, 4, 6, 7, 9, 10, 12, 13, 15, 16, 18, 19],
    'm7b9': [0, 1, 3, 5, 7, 9, 10, 12, 13, 15, 17, 19, 21, 22],
    'maj7#11': [0, 2, 4, 6, 7, 9, 11, 12, 14, 16, 18, 19, 21, 24]
}


class MyChord:

    def __init__(self, root, beats, shape):
        self.root = root
        self.beats = beats
        self.shape = shape


class Metadata:

    def __init__(self, key, chords, time_signature, tempo, smallest_note):
        self.key = music21.key.Key(key)
        self.chords = chords
        self.time_signature = music21.meter.TimeSignature(time_signature)
        self.resolution = self.time_signature.denominator / smallest_note
        self.notes_per_measure = int(smallest_note * self.time_signature.numerator / self.time_signature.denominator)
        self.tempo = tempo


def phrase_to_midi(phrase, measure_population, metadata):
    measure_metadata = deepcopy(metadata)

    phrase_stream = music21.stream.Stream()
    phrase_stream.append(music21.tempo.MetronomeMark(number=metadata.tempo))
    for measure in phrase:
        measure = measure_population.genomes[measure]
        measure_stream, beat_idx, chord_idx = measure_to_midi(measure, measure_metadata)

        # remove the MetronomeMark from the measure_stream
        measure_stream = measure_stream[1:]
        phrase_stream.append(measure_stream)

        measure_metadata.chords = measure_metadata.chords[chord_idx:]
        if len(measure_metadata.chords) == 0:
            measure_metadata.chords = deepcopy(metadata.chords)
        measure_metadata.chords[0].beats -= beat_idx

    return phrase_stream


def measure_to_midi(measure, metadata):
    s = music21.stream.Stream()
    s.append(music21.tempo.MetronomeMark(number=metadata.tempo))

    # do midi conversion
    chord_idx = 0
    idx = 0
    for genjam_e in measure:

        current_chord_info = metadata.chords[chord_idx]
        note_chord_offsets = chord_shapes[current_chord_info.shape]
        genes_per_chord = current_chord_info.beats / metadata.resolution
        assert(genes_per_chord.is_integer())
        if genjam_e == 0:
            if len(s.notes) == 0:
                s.append(music21.note.Rest())

            # extend previous note or rest
            s.notesAndRests[-1].duration.quarterLength += metadata.resolution
        elif genjam_e == 15:
            s.append(music21.note.Rest())
        else:
            new_note = music21.note.Note(current_chord_info.root)
            new_note.duration.quarterLength = metadata.resolution
            tonic_midi_pitch = new_note.pitch.midi
            new_note.pitch.midi = tonic_midi_pitch + note_chord_offsets[genjam_e - 1]
            s.append(new_note)

        idx += 1
        if idx == genes_per_chord:
            idx = 0
            chord_idx += 1

    return s, idx * metadata.resolution, chord_idx
