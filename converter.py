from __future__ import print_function, division

import music21
from copy import deepcopy

SUSTAIN = 127

# TRANSPOSE ASSUMES REST is 0
REST = 0


class MyChord:

    def __init__(self, root, beats, shape, accompaniment, bass=None):
        self.root = root
        self.beats = beats
        self.shape = shape
        self.accompaniment = accompaniment
        self.bass = bass


class Metadata:

    def __init__(self, key, chords, time_signature, tempo, smallest_note, backing_velocity, accompaniment=None):
        self.key = music21.key.Key(key)
        self.chords = chords
        self.time_signature = music21.meter.TimeSignature(time_signature)
        self.resolution = self.time_signature.denominator / smallest_note
        self.notes_per_beat = smallest_note / self.time_signature.denominator
        self.notes_per_measure = int(smallest_note * self.time_signature.numerator / self.time_signature.denominator)
        self.tempo = tempo
        self.ms_per_beat = (60 * 1000 / tempo)
        self.accompaniment = accompaniment
        self.backing_velocity = backing_velocity

    def __str__(self):
        return '_'.join([str(self.key), str(self.time_signature.ratioString.replace('/', '-')),
                        str(self.resolution), str(self.tempo) + 'bpm'])


def phrase_to_parts(phrase, measure_population, metadata, accompany=False):
    measure_metadata = deepcopy(metadata)

    phrase_lead_part = music21.stream.Part()
    phrase_backing_part = music21.stream.Part()
    phrase_bass_part = music21.stream.Part()

    for measure_idx in phrase:
        measure = measure_population.genomes[measure_idx]
        lead_part, backing_part, bass_part, beat_idx, chord_idx = measure_to_parts(measure,
                                                                                   measure_metadata,
                                                                                   accompany=accompany)
        phrase_lead_part.append(lead_part)
        phrase_backing_part.append(backing_part)
        phrase_bass_part.append(bass_part)

        measure_metadata.chords = measure_metadata.chords[chord_idx:]
        if len(measure_metadata.chords) == 0:
            measure_metadata.chords = deepcopy(metadata.chords)
        measure_metadata.chords[0].beats -= beat_idx

    return phrase_lead_part, phrase_backing_part, phrase_bass_part


def measure_to_parts(measure, metadata, accompany=False):
    lead_part = music21.stream.Part()
    backing_part = music21.stream.Part()
    bass_part = music21.stream.Part()

    # do midi conversion
    chord_idx = 0
    idx = 0
    for genjam_e in measure:
        current_chord_info = metadata.chords[chord_idx]
        genes_per_chord = current_chord_info.beats / metadata.resolution
        assert(genes_per_chord.is_integer())

        if accompany:
            root = music21.note.Note(current_chord_info.root)
            if idx % (metadata.notes_per_measure/2) == 0:
                midi_numbers = [root.pitch.midi + offset for offset in current_chord_info.accompaniment]
                chord = music21.chord.Chord(midi_numbers)
                # Currently we use half notes
                chord.quarterLength = 2
                chord.volume.velocity = metadata.backing_velocity
                backing_part.append(chord)

                if idx == 0 and current_chord_info.bass:
                    for ioi, offset in enumerate(current_chord_info.bass):
                        pitch = root.pitch.midi + offset
                        walking_bass_note = music21.note.Note(pitch)
                        if root.pitch.midi > 60:
                            walking_bass_note = walking_bass_note.transpose(-24)
                        else:
                            walking_bass_note = walking_bass_note.transpose(-12)
                        walking_bass_note.volume.velocity = metadata.backing_velocity
                        bass_part.insert(ioi, walking_bass_note)

        if genjam_e == SUSTAIN:
            # hold the note
            if len(lead_part.notes) == 0:
                # rest if it's the first note
                lead_part.append(music21.note.Rest(quarterLength=metadata.resolution))
            else:
                # extend previous note or rest
                lead_part.notesAndRests[-1].duration.quarterLength += metadata.resolution
        elif genjam_e == REST:
            lead_part.append(music21.note.Rest(quarterLength=metadata.resolution))
        else:
            new_note = music21.note.Note(genjam_e)
            new_note.duration.quarterLength = metadata.resolution
            # Here is where you'd account for velocity
            new_note.volume.velocity = 127
            lead_part.append(new_note)

        idx += 1
        if idx == genes_per_chord:
            idx = 0
            chord_idx += 1

    return lead_part, backing_part, bass_part, idx * metadata.resolution, chord_idx
