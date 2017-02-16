from __future__ import print_function, division

import music21
from copy import deepcopy

# Each number is midi pitch relative to the tonic of the chord
# Each chord shape has 14 possible things, mapping to genjam's 1-14

chord_shapes = {
    'maj': {'offsets': [0, 2, 4, 7, 9, 12, 14, 16, 19, 21, 24, 26, 28, 31]},
    'maj': {'offsets': [0, 2, 3, 7, 9, 12, 14, 15, 19, 21, 24, 26, 27, 31]},
    'maj7': {'offsets': [0, 2, 4, 7, 9, 11, 12, 14, 16, 19, 21, 23, 24, 26]},
    '7': {'offsets': [0, 2, 4, 7, 9, 10, 12, 14, 16, 19, 21, 22, 24, 26]},
    'min7': {'offsets': [0, 2, 3, 5, 7, 10, 12, 14, 15, 17, 19, 22, 24, 25]},
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

    def __init__(self, root, beats, shape, accompaniment):
        self.root = root
        self.beats = beats
        self.shape = shape
        self.accompaniment = accompaniment


class Metadata:

    def __init__(self, key, chords, time_signature, tempo, smallest_note, accompaniment=None):
        self.key = music21.key.Key(key)
        self.chords = chords
        self.time_signature = music21.meter.TimeSignature(time_signature)
        self.resolution = self.time_signature.denominator / smallest_note
        self.notes_per_beat = smallest_note / self.time_signature.denominator
        self.notes_per_measure = int(smallest_note * self.time_signature.numerator / self.time_signature.denominator)
        self.tempo = tempo
        self.ms_per_beat = (60 * 1000 / tempo)
        self.accompaniment = accompaniment

    def __str__(self):
        return '_'.join([str(self.key), str(self.time_signature.ratioString.replace('/', '-')),
                        str(self.resolution), str(self.tempo) + 'bpm'])


def phrase_to_parts(phrase, measure_population, metadata, accompany=False):
    measure_metadata = deepcopy(metadata)

    phrase_lead_part = music21.stream.Part()
    phrase_backing_part = music21.stream.Part()

    for measure in phrase:
        measure = measure_population.genomes[measure]
        measure_lead_part, measure_backing_part, beat_idx, chord_idx = measure_to_parts(measure,
                                                                                        measure_metadata,
                                                                                        accompany=accompany)
        phrase_lead_part.append(measure_lead_part)
        phrase_backing_part.append(measure_backing_part)

        measure_metadata.chords = measure_metadata.chords[chord_idx:]
        if len(measure_metadata.chords) == 0:
            measure_metadata.chords = deepcopy(metadata.chords)
        measure_metadata.chords[0].beats -= beat_idx

    return phrase_lead_part, phrase_backing_part


def measure_to_parts(measure, metadata, accompany=False):
    lead_part = music21.stream.Part()
    backing_part = music21.stream.Part()

    # do midi conversion
    chord_idx = 0
    idx = 0
    for genjam_e in measure:
        current_chord_info = metadata.chords[chord_idx]
        note_chord_offsets = chord_shapes[current_chord_info.shape]['offsets']
        genes_per_chord = current_chord_info.beats / metadata.resolution
        assert(genes_per_chord.is_integer())

        if accompany and idx == metadata.notes_per_beat:
            root = music21.note.Note(current_chord_info.root)
            midi_numbers = [root.pitch.midi + offset for offset in current_chord_info.accompaniment]
            chord = music21.chord.Chord(midi_numbers)
            chord.quarterLength = current_chord_info.beats
            chord.volume.velocity = 10
            backing_part.insert(chord)

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

    return lead_part, backing_part, idx * metadata.resolution, chord_idx
