import sys
from bitstring import BitStream, CreationError
from copy import deepcopy
import numpy as np


def uint_to_bit_str(value, num_bits):
    try:
        return BitStream(length=num_bits, uint=value).bin
    except CreationError as ce:
        sys.exit('%i is out of the range of %i unsigned bits'
                 % (value, num_bits))


def int_to_bit_str(value, num_bits):
    try:
        return BitStream(length=num_bits, int=value).bin
    except CreationError as ce:
        sys.exit('%i is out of the range of %i signed bits'
                 % (value, num_bits))


def run(current_population, mutate_method, fitness_method, *args):
    if fitness_method:
        fitness_method(current_population, *args)

    selected_genomes = current_population.select()
    unmodified_population = deepcopy(current_population)
    new_genomes = []
    for i, pair in enumerate(selected_genomes):
        g1, g2 = pair
        baby1, baby2 = g1.cross(g2)
        new_genomes += [baby1, baby2, g1, g2]

        if mutate_method:
            mutate_method(g1, g2, baby1, baby2, unmodified_population, *args)
    current_population.genomes = new_genomes

    return current_population


class Genome:

    def __init__(self, length, number_size, signed=False):
        self.number_size = number_size
        self.length = length
        self.data = BitStream()
        self.fitness = 0
        self.signed = signed
        self.id = 0

    def cross(self, other_genome):
        raise NotImplementedError()

    def initialize(self):
        raise NotImplementedError()

    def __getitem__(self, idx):
        ''' get idx'th number genome as integer '''
        as_list = [n for n in self.data.cut(self.number_size)]
        if isinstance(idx, slice):
            if self.signed:
                return [n.int for n in as_list[idx]]
            else:
                return [n.uint for n in as_list[idx]]
        elif isinstance(idx, int):
            if self.signed:
                return as_list[idx].int
            else:
                return as_list[idx].uint
        else:
            raise TypeError("ya fucked up")

    def __setitem__(self, idx, value):
        ''' set idx'th number genome as integer '''
        new_bin_str = ''
        for i, n in enumerate(self.data.cut(self.number_size)):
            if i == idx:
                if self.signed:
                    new_bin_str += int_to_bit_str(value, self.number_size)
                else:
                    new_bin_str += uint_to_bit_str(value, self.number_size)
            else:
                new_bin_str += n.bin
        self.data = BitStream(bin=new_bin_str)

    def as_numpy(self):
        if self.signed:
            return np.array([n.int for n in self.data.cut(self.number_size)])
        else:
            return np.array([n.uint for n in self.data.cut(self.number_size)])

    def __repr__(self):
        r = str(self.fitness) + "| "
        for n in self.data.cut(self.number_size):
            if self.signed:
                r += str(n.int) + ", "
            else:
                r += str(n.uint) + ", "
        return r


class Population:

    def __init__(self, size):
        self.size = size
        self.genomes = []

    def select(self):
        ''' return a list of 2-tuples of genomes to be crossed '''
        raise NotImplemented()

    def save(self, filename):
        # save to file using numpy
        genome_arr = []
        for g in self.genomes:
            genome_arr.append(g.as_numpy())
        nparr = np.array(genome_arr)
        np.savetxt(open(filename, 'wb'), nparr, fmt='%10d')

    def __repr__(self):
        r = ""
        for genome in self.genomes:
            r += repr(genome) + "\n"

        return r
