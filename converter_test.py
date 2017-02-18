import music21

from converter import Metadata, phrase_to_parts, measure_to_parts, MyChord
from plonky import MeasurePopulation, Measure, Phrase


def main():
    # Chords are (tonic with register info, number of beats, chord shape)
    chords = [MyChord('C3', 4, 'maj'), MyChord('A2', 4, 'min'), MyChord('F2', 4, 'maj'), MyChord('G2', 4, 'maj')]
    smallest_note = 8
    metadata = Metadata('C', chords, '4/4', 100, smallest_note)

    # Generate some fake Phrases/Measures to test with
    measures = MeasurePopulation(1)
    for i in range(measures.size):
        m = Measure(metadata.notes_per_measure, 4)
        m.initialize()
        for j in range(0, m.length, 1):
            m[j] = 1 + j
            print(1 + j)
        measures.genomes.append(m)

    p = Phrase(4, 6)
    p.initialize()
    for i in range(p.length):
        p[i] = 0

    stream = phrase_to_parts(p, measures, metadata)
    # stream, _, _ = measure_to_midi(measures.genomes[0], metadata)
    sp = music21.midi.realtime.StreamPlayer(stream)
    sp.play()

if __name__ == "__main__":
    main()
