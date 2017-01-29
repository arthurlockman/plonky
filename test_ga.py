import numpy as np
import sys
from ga import Genome, Population, run


class NumberGenome(Genome):

    def __init__(self):
        super().__init__(4)

    def initialize(self):
        for i in range(self.size):
            self.data[i] = np.random.randint(-10, 10)

    def cross(self, other_genome):
        idx = np.random.randint(1, self.size)
        baby1 = NumberGenome()
        baby1.data = np.concatenate((self.data[:idx], other_genome.data[idx:]))
        baby2 = NumberGenome()
        baby2.data = np.concatenate((other_genome.data[:idx], self.data[idx:]))
        return baby1, baby2


class NumberPopulation(Population):

    def __init__(self):
        super().__init__(12)

    def select(self):
        sorted_data = sorted(self.genomes, key=lambda g: -abs(g.fitness))
        selected = []
        for idx in range(self.size//2, self.size - 1, 2):
            parent1 = sorted_data[idx]
            parent2 = sorted_data[idx + 1]
            selected.append((parent1, parent2))

        return selected


def mutate(parent1, parent2, baby1, baby2):
    for g in [parent1, parent2, baby1, baby2]:
        if not isinstance(g, NumberGenome):
            sys.exit("This mutation only works on NumberGenomes, not %s" % str(type(g)))

        if np.random.rand() < 0.10:
            idx = np.random.randint(0, g.size)
            g.data[idx] += 1
        if np.random.rand() < 0.20:
            idx = np.random.randint(0, g.size)
            g.data[idx] -= 1


def fitness(genome):
    if not isinstance(genome, NumberGenome):
        sys.exit("This fitness only works on NumberGenomes")

    genome.fitness = sum(genome.data)

if __name__ == '__main__':
    pop = NumberPopulation()
    for i in range(pop.size):
        g = NumberGenome()
        g.initialize()
        pop.genomes.append(g)

    run(10, pop, mutate_method=mutate, assign_fitness=fitness)

