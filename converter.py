import sys
import numpy as np
from genjam import Measure, Phrase, MeasurePopulation
import music21


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


class SoloMetadata:

    def __init__(self, key, chords, time_signature, tempo, smallest_note):
        self.key = music21.key.Key(key)
        self.chords = chords
        self.time_signature = music21.meter.TimeSignature(time_signature)
        self.resolution = self.time_signature.denominator / smallest_note
        self.tempo = tempo


def phrase_to_midi(phrase, measure_population, metadata):
    genjam_events = []
    for on in phrase:
        measure = measure_population.genomes[on]
        genjam_events.extend(measure)

    s = music21.stream.Stream()
    s.append(music21.tempo.MetronomeMark(number=metadata.tempo))

    # do midi conversion
    harmonic_idx = 0
    idx = 0
    for genjam_e in genjam_events:

        current_chord_info = metadata.chords[harmonic_idx]
        note_chord_offsets = chord_shapes[current_chord_info[2]]
        beats_for_chord = current_chord_info[1] / metadata.resolution
        if genjam_e == 0:
            if len(s.notes) == 0:
                s.append(music21.note.Rest())

            # extend previous note or rest
            s.notesAndRests[-1].duration.quarterLength += metadata.resolution
        elif genjam_e == 15:
            s.append(music21.note.Rest())
        else:
            new_note = music21.note.Note(current_chord_info[0])
            new_note.duration.quarterLength = metadata.resolution
            tonic_midi_pitch = new_note.pitch.midi
            new_note.pitch.midi = tonic_midi_pitch + note_chord_offsets[genjam_e - 1]
            s.append(new_note)

        idx += 1
        if idx == beats_for_chord:
            idx = 0
            harmonic_idx += 1
            if harmonic_idx >= len(metadata.chords):
                harmonic_idx = 0

    return s


def main():
    # Chords are (tonic with register info, number of beats, chord shape)
    chords = [('C3', 4, 'maj'), ('A2', 4, 'min'), ('F2', 4, 'maj'), ('G2', 4, 'maj')]
    smallest_note = 8
    metadata = SoloMetadata('C', chords, '4/4', 100, smallest_note)

    measures = MeasurePopulation(10)
    for i in range(measures.size):
        m = Measure(smallest_note, 4)
        m.initialize()
        for j in range(m.length):
            m[j] = 1
        measures.genomes.append(m)

    p = Phrase(2, 6)
    p.initialize()
    for i in range(p.length):
        p[i] = i

    stream = phrase_to_midi(p, measures, metadata)

    sp = music21.midi.realtime.StreamPlayer(stream)

    def onEnd(args):
        print("Clip done")

    sp.play(endFunction=onEnd)


if __name__ == "__main__":
    main()
