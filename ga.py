import numpy as np


def run(max_iters, initial_population, mutate_method, assign_fitness):
    current_population = initial_population

    iter = 0

    while iter < max_iters:

        for genome in current_population.genomes:
            assign_fitness(genome)
        print(current_population)

        selected_genomes = current_population.select()
        new_genomes = []
        for i, pair in enumerate(selected_genomes):
            g1, g2 = pair
            baby1, baby2 = g1.cross(g2)
            new_genomes += [baby1, baby2, g1, g2]

            mutate_method(g1, g2, baby1, baby2)
        current_population.genomes = new_genomes
        iter += 1


class Genome:

    def __init__(self, size):
        self.size = size
        self.data = np.ndarray(size)
        self.fitness = 0
        self.id = 0

    def cross(self, other_genome):
        pass

    def initialize(self):
        pass

    def __repr__(self):
        r = str(self.fitness) + "| "
        for n in self.data:
            r += str(n) + ", "

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
