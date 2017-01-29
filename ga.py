import sys
from bitstring import BitStream, CreationError
import numpy as np


def run(current_population, mutate_method, assign_fitness):
        for genome in current_population.genomes:
            assign_fitness(genome)

        selected_genomes = current_population.select()
        new_genomes = []
        for i, pair in enumerate(selected_genomes):
            g1, g2 = pair
            baby1, baby2 = g1.cross(g2)
            new_genomes += [baby1, baby2, g1, g2]

            mutate_method(g1, g2, baby1, baby2)
        current_population.genomes = new_genomes

        return current_population


class Genome:

    def __init__(self, length, number_size):
        self.number_size = number_size
        self.MAX_INT = 1 << (number_size - 1) - 1
        self.MIN_INT = -1 << (number_size - 1)
        self.size = length
        self.data = BitStream()
        self.fitness = 0
        self.id = 0

    def cross(self, other_genome):
        pass

    def initialize(self):
        pass

    def __getitem__(self, idx):
        ''' get idx'th number genome as integer '''
        as_list = [n for n in self.data.cut(self.number_size)]
        if isinstance(idx, slice):
            return [n.int for n in as_list[idx]]
        elif isinstance(idx, int):
            return as_list[idx].int
        else:
            raise TypeError("ya fucked up")

    def __setitem__(self, idx, value):
        ''' set idx'th number genome as integer '''
        new_bin_str = ''
        for i, n in enumerate(self.data.cut(self.number_size)):
            if i == idx:
                try:
                    new_bin_str += BitStream(length=self.number_size, int=value).bin
                except CreationError as ce:
                    sys.exit('%i is out of the range of %i bits. Range is (%i,%i)'
                             % (value, self.number_size, self.MIN_INT, self.MAX_INT))
            else:
                new_bin_str += n.bin
        self.data = BitStream(bin=new_bin_str)

    def as_numpy(self):
        return np.array([n.int for n in self.data.cut(self.number_size)])

    def __repr__(self):
        r = str(self.fitness) + "| "
        for n in self.data.cut(self.number_size):
            r += str(n.int) + ", "
        return r


class Population:

    def __init__(self, size):
        self.size = size
        self.genomes = []

    def select(self):
        ''' return a list of 2-tuples of genomes to be crossed '''
        pass

    def __repr__(self):
        r = ""
        for genome in self.genomes:
            r += repr(genome) + "\n"

        return r
