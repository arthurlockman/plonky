from bitstring import BitStream
import numpy as np
import sys
from ga import Genome, Population, run


class NumberGenome(Genome):

    def __init__(self, number_size):
        super().__init__(length=6, number_size=number_size, signed=True)

    def initialize(self):
        num_bits = self.number_size * self.length
        self.data = BitStream(bin=''.join([np.random.choice(('0', '1')) for _ in range(num_bits)]))

    def cross(self, other_genome):
        bit_idx = np.random.randint(1, self.length * self.number_size)
        baby1 = NumberGenome(self.number_size)
        baby1.data = self.data[:bit_idx] + other_genome.data[bit_idx:]
        baby2 = NumberGenome(self.number_size)
        baby2.data = other_genome.data[:bit_idx] + self.data[bit_idx:]
        return baby1, baby2

    def assign_fitness(self):
        self.fitness = sum(self.as_numpy())

    @staticmethod
    def mutate(parent1, parent2, baby1, baby2, population):
        for g in [parent1, parent2, baby1, baby2]:
            if np.random.rand() < 0.40:
                idx = np.random.randint(0, g.length)
                if g[idx] < g.MAX_INT:
                    g[idx] += 1
            if np.random.rand() < 0.80:
                idx = np.random.randint(0, g.length)
                if g[idx] > g.MIN_INT:
                    g[idx] -= 1


class NumberPopulation(Population):

    def select(self):
        sorted_data = sorted(self.genomes, key=lambda g: -abs(g.fitness))
        selected = []
        for idx in range(self.size//2, self.size - 1, 2):
            parent1 = sorted_data[idx]
            parent2 = sorted_data[idx + 1]
            selected.append((parent1, parent2))

        return selected

if __name__ == '__main__':
    S = 20
    pop = NumberPopulation(size=S)
    for i in range(pop.size):
        g = NumberGenome(number_size=7)
        g.initialize()
        pop.genomes.append(g)

    N = 20
    for i in range(N):
        pop = run(pop, mutate_method=NumberGenome.mutate)
        if i == 0 or i == N - 1:
            print(pop)

