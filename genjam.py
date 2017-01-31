import sys
from math import log
import numpy as np
from bitstring import BitStream
from ga import Genome, Population, run, uint_to_bit_str


class Measure(Genome):

    def initialize(self):
        bit_str = ''
        for _ in range(self.length):
            e = np.random.rand()
            if e < 0.2:
                # rest
                bit_str += uint_to_bit_str(value=0, num_bits=4)
            elif e < 0.4:
                # hold
                bit_str += uint_to_bit_str(value=15, num_bits=4)
            else:
                # new note
                new_note_pitch = np.random.randint(1, 15)
                bit_str += uint_to_bit_str(new_note_pitch, self.number_size)

        self.data = BitStream(bin=bit_str)

    def cross(self, other_genome):
        bit_idx = np.random.randint(1, self.length * self.number_size - 1)
        baby1 = Phrase(self.length, self.number_size)
        baby1.data = self.data[:bit_idx] + other_genome.data[bit_idx:]
        baby2 = Phrase(self.length, self.number_size)
        baby2.data = other_genome.data[:bit_idx] + self.data[bit_idx:]
        return baby1, baby2

    def assign_fitness(self):
        self.fitness = int(np.random.rand() * 100)

    @staticmethod
    def mutate(parent1, parent2, baby1, baby2, population):
        def reverse(g):
            for first in range(g.length/2):
                last = g.length - 1 - first
                tmp = g[first]
                g[first] = g[last]
                g[last] = tmp

        def rotate(g):
            pass

        def invert(g):
            pass

        def sort_ascending(g):
            pass

        def sort_descending(g):
            pass

        def transpose(g):
            steps = np.random.randint(1, 4)
            pass

        mutations = [
            reverse,
            rotate,
            invert,
            sort_ascending,
            sort_descending,
            transpose,
        ]

        # do nothing to parents or baby1.
        # mutate baby2 in one of various ways
        mutation_func = np.random.choice(mutations, 1)[0]
        baby2 = reverse(baby2)


class Phrase(Genome):

    def initialize(self):
        num_bits = self.number_size * self.length
        self.data = BitStream(bin=''.join([np.random.choice(('0', '1')) for _ in range(num_bits)]))

    def cross(self, other_genome):
        bit_idx = np.random.randint(1, self.length * self.number_size - 1)
        baby1 = Phrase(self.length, self.number_size)
        baby1.data = self.data[:bit_idx] + other_genome.data[bit_idx:]
        baby2 = Phrase(self.length, self.number_size)
        baby2.data = other_genome.data[:bit_idx] + self.data[bit_idx:]
        return baby1, baby2

    def assign_fitness(self):
        self.fitness = int(np.random.rand() * 100)

    @staticmethod
    def mutate(parent1, parent2, baby1, baby2, population):
        def reverse(g):
            for first in range(g.length/2):
                last = g.length - 1 - first
                tmp = g[first]
                g[first] = g[last]
                g[last] = tmp

        def rotate(g):
            pass

        def genetic_repair(g):
            pass

        def super_phrase(g):
            pass

        def lick_thinner(g):
            pass

        def orphan(g):
            pass

        mutations = [
            reverse,
            rotate,
            genetic_repair,
            super_phrase,
            lick_thinner,
            orphan,
        ]

        # do nothing to parents or baby1.
        # mutate baby2 in one of various ways
        mutation_func = np.random.choice(mutations, 1)[0]
        baby2 = mutation_func(baby2)


class MeasurePopulation(Population):

    def select(self):
        # tournament style
        # assumes population size is multiple of 4

        # in-place shuffle genomes
        np.random.shuffle(self.genomes)
        selected = []

        for i in range(0, self.size, 4):
            # four random possible parents
            possible_parents = sorted(self.genomes[i:i+4], key=lambda g: g.fitness)
            # pick the best two
            parents = possible_parents[2:]
            selected.append(tuple(parents))

        return selected


class PhrasePopulation(Population):

    def select(self):
        # tournament style
        # assumes population size is multiple of 4

        # in-place shuffle genomes
        np.random.shuffle(self.genomes)
        selected = []

        for i in range(0, self.size, 4):
            # four random possible parents
            possible_parents = sorted(self.genomes[i:i+4], key=lambda g: g.fitness)
            # pick the best two
            parents = possible_parents[2:]
            selected.append(tuple(parents))

        return selected


if __name__ == '__main__':
    measure_pop_size = 64
    time_signature = (4, 4)
    smallest_note_duration = 8  #8 == 1/8th note
    measures_per_phrase = 4

    events_per_measure = smallest_note_duration * time_signature[0] / time_signature[1]

    if not events_per_measure.is_integer():
        sys.exit("You can't use 1/%i notes in %i/%i" % (smallest_note_duration, time_signature[0], time_signature[1]))
    events_per_measure = int(events_per_measure)

    phrase_genome_len = log(measure_pop_size, 2)
    if not phrase_genome_len.is_integer():
        sys.exit("Measure pop size must be power of 2. %i is not." % measure_pop_size)
    phrase_genome_len = int(phrase_genome_len)

    measures = MeasurePopulation(64)
    for _ in range(measures.size):
        g = Measure(length=events_per_measure, number_size=4)
        g.initialize()
        measures.genomes.append(g)

    phrases = PhrasePopulation(48)
    for _ in range(phrases.size):
        g = Phrase(length=measures_per_phrase, number_size=phrase_genome_len)
        g.initialize()
        phrases.genomes.append(g)

    N = 2
    for _ in range(N):
        measures = run(measures, mutate_method=Measure.mutate)
        phrases = run(measures, mutate_method=Phrase.mutate)
        print(phrases, measures)

