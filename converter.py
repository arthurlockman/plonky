from __future__ import print_function, division

import music21
from copy import deepcopy

# Each number is midi pitch relative to the tonic of the chord
# Each chord shape has 14 possible things, mapping to genjam's 1-14

chord_shapes = {
    'maj': {'offsets': [0, 2, 4, 7, 9, 12, 14, 16, 19, 21, 24, 26, 28, 31]},
    'min': {'offsets': [0, 2, 3, 7, 9, 12, 14, 15, 19, 21, 24, 26, 27, 31]},
    'maj7': {'offsets': [0, 2, 4, 7, 9, 11, 12, 14, 16, 19, 21, 23, 24, 26]},
    '7': {'offsets': [0, 2, 4, 7, 9, 10, 12, 14, 16, 19, 21, 22, 24, 26]},
    'min7': {'offsets': [0, 2, 3, 5, 7, 10, 12, 14, 15, 17, 19, 22, 24, 26]},
    'min7b5': {'offsets': [0, 3, 5, 6, 8, 10, 12, 15, 17, 18, 20, 22, 24, 27]},
    'dim': {'offsets': [0, 2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 18, 20]},
    '+': {'offsets': [0, 2, 4, 6, 8, 9, 11, 12, 14, 16, 18, 20, 21, 23]},
    '7+': {'offsets': [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26]},
    '7#11': {'offsets': [0, 2, 4, 6, 7, 9, 10, 12, 14, 16, 18, 19, 21, 22]},
    '7#9': {'offsets': [0, 1, 3, 4, 6, 8, 10, 12, 13, 15, 16, 18, 20, 22]},
    '7b9': {'offsets': [0, 1, 3, 4, 6, 7, 9, 10, 12, 13, 15, 16, 18, 19]},
    'm7b9': {'offsets': [0, 1, 3, 5, 7, 9, 10, 12, 13, 15, 17, 19, 21, 22]},
    'maj7#11': {'offsets': [0, 2, 4, 6, 7, 9, 11, 12, 14, 16, 18, 19, 21, 24]},
}


class MyChord:

    def __init__(self, root, beats, shape):
        self.root = root
        self.beats = beats
        self.shape = shape


class Metadata:

    def __init__(self, key, chords, time_signature, tempo, smallest_note, backing_velocity):
        self.key = music21.key.Key(key)
        self.chords = chords
        self.time_signature = music21.meter.TimeSignature(time_signature)
        self.resolution = self.time_signature.denominator / smallest_note
        self.notes_per_beat = smallest_note / self.time_signature.denominator
        self.notes_per_measure = int(smallest_note * self.time_signature.numerator / self.time_signature.denominator)
        self.tempo = tempo
        self.ms_per_beat = (60 * 1000 / tempo)
        self.backing_velocity = backing_velocity
        self.backing_stream = None
        self.events_per_note = int(4 * self.resolution)

    def __str__(self):
        return '_'.join([str(self.key), str(self.time_signature.ratioString.replace('/', '-')),
                        str(self.resolution), str(self.tempo) + 'bpm'])


def create_stream(phrases, measures, metadata):
    population_lead_part = music21.stream.Part()
    population_lead_part.insert(0, music21.instrument.Trumpet())

    for phrase in phrases:
        lead_part = phrase_to_parts(phrase, measures, metadata)
        population_lead_part.append(lead_part)

    if metadata.backing_stream:
        # TODO: somehow copy/extend the stream the correct number of times
        # so the backing track doesn't have to be hardcoded length
        stream = deepcopy(metadata.backing_stream)
    else:
        stream = music21.stream.Stream()

    # put Metronome and lead at the beginning
    stream.insert(0, music21.tempo.MetronomeMark(number=metadata.tempo))
    stream.insert(0, population_lead_part.flat)
    # insert just one midi 0 note to allow the piece to start with a rest
    n = music21.note.Note(music21.pitch.Pitch('C0'))
    n.volume.velocity = 1
    population_lead_part.insert(0, n)

    return stream


def phrase_to_parts(phrase, measure_population, metadata):
    measure_metadata = deepcopy(metadata)

    phrase_lead_part = music21.stream.Part()

    for measure_idx in phrase:
        measure = measure_population.genomes[measure_idx]
        lead_part, beat_idx, chord_idx = measure_to_parts(measure, measure_metadata)
        phrase_lead_part.append(lead_part)

        measure_metadata.chords = measure_metadata.chords[chord_idx:]
        if len(measure_metadata.chords) == 0:
            measure_metadata.chords = deepcopy(metadata.chords)
        measure_metadata.chords[0].beats -= beat_idx

    return phrase_lead_part


def measure_to_parts(measure, metadata):
    lead_part = music21.stream.Part()

    # do midi conversion
    chord_idx = 0
    idx = 0
    for genjam_e in measure:
        current_chord_info = metadata.chords[chord_idx]
        note_chord_offsets = chord_shapes[current_chord_info.shape]['offsets']
        genes_per_chord = current_chord_info.beats / metadata.resolution
        assert(genes_per_chord.is_integer())

        if genjam_e == 15:
            # hold the note
            if len(lead_part.notes) == 0:
                # rest if it's the first note
                lead_part.append(music21.note.Rest(quarterLength=metadata.resolution))
            else:
                # extend previous note or rest
                lead_part.notesAndRests[-1].duration.quarterLength += metadata.resolution
        elif genjam_e == 0:
            lead_part.append(music21.note.Rest(quarterLength=metadata.resolution))
        else:
            new_note = music21.note.Note(current_chord_info.root)
            new_note.duration.quarterLength = metadata.resolution
            tonic_midi_pitch = new_note.pitch.midi
            new_note.pitch.midi = tonic_midi_pitch + note_chord_offsets[genjam_e - 1]
            # Here is where you'd account for velocity
            new_note.volume.velocity = 127
            lead_part.append(new_note)

        idx += 1
        if idx == genes_per_chord:
            idx = 0
            chord_idx += 1

    return lead_part, idx * metadata.resolution, chord_idx


def set_stream_velocity(stream, velocity):
    for note in stream.recurse():
        if isinstance(note, music21.note.Note) or isinstance(note, music21.chord.Chord):
            note.volume.velocity = velocity
