import unittest
from copy import deepcopy
from converter import measure_to_midi, phrase_to_midi, chord_shapes, MyChord, Metadata
from genjam import Measure, Phrase, PhrasePopulation, MeasurePopulation
import music21

class MutationTests(unittest.TestCase):

    def test_measure_reverse(self):
        m = Measure(4, 4)
        m.initialize()
        m[0] = 0
        m[1] = 1
        m[2] = 2
        m[3] = 3
        Measure.reverse(m)

        self.assertEqual(m[0], 3)
        self.assertEqual(m[1], 2)
        self.assertEqual(m[2], 1)
        self.assertEqual(m[3], 0)

    def test_measure_rotate(self):
        m = Measure(4, 4)
        m.initialize()
        m[0] = 0
        m[1] = 1
        m[2] = 2
        m[3] = 3
        Measure._rotate(m, 1)

        self.assertEqual(m[0], 3)
        self.assertEqual(m[1], 0)
        self.assertEqual(m[2], 1)
        self.assertEqual(m[3], 2)

        Measure._rotate(m, 1)

        self.assertEqual(m[0], 2)
        self.assertEqual(m[1], 3)
        self.assertEqual(m[2], 0)
        self.assertEqual(m[3], 1)

    def test_measure_invert(self):
        m = Measure(4, 4)
        m.initialize()
        m[0] = 0
        m[1] = 1
        m[2] = 2
        m[3] = 3
        Measure.invert(m)

        self.assertEqual(m[0], 15)
        self.assertEqual(m[1], 14)
        self.assertEqual(m[2], 13)
        self.assertEqual(m[3], 12)

    def test_measure_ascending(self):
        m = Measure(8, 4)
        m.initialize()
        m[0] = 9
        m[1] = 7
        m[2] = 0
        m[3] = 5
        m[4] = 7
        m[5] = 15
        m[6] = 15
        m[7] = 0
        Measure.sort_ascending(m)

        self.assertEqual(m[0], 5)
        self.assertEqual(m[1], 7)
        self.assertEqual(m[2], 0)
        self.assertEqual(m[3], 7)
        self.assertEqual(m[4], 9)
        self.assertEqual(m[5], 15)
        self.assertEqual(m[6], 15)
        self.assertEqual(m[7], 0)

    def test_measure_descending(self):
        m = Measure(8, 4)
        m.initialize()
        m[0] = 9
        m[1] = 7
        m[2] = 0
        m[3] = 5
        m[4] = 7
        m[5] = 15
        m[6] = 15
        m[7] = 0
        Measure.sort_descending(m)

        self.assertEqual(m[0], 9)
        self.assertEqual(m[1], 7)
        self.assertEqual(m[2], 0)
        self.assertEqual(m[3], 7)
        self.assertEqual(m[4], 5)
        self.assertEqual(m[5], 15)
        self.assertEqual(m[6], 15)
        self.assertEqual(m[7], 0)

    def test_measure_transpose(self):
        m = Measure(4, 4)
        m.initialize()
        m[0] = 1
        m[1] = 4
        m[2] = 8
        m[3] = 14
        Measure._transpose(m, 2)

        self.assertEqual(m[0], 3)
        self.assertEqual(m[1], 6)
        self.assertEqual(m[2], 10)
        self.assertEqual(m[3], 12)

        Measure._transpose(m, -2)

        self.assertEqual(m[0], 1)
        self.assertEqual(m[1], 4)
        self.assertEqual(m[2], 8)
        self.assertEqual(m[3], 10)

        Measure._transpose(m, -2)

        self.assertEqual(m[0], 3)
        self.assertEqual(m[1], 2)
        self.assertEqual(m[2], 6)
        self.assertEqual(m[3], 8)

    def test_phrase_reverse(self):
        p = Phrase(4, 4)
        p.initialize()
        p[0] = 0
        p[1] = 1
        p[2] = 2
        p[3] = 3
        Phrase.reverse(p)

        self.assertEqual(p[0], 3)
        self.assertEqual(p[1], 2)
        self.assertEqual(p[2], 1)
        self.assertEqual(p[3], 0)

    def test_phrase_rotate(self):
        p = Phrase(4, 4)
        p.initialize()
        p[0] = 0
        p[1] = 1
        p[2] = 2
        p[3] = 3
        Phrase._rotate(p, 1)

        self.assertEqual(p[0], 3)
        self.assertEqual(p[1], 0)
        self.assertEqual(p[2], 1)
        self.assertEqual(p[3], 2)

        Phrase._rotate(p, 1)

        self.assertEqual(p[0], 2)
        self.assertEqual(p[1], 3)
        self.assertEqual(p[2], 0)
        self.assertEqual(p[3], 1)

    def test_phrase_genetic_repair(self):
        p = Phrase(4, 4)
        p.initialize()
        p[0] = 4
        p[1] = 1  # the worst one, will be replaced
        p[2] = 6
        p[3] = 9
        Phrase._genetic_repair(p, 8)

        self.assertEqual(p[0], 4)
        self.assertEqual(p[1], 8)
        self.assertEqual(p[2], 6)
        self.assertEqual(p[3], 9)

    def test_phrase_super(self):
        pop = MeasurePopulation(10)
        for i in range(pop.size):
            m = Measure(4, 4)
            m.initialize()
            m.fitness = i
            pop.genomes.append(m)

        p = Phrase(4, 4)
        original_p = deepcopy(p)
        p.initialize()
        Phrase.super_phrase(p, None, pop)

        # not a very good test...
        self.assertNotEquals(p, original_p)

    def test_lick_thinner(self):
        pop = PhrasePopulation(10)
        for i in range(pop.size):
            p = Phrase(4, 4)
            p.initialize()
            # 0 will occur most often
            p[0] = 0
            p[1] = 0
            p[2] = 2
            p[3] = 3
            pop.genomes.append(p)

        p = Phrase(4, 4)
        p.initialize()
        p[0] = 0
        p[1] = 3
        p[2] = 2
        p[3] = 1
        Phrase._lick_thinner(p, pop, 12)

        self.assertEqual(p[0], 12)
        self.assertEqual(p[1], 3)
        self.assertEqual(p[2], 2)
        self.assertEqual(p[3], 1)

    def test_orphan(self):
        pop = PhrasePopulation(10)
        for i in range(pop.size):
            p = Phrase(4, 4)
            p.initialize()
            # 0 will occur most often
            p[0] = 4
            p[1] = 5
            p[2] = 6
            p[3] = 7
            pop.genomes.append(p)

        p = Phrase(4, 4)
        p.initialize()
        p[0] = 0
        p[1] = 1
        p[2] = 2
        p[3] = 3
        original_p = deepcopy(p)

        mpop = MeasurePopulation(8)
        Phrase.orphan(p, pop, mpop)

        # not a very good test...
        self.assertNotEquals(p, original_p)

class ConverterTests(unittest.TestCase):

    def test_conversion_4_4_8ths(self):
        chords = [MyChord('C3', 4, 'maj'), MyChord('A2', 4, 'min'), MyChord('F2', 4, 'maj'), MyChord('G2', 4, 'maj')]
        smallest_note = 8
        metadata = Metadata('C', chords, '4/4', 100, smallest_note)

        for i in range(200):
            m = Measure(metadata.notes_per_measure, 4)
            m.initialize()
            stream, _, _ = measure_to_midi(m, metadata)

            measure_len = 0
            for event in stream:
                if isinstance(event, music21.note.Note) or isinstance(event, music21.note.Rest):
                    measure_len += event.quarterLength

            self.assertEqual(measure_len, 4)
