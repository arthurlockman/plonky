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
        pass


class Phrase(Genome):

    def initialize(self):
        num_bits = self.number_size * self.length
        self.data = BitStream(bin=''.join([np.random.choice(('0', '1')) for _ in range(num_bits)]))
        pass

    def cross(self, other_genome):
        pass


class MeasurePopulation(Population):

    def select(self):
        pass


class PhrasePopulation(Population):

    def select(self):
        pass


def fitness(genome):
    print(genome)
    while True:
        f = input("f : ")
        if f == '1':
            genome.fitness = min(genome.fitness + 1, 30)
            break
        elif f == '-1':
            genome.fitness = max(genome.fitness - 1, -30)
            break
        elif f == '':
            break


def mutate(parent1, parent2, baby1, baby2):
    pass


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
    for i in range(measures.size):
        g = Measure(length=events_per_measure, number_size=4)
        g.initialize()
        measures.genomes.append(g)

    phrases = PhrasePopulation(48)
    for i in range(phrases.size):
        g = Phrase(length=measures_per_phrase, number_size=phrase_genome_len)
        g.initialize()
        phrases.genomes.append(g)

    N = 2
    for i in range(N):
        measures = run(measures, mutate_method=mutate, assign_fitness=fitness)
        phrases = run(measures, mutate_method=mutate, assign_fitness=fitness)
        print(phrases, measures)

