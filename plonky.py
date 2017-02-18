from __future__ import print_function, division

import os
import sys
import time
from copy import deepcopy
from math import log
import csv
import music21
import numpy as np
from bitstring import BitStream, BitArray

from converter import Metadata, phrase_to_parts, MyChord, measure_to_parts
from fitness import FitnessFunction
from ga import Genome, Population, mutate_and_cross, uint_to_bit_str
from non_blocking_input import NonBlockingInput


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
        baby1 = Measure(self.length, self.number_size)
        baby1.data = self.data[:bit_idx] + other_genome.data[bit_idx:]
        baby2 = Measure(self.length, self.number_size)
        baby2.data = other_genome.data[:bit_idx] + self.data[bit_idx:]
        return baby1, baby2

    @staticmethod
    def reverse(g, population=None):
        for first in range(int(g.length/2)):
            last = g.length - 1 - first
            tmp = g[first]
            g[first] = g[last]
            g[last] = tmp

    @staticmethod
    def rotate(g, population=None):
        Measure._rotate(g, np.random.randint(1, 7))

    @staticmethod
    def _rotate(g, num_rotations):
        for i in range(num_rotations):
            g.data.ror(g.number_size)

    @staticmethod
    def invert(g, population=None):
        for i in range(g.length):
            g[i] = 15 - g[i]

    @staticmethod
    def sort_ascending(g, population=None):
        actual_notes = []
        zeros_and_fifteens = []

        # pull out the 0's and 15's
        for i in range(g.length):
            if g[i] == 0 or g[i] == 15:
                zeros_and_fifteens.append((i, g[i]))
            else:
                actual_notes.append(g[i])

        # sort the real notes
        sorted_notes = sorted(actual_notes)

        # put the 0's and 15's back
        for i, x in zeros_and_fifteens:
            sorted_notes.insert(i, x)

        # copy the values back to g
        for idx in range(g.length):
            g[idx] = sorted_notes[idx]

    @staticmethod
    def sort_descending(g, population=None):
        actual_notes = []
        zeros_and_fifteens = []

        # pull out the 0's and 15's
        for i in range(g.length):
            if g[i] == 0 or g[i] == 15:
                zeros_and_fifteens.append((i, g[i]))
            else:
                actual_notes.append(g[i])

        # sort the real notes
        sorted_notes = sorted(actual_notes, key=lambda n: -n)

        # put the 0's and 15's back
        for i, x in zeros_and_fifteens:
            sorted_notes.insert(i, x)

        # copy the values back to g
        for idx in range(g.length):
            g[idx] = sorted_notes[idx]

    @staticmethod
    def transpose(g):
        signed_steps = np.random.randint(1, 8)

        max_val = 1
        min_val = 14
        for idx in range(g.length):
            if g[idx] == 0 or g[idx] == 15:
                continue
            if g[idx] < min_val:
                min_val = g[idx]
            if g[idx] > max_val:
                max_val = g[idx]

        if (14 - max_val) < (min_val - 1):
            signed_steps = -signed_steps

        Measure._transpose(g, signed_steps)

    @staticmethod
    def _transpose(g, signed_steps):
        for idx in range(g.length):
            if g[idx] == 0 or g[idx] == 15:
                continue
            tmp = g[idx] + signed_steps
            if tmp > 14:
                g[idx] = 14 - (tmp - 14)
            elif tmp < 1:
                g[idx] = 1 + (1 - tmp)
            else:
                g[idx] = tmp

    @staticmethod
    def time_stretch(g):
        # double the length of all notes, cutting off the last half of the measure
        new_g = []
        for i in range(g.length//2):
            new_g.append(g[i])
            new_g.append(15)

        for idx in range(g.length):
            g[idx] = new_g[idx]

    @staticmethod
    def bit_flip(g):
        bit_idx = np.random.randint(g.number_size * g.length)
        Measure._bit_flip(g, bit_idx)

    @staticmethod
    def _bit_flip(g, bit_idx):
        gene_idx = bit_idx // g.length
        gene_bit_idx = bit_idx % g.length
        gene = g[gene_idx]
        a = BitArray(uint=gene, length=g.number_size)
        a._invert(gene_bit_idx)

        g[gene_idx] = a.uint

    @staticmethod
    def mutate(parent1, parent2, baby1, baby2, population):
        mutations = [
            Measure.bit_flip,
            Measure.reverse,
            Measure.rotate,
            Measure.invert,
            Measure.sort_ascending,
            Measure.sort_descending,
            Measure.transpose,
            Measure.time_stretch,
        ]

        # do nothing to parents or baby1.
        # mutate baby2 in one of various ways
        mutation_func = np.random.choice(mutations, 1)[0]
        mutation_func(baby2)


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

    @staticmethod
    def reverse(g, population=None, measure_population=None):
        for first in range(int(g.length/2)):
            last = g.length - 1 - first
            tmp = g[first]
            g[first] = g[last]
            g[last] = tmp

    @staticmethod
    def rotate(g, num_rotations, population=None, measure_population=None):
        Phrase._rotate(g, np.random.randint(1, 7))

    @staticmethod
    def _rotate(g, num_rotations):
        for i in range(num_rotations):
            g.data.ror(g.number_size)

    @staticmethod
    def genetic_repair(g, population, measure_population):
        new_random_measure = np.random.randint(measure_population.size)
        Phrase._genetic_repair(g, new_random_measure)

    @staticmethod
    def _genetic_repair(g, new_measure):
        min_f = sys.maxsize
        min_idx = 0
        for i in range(g.length):
            if g[i] < min_f:
                min_f = g[i]
                min_idx = i

        g[min_idx] = new_measure

    @staticmethod
    def super_phrase(g, population, measure_population):
        new_g = []
        for i in range(g.length):
            # 3 measure tourney
            max_f = -sys.maxint
            max_measure = 0
            for _ in range(3):
                m = np.random.randint(measure_population.size)
                p = measure_population.genomes[m]
                if p.fitness > max_f:
                    max_f = p.fitness
                    max_measure = m

            new_g.append(max_measure)

        for i in range(g.length):
            g[i] = new_g[i]

    @staticmethod
    def lick_thinner(g, population, measure_population):
        new_measure = np.random.randint(measure_population.size)
        Phrase._lick_thinner(g, population, new_measure)

    def _lick_thinner(g, population, new_measure):
        counts = dict((idx, 0) for idx, el in enumerate(g))
        for phrase in population.genomes:
            for m in phrase:
                for i in range(g.length):
                    if g[i] == m:
                        counts[i] += 1
                        continue

        max_count = 0
        max_idx = 0
        for idx, count in counts.items():
            if count > max_count:
                max_count = count
                max_idx = idx

        g[max_idx] = new_measure

    @staticmethod
    def orphan(g, population, measure_population):
        # count how often a measure exists in the phrase population
        counts = dict((i, 0) for i in range(measure_population.size))
        for phrase in population.genomes:
            for measure in phrase:
                counts[measure] += 1

        new_g = []
        for i in range(g.length):
            # random tourney

            min_count = sys.maxsize
            min_m = 0
            for _ in range(3):
                m = np.random.randint(measure_population.size)
                if counts[m] < min_count:
                    min_count = counts[m]
                    min_m = m

            new_g.append(min_m)

        for i in range(g.length):
            g[i] = new_g[i]

    @staticmethod
    def mutate(parent1, parent2, baby1, baby2, population, *args):
        mutations = [
            Phrase.reverse,
            Phrase.rotate,
            Phrase.genetic_repair,
            Phrase.super_phrase,
            Phrase.lick_thinner,
            Phrase.orphan,
        ]

        # do nothing to parents or baby1.
        # mutate baby2 in one of various ways
        mutation_func = np.random.choice(mutations, 1)[0]
        measure_population = args[0]
        mutation_func(baby2, population, measure_population)


class MeasurePopulation(Population):

    def select(self):
        # tournament style
        # assumes population size is multiple of 4

        # in-place shuffle genomes
        np.random.shuffle(self.genomes)
        selected = []

        for i in range(0, self.size - 4, 4):
            # four random possible parents
            possible_parents = sorted(self.genomes[i:i+4], key=lambda g: g.fitness)
            # pick the best two
            parents = possible_parents[2:]
            selected.append(tuple(parents))

        # make sure pop size stays constant
        while len(selected) < self.size/4:
            rand_idx1 = np.random.randint(self.size)
            random_genome1 = self.genomes[rand_idx1]
            rand_idx2 = np.random.randint(self.size)
            random_genome2 = self.genomes[rand_idx2]
            selected.append((random_genome1, random_genome2))

        return selected


class PhrasePopulation(Population):

    def select(self):
        # tournament style
        # assumes population size is multiple of 4

        # in-place shuffle genomes
        np.random.shuffle(self.genomes)
        selected = []

        for i in range(0, self.size - 4, 4):
            # four random possible parents
            possible_parents = sorted(self.genomes[i:i+4], key=lambda g: g.fitness)
            # pick the best two
            parents = possible_parents[2:]
            selected.append(tuple(parents))


        # make sure pop size stays constant
        while len(selected) < self.size/4:
            rand_idx1 = np.random.randint(self.size)
            random_genome1 = self.genomes[rand_idx1]
            rand_idx2 = np.random.randint(self.size)
            random_genome2 = self.genomes[rand_idx2]
            selected.append((random_genome1, random_genome2))

        return selected

    def render_midi(self, measures, metadata, filename):
        population_lead_part = music21.stream.Part()
        population_backing_part = music21.stream.Part()
        population_lead_part.append(music21.instrument.Trumpet())
        population_backing_part.append(music21.instrument.Piano())
        for phrase in self.genomes:
            phrase_lead, phrase_backing = phrase_to_parts(phrase, measures, metadata, accompany=True)
            population_lead_part.append(phrase_lead)
            population_backing_part.append(phrase_backing)
        population_stream = music21.stream.Stream()
        population_stream.append(music21.tempo.MetronomeMark(number=metadata.tempo))
        population_stream.append(population_lead_part.flat)
        population_stream.append(population_backing_part.flat)
        midi_file = music21.midi.translate.streamToMidiFile(population_stream)
        midi_file.open(filename, 'wb')
        midi_file.write()
        midi_file.close()

    def play(self, measures, metadata, best_n_phrases=None):

        if best_n_phrases:
            # sort and pick the best n phrases
            genomes = sorted(self.genomes, key=lambda p: p.fitness)[:best_n_phrases]
        else:
            genomes = self.genomes

        population_lead_part = music21.stream.Part()
        population_backing_part = music21.stream.Part()
        population_lead_part.append(music21.instrument.Trumpet())
        population_backing_part.append(music21.instrument.Piano())
        for phrase in genomes:
            phrase_lead, phrase_backing = phrase_to_parts(phrase, measures, metadata, accompany=True)
            population_lead_part.append(phrase_lead)
            population_backing_part.append(phrase_backing)
        population_stream = music21.stream.Stream()
        population_stream.append(music21.tempo.MetronomeMark(number=metadata.tempo))
        population_stream.append(population_lead_part.flat)
        population_stream.append(population_backing_part.flat)

        sp = music21.midi.realtime.StreamPlayer(population_stream)
        sp.play()


def assign_random_fitness(phrase_pop, measures, metadata):
    phrase_genomes = phrase_pop.genomes
    for pidx, phrase in enumerate(phrase_genomes):
        phrase.fitness += np.random.randint(-2, 2)
        for measure_idx in phrase:
            measures.genomes[measure_idx].fitness += np.random.randint(-2, 2)


def assign_fitness_penalize_jumps(phrase_pop, measures, metadata):
    phrase_genomes = phrase_pop.genomes
    last_note = None
    for pidx, phrase in enumerate(phrase_genomes):
        for measure_idx in phrase:
            measure = measures.genomes[measure_idx]
            for note in measure:
                if 0 < note < 15:
                    if not last_note:
                        last_note = note
                    else:
                        jump_size = last_note - note
                        if jump_size > 3:
                            measure.fitness -= jump_size


def assign_fitness_penalize_rests(phrase_pop, measures, metadata):
    phrase_genomes = phrase_pop.genomes
    rest_on = None
    for pidx, phrase in enumerate(phrase_genomes):
        for measure_idx in phrase:
            measure = measures.genomes[measure_idx]
            for note in measure:
                if note == 0:
                    rest_on = True
                elif 0 < note < 15:
                    rest_on = False

                if rest_on and note == 15:
                    measure.fitness -= 6
                    phrase.fitness -= 2


def manual_fitness(phrase_pop, measures, metadata, nbinput):
    # setup logging
    log = {'phrases': {},
           'measures': {}}

    phrase_genomes = phrase_pop.genomes
    feedback_offset = 2  # in beats
    population_lead_part = music21.stream.Part()
    population_backing_part = music21.stream.Part()
    population_lead_part.append(music21.instrument.Trumpet())
    population_backing_part.append(music21.instrument.Piano())

    for idx, phrase in enumerate(phrase_genomes):
        phrase_lead, phrase_backing = phrase_to_parts(phrase, measures, metadata, accompany=True)
        population_lead_part.append(phrase_lead)
        population_backing_part.append(phrase_backing)

    d = {'raw_count': 0, 'measure_feedback': [], 'phrase_feedback': []}

    def get_feedback(args):
        verbose, _prescalar = args
        # constant variables
        measures_per_phrase = phrase_genomes[0].length
        beats_per_measure = metadata.time_signature.numerator
        beats_per_phrase = beats_per_measure * measures_per_phrase

        # figure out where we are in the stream
        beat_idx = d['raw_count'] // _prescalar

        # move feedback back by a fixed number of beats
        beat_idx = max(0, beat_idx - feedback_offset)

        phrase_idx = beat_idx // beats_per_phrase
        current_phrase = phrase_genomes[phrase_idx]
        measure_idx = (beat_idx % beats_per_phrase) // beats_per_measure
        current_measure = measures.genomes[current_phrase[measure_idx]]

        # Non-Blocking check for input and assign fitness
        i = nbinput.input()
        if i == 'g':
            current_phrase.fitness += 1
            current_measure.fitness += 1
            if verbose:
                print("%s %i %i +1" % (current_phrase, measure_idx, beat_idx))
        elif i == 'b':
            current_phrase.fitness -= 1
            current_measure.fitness -= 1
            if verbose:
                print("%s %i %i -1" % (current_phrase, measure_idx, beat_idx))
        elif i == 's':
            t = time.time()
            filename_p = 'phrases_' + str(metadata) + "_" + str(int(t)) + '.np'
            phrase_pop.save(filename_p)
            filename_m = 'measures_' + str(metadata) + "_" + str(int(t)) + '.np'
            measures.save(filename_m)
            print("saved " + filename_m + " and " + filename_p)
        else:
            if verbose:
                print("%i %i %i" % (phrase_idx, measure_idx, beat_idx))

        d['raw_count'] += 1

        measure_numbers = current_measure.as_numpy()
        phrase_numbers = current_phrase.as_numpy()
        measure_numbers_padded = [str(item).zfill(2) for item in measure_numbers]
        phrase_numbers_padded = [str(item).zfill(2) for item in phrase_numbers]
        measure_hash = ''.join(measure_numbers_padded)
        phrase_hash = ''.join(phrase_numbers_padded)

        if beat_idx % beats_per_measure == 0:
            d['measure_feedback'] = []
        if beat_idx % beats_per_phrase == 0:
            d['phrase_feedback'] = []

        if i == 'g':
            d['measure_feedback'].append((beat_idx % beats_per_measure, 1))
            d['phrase_feedback'].append((measure_idx % measures_per_phrase, 1))
            feedback = True
        elif i == 'b':
            d['measure_feedback'].append((beat_idx % beats_per_measure, -1))
            d['phrase_feedback'].append((measure_idx % measures_per_phrase, -1))
            feedback = True
        else:
            feedback = False

        if feedback:
            if measure_hash not in log['measures']:
                log['measures'][measure_hash] = []
            log['measures'][measure_hash].append(d['measure_feedback'])

            if phrase_hash not in log['phrases']:
                log['phrases'][phrase_hash] = []
            log['phrases'][phrase_hash].append(d['phrase_feedback'])

    prescalar = 8
    wait_ms = metadata.ms_per_beat / prescalar
    population_stream = music21.stream.Stream()
    population_stream.append(music21.tempo.MetronomeMark(number=metadata.tempo))
    population_stream.append(population_lead_part.flat)
    population_stream.append(population_backing_part.flat)
    sp = music21.midi.realtime.StreamPlayer(population_stream)
    sp.play(busyFunction=get_feedback, busyArgs=[False, prescalar], busyWaitMilliseconds=wait_ms)
    # send_stream_to_virtual_midi(metadata.midi_out, phrase_stream, metadata)

    with open('saves/phrase_feedback.csv', 'wb') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in log['phrases'].items():
            writer.writerow([key, value])

    with open('saves/measure_feedback.csv', 'wb') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in log['measures'].items():
            writer.writerow([key, value])


def automatic_fitness(phrases, measures, metadata, ff):
    phrase_genomes = phrases.genomes
    population_stream = music21.stream.Stream()
    population_stream.append(music21.tempo.MetronomeMark(number=metadata.tempo))
    last_note = None
    total_population_fitness = 0
    total_population_length = 0
    iters = 0
    for phrase in phrase_genomes:
        measure_metadata = deepcopy(metadata)

        cumulative_fitness = 0
        cumulative_length = 0
        last_length = 0
        last_fitness = None
        stream_to_evaluate = music21.stream.Stream()
        for measure_idx in phrase:
            iters += 1
            measure = measures.genomes[measure_idx]
            measure_lead_part, _, beat_idx, chord_idx = measure_to_parts(measure, measure_metadata)
            stream_to_evaluate.append(measure_lead_part)

            measure_metadata.chords = measure_metadata.chords[chord_idx:]
            if len(measure_metadata.chords) == 0:
                measure_metadata.chords = deepcopy(metadata.chords)
            measure_metadata.chords[0].beats -= beat_idx

            mf = music21.midi.translate.streamToMidiFile(stream_to_evaluate.flat)
            tmp_midi_name = '.tmp.mid'
            mf.open(tmp_midi_name, 'wb')
            mf.write()
            mf.close()
            cumulative_fitness, cumulative_length = ff.evaluate_fitness(tmp_midi_name)

            # TODO: this is a workaround for a bug and should be removed eventually
            if cumulative_fitness is None:
                sys.exit("No Fitness Returned")
            else:
                cumulative_fitness = int(cumulative_fitness)

            # compute change in fitness caused by the new measure
            delta_length = cumulative_length - last_length
            if last_fitness:
                delta_fitness = cumulative_fitness - last_fitness
            else:
                delta_fitness = cumulative_fitness

            if delta_length == 0:
                # emergency repair! empty measure!
                print("Emergency repair on empty measure:", measure)
                measure.initialize()
            else:

                last_fitness = cumulative_fitness
                last_length = cumulative_length
                # TODO: should be delta_fitness not cumulative_fitness
                scaled_fitness = int(10 * cumulative_fitness)
                measure.fitness = scaled_fitness
                phrase.fitness = scaled_fitness
                # print("%i out of %i" % (iters, phrases.size * phrase_genomes[0].length))

                # add penalty for empty bars
                empty = True
                for note in measure:
                    if 0 < note < 15:
                        empty = False
                if empty:
                    measure.fitness -= 100

                # penalty for too many 16th notes
                # for note in measure:
                #     if last_note:
                #         if (0 < note < 15) and (0 < last_note < 15):
                #             measure.fitness -= 10
                #     last_note = note

        total_population_fitness += cumulative_fitness
        total_population_length += cumulative_length

    print('fitness:', total_population_fitness, ' length:', total_population_length)


def main():
    if '--debug' in sys.argv:
        print("waiting 10 seconds so you can attach a debugger...")
        time.sleep(10)

    measure_pop_size = 512
    smallest_note = 16
    # one measure of each chord for 4 beats each
    chords = [MyChord('E3', 4, 'min7', [0, 3, 7, 14]),
              MyChord('G3', 4, 'maj7', [0, 4, 7, 10]),
              MyChord('D3', 4, 'maj7', [0, 4, 7, 14]),
              MyChord('D3', 4, 'maj7', [0, 4, 7, 14]),
              MyChord('E3', 4, 'min7', [0, 3, 7, 14]),
              MyChord('G3', 4, 'maj7', [0, 4, 7, 10]),
              MyChord('D3', 4, 'maj7', [0, 4, 7, 14]),
              MyChord('D3', 4, 'maj7', [0, 4, 7, 14]),
              ]

    metadata = Metadata('C', chords, '4/4', 140, smallest_note, 80)
    measures_per_phrase = 8

    phrase_genome_len = log(measure_pop_size, 2)
    if not phrase_genome_len.is_integer():
        sys.exit("Measure pop size must be power of 2. %i is not." % measure_pop_size)
    phrase_genome_len = int(phrase_genome_len)

    measures = MeasurePopulation(measure_pop_size)
    for itr in range(measures.size):
        m = Measure(length=metadata.notes_per_measure, number_size=4)
        m.initialize()
        measures.genomes.append(m)

    phrases = PhrasePopulation(64)
    for itr in range(phrases.size):
        p = Phrase(length=measures_per_phrase, number_size=phrase_genome_len)
        p.initialize()
        phrases.genomes.append(p)

    if '--resume' in sys.argv:
        print("Loading measure & phrase populations from files")
        measures.load('measures.np')
        phrases.load('phrases.np')

    if '--play' in sys.argv:
        print("playing generation")
        phrases.play(measures, metadata, best_n_phrases=8)
        return
    elif '--render' in sys.argv:
        print("rendering generation")
        if os.path.exists('output.mid'):
            if raw_input("overwrite output.mid? [y/n]") == 'y':
                phrases.render_midi(measures, metadata, 'output.mid')
                return
            else:
                print("Ignoring.")
                return
        else:
            phrases.render_midi(measures, metadata, 'output.mid')
            return

    if '--manual' in sys.argv:
        manual = True
        ff = None
        print("Using manual fitness function")
        nbinput = NonBlockingInput()
        metadata.backing_velocity = 10
    else:
        manual = False
        nbinput = None
        ff = FitnessFunction()
        print("Using automatic fitness function")

    num_generations = 100
    if '--generations' in sys.argv:
        _pos = sys.argv.index('--generations')
        num_generations = int(sys.argv[_pos + 1])

    print("Running " + str(num_generations) + " generations.")
    last_time = time.time()
    t0 = last_time
    for itr in range(num_generations):

        measures.save('in_progress_measures.np')
        phrases.save('in_progress_phrases.np')

        # assign fitness
        if manual:
            manual_fitness(phrases, measures, metadata, nbinput)
        else:
            automatic_fitness(phrases, measures, metadata, ff)

        # do mutation on measures
        measures = mutate_and_cross(measures, Measure.mutate)
        phrases = mutate_and_cross(phrases, Phrase.mutate, measures, metadata, ff)

        # TODO: Initialize fitness of new measure to the mean of the not-new measures?

        measures.save('measures.np')
        phrases.save('phrases.np')
        t_now = time.time()
        print("Generation %i completed in %3.3f seconds." % (itr, t_now - last_time))
        last_time = t_now

    t1 = time.time()
    print("Training Time:", t1 - t0)
    print("Done. (hit any key to exit)")

if __name__ == '__main__':
    main()
