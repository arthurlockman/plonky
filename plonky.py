from __future__ import print_function, division

import os
import sys
import time
from math import log
import csv
import music21
import numpy as np
from bitstring import BitStream, BitArray

from converter import *
from improv_fitness import FitnessFunction
from ga import Genome, Population, mutate_and_cross, uint_to_bit_str
from non_blocking_input import NonBlockingInput


class Measure(Genome):

    def initialize(self):
        """ non random initialization, where jumps between sequential notes are bounded """
        bit_str = ''
        last_note = None
        for _ in range(self.length):
            e = np.random.rand()
            if e < 0.2:
                # rest
                bit_str += uint_to_bit_str(value=0, num_bits=NOTE_BITS)
            elif e < 0.4:
                # hold/sustain
                bit_str += uint_to_bit_str(value=SUSTAIN, num_bits=NOTE_BITS)
            else:
                # new note
                if last_note:
                    while True:
                        new_note_pitch = last_note + np.random.randint(-3, 4)
                        if 0 < new_note_pitch < SUSTAIN:
                            break
                else:
                    new_note_pitch = np.random.randint(1, SUSTAIN)
                last_note = new_note_pitch
                bit_str += uint_to_bit_str(new_note_pitch, self.number_size)

        self.data = BitStream(bin=bit_str)

    def _old_rand_initialize(self):
        bit_str = ''
        for _ in range(self.length):
            e = np.random.rand()
            if e < 0.2:
                # rest
                bit_str += uint_to_bit_str(value=0, num_bits=NOTE_BITS)
            elif e < 0.4:
                # hold
                bit_str += uint_to_bit_str(value=SUSTAIN, num_bits=NOTE_BITS)
            else:
                # new note
                new_note_pitch = np.random.randint(1, SUSTAIN)
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
            g[i] = SUSTAIN - g[i]

    @staticmethod
    def sort_ascending(g, population=None):
        actual_notes = []
        zeros_and_fifteens = []

        # pull out the 0's and SUSTAIN's
        for i in range(g.length):
            if g[i] == 0 or g[i] == SUSTAIN:
                zeros_and_fifteens.append((i, g[i]))
            else:
                actual_notes.append(g[i])

        # sort the real notes
        sorted_notes = sorted(actual_notes)

        # put the 0's and SUSTAIN's back
        for i, x in zeros_and_fifteens:
            sorted_notes.insert(i, x)

        # copy the values back to g
        for idx in range(g.length):
            g[idx] = sorted_notes[idx]

    @staticmethod
    def sort_descending(g, population=None):
        actual_notes = []
        zeros_and_fifteens = []

        # pull out the 0's and SUSTAIN's
        for i in range(g.length):
            if g[i] == 0 or g[i] == SUSTAIN:
                zeros_and_fifteens.append((i, g[i]))
            else:
                actual_notes.append(g[i])

        # sort the real notes
        sorted_notes = sorted(actual_notes, key=lambda n: -n)

        # put the 0's and SUSTAIN's back
        for i, x in zeros_and_fifteens:
            sorted_notes.insert(i, x)

        # copy the values back to g
        for idx in range(g.length):
            g[idx] = sorted_notes[idx]

    @staticmethod
    def transpose(g):
        signed_steps = np.random.randint(1, 8)

        max_val = 1
        min_val = MAX_NOTE
        for idx in range(g.length):
            if g[idx] == 0 or g[idx] == SUSTAIN:
                continue
            if g[idx] < min_val:
                min_val = g[idx]
            if g[idx] > max_val:
                max_val = g[idx]

        if (MAX_NOTE - max_val) < (min_val - 1):
            signed_steps = -signed_steps

        Measure._transpose(g, signed_steps)

    @staticmethod
    def _transpose(g, signed_steps):
        for idx in range(g.length):
            if g[idx] == 0 or g[idx] == SUSTAIN:
                continue
            tmp = g[idx] + signed_steps
            if tmp > MAX_NOTE:
                g[idx] = MAX_NOTE - (tmp - MAX_NOTE)
            elif tmp < 1:
                g[idx] = 1 + (1 - tmp)
            else:
                g[idx] = tmp

    @staticmethod
    def end_time_stretch(g):
        # double the length of all notes, cutting off the first half of the measure
        new_g = []
        for i in range(g.length//2, g.length):
            new_g.append(g[i])
            new_g.append(SUSTAIN)

        for idx in range(g.length):
            g[idx] = new_g[idx]

    @staticmethod
    def time_stretch(g):
        # double the length of all notes, cutting off the last half of the measure
        new_g = []
        for i in range(g.length//2):
            new_g.append(g[i])
            new_g.append(SUSTAIN)

        for idx in range(g.length):
            g[idx] = new_g[idx]

    @staticmethod
    def bit_flip(g):
        bit_idx = np.random.randint(0, g.number_size * g.length)
        Measure._bit_flip(g, bit_idx)

    @staticmethod
    def _bit_flip(g, bit_idx):
        gene_idx = bit_idx // g.number_size
        gene_bit_idx = bit_idx % g.number_size
        gene = g[gene_idx]
        a = BitArray(uint=gene, length=g.number_size)
        a._invert(gene_bit_idx)

        g[gene_idx] = a.uint

    @staticmethod
    def fill(g):
        last_note = None
        for idx, note in enumerate(g):
            if 0 < note < SUSTAIN:
                last_note = note
            if note == SUSTAIN:
                if last_note:
                    if np.random.rand() < 0.5:
                        g[idx] = last_note + 1
                    else:
                        g[idx] = last_note - 1
                else:
                    g[idx] = np.random.randint(0, SUSTAIN)

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
            # Measure.time_stretch,
            # Measure.end_time_stretch,
            # Measure.fill,
        ]

        # do nothing to parents or baby1.
        # mutate baby2 in one of various ways
        if np.random.rand() < 0.5:
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
    def bit_flip(g, population=None, measure_population=None):
        bit_idx = np.random.randint(0, g.number_size * g.length)
        Phrase._bit_flip(g, bit_idx)

    @staticmethod
    def _bit_flip(g, bit_idx):
        gene_idx = bit_idx // g.number_size
        gene_bit_idx = bit_idx % g.number_size
        gene = g[gene_idx]
        a = BitArray(uint=gene, length=g.number_size)
        a._invert(gene_bit_idx)

        g[gene_idx] = a.uint

    @staticmethod
    def mutate(parent1, parent2, baby1, baby2, population, *args):
        mutations = [
            Phrase.bit_flip,
            Phrase.reverse,
            Phrase.rotate,
            Phrase.genetic_repair,
            Phrase.super_phrase,
            Phrase.lick_thinner,
            Phrase.orphan,
        ]

        # do nothing to parents or baby1.
        # mutate baby2 in one of various ways
        if np.random.rand() < 0.5:
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

    def render_midi(self, measures, metadata, filename, best_n_phrases=None):
        if best_n_phrases:
            # sort and pick the best n phrases
            genomes = sorted(self.genomes, key=lambda p: p.fitness)[:best_n_phrases]
        else:
            genomes = sorted(self.genomes, key=lambda p: p.fitness)

        population_stream = create_stream(genomes, measures, metadata)
        midi_file = music21.midi.translate.streamToMidiFile(population_stream)
        midi_file.open(filename, 'wb')
        midi_file.write()
        midi_file.close()

    def play(self, measures, metadata, best_n_phrases=None):

        if best_n_phrases:
            # sort and pick the best n phrases
            genomes = sorted(self.genomes, key=lambda p: p.fitness)[:best_n_phrases]
        else:
            genomes = sorted(self.genomes, key=lambda p: p.fitness)

        population_stream = create_stream(genomes, measures, metadata)
        sp = music21.midi.realtime.StreamPlayer(population_stream)
        sp.play()


def assign_random_fitness(phrase_pop, measures, metadata):
    phrase_genomes = phrase_pop.genomes
    for pidx, phrase in enumerate(phrase_genomes):
        phrase.fitness += np.random.randint(-2, 2)
        for measure_idx in phrase:
            measures.genomes[measure_idx].fitness += np.random.randint(-2, 2)


def assign_fitness_reward_notes(phrase_pop, measures, metadata):
    phrase_genomes = phrase_pop.genomes
    for phrase in phrase_genomes:
        for measure_idx in phrase:
            measure = measures.genomes[measure_idx]
            for note in measure:
                if 0 < note < SUSTAIN:
                    measure.fitness += 1
                    phrase.fitness += 1


def assign_fitness_penalize_jumps(phrase_pop, measures, metadata):
    phrase_genomes = phrase_pop.genomes
    sum_jumps = 0
    for phrase in phrase_genomes:
        last_note = None
        for measure_idx in phrase:
            measure = measures.genomes[measure_idx]
            for note in measure:
                if 0 < note < SUSTAIN:
                    if last_note:
                        jump_size = last_note - note
                        sum_jumps += abs(jump_size)
                        if jump_size > 2:
                            measure.fitness -= 4
                            phrase.fitness -= 4
                    last_note = note

    return sum_jumps


def assign_fitness_penalize_rests(phrase_pop, measures, metadata):
    phrase_genomes = phrase_pop.genomes
    rest_on = None
    for pidx, phrase in enumerate(phrase_genomes):
        for measure_idx in phrase:
            measure = measures.genomes[measure_idx]
            for note in measure:
                if note == 0:
                    rest_on = True
                elif 0 < note < SUSTAIN:
                    rest_on = False

                if rest_on and note == SUSTAIN:
                    measure.fitness -= 6
                    phrase.fitness -= 2


def manual_fitness(phrases, measures, metadata, nbinput):
    # setup logging
    feedback_log = {'phrases': {}, 'measures': {}}

    phrase_genomes = phrases.genomes
    feedback_offset = 3  # in beats

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

        # we might reach the end of the phrase in this callback
        # so just stop if we do
        if phrase_idx >= len(phrase_genomes):
            return

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
            phrases.save(filename_p)
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
            if measure_hash not in feedback_log['measures']:
                feedback_log['measures'][measure_hash] = []
            feedback_log['measures'][measure_hash].append(d['measure_feedback'])

            if phrase_hash not in feedback_log['phrases']:
                feedback_log['phrases'][phrase_hash] = []
            feedback_log['phrases'][phrase_hash].append(d['phrase_feedback'])

    prescalar = 8
    wait_ms = metadata.ms_per_beat / prescalar

    population_stream = create_stream(phrase_genomes, measures, metadata)
    sp = music21.midi.realtime.StreamPlayer(population_stream)
    sp.play(busyFunction=get_feedback, busyArgs=[False, prescalar], busyWaitMilliseconds=wait_ms)

    with open('saves/phrase_feedback.csv', 'wb') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in feedback_log['phrases'].items():
            writer.writerow([key, value])

    with open('saves/measure_feedback.csv', 'wb') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in feedback_log['measures'].items():
            writer.writerow([key, value])


def automatic_fitness(phrases, measures, metadata, ff):
    phrase_genomes = phrases.genomes
    total_phrase_fitness = 0
    total_measure_fitness = 0

    for phrase in phrase_genomes:
        phrase.fitness = 0  # reset fitness
        last_note = None
        cumulative_fitness = 0
        last_fitness = None
        melody = []
        chord_idx = 0
        beat_idx = 1

        for measure_idx in phrase:
            measure = measures.genomes[measure_idx]
            measure.fitness = 0  # reset fitness

            idx = 1
            silent = True
            for note in measure:
                # figure out the current chord
                current_chord_info = metadata.chords[chord_idx]
                note_chord_offsets = chord_shapes[current_chord_info.shape]['offsets']
                tonic_midi = music21.pitch.Pitch(current_chord_info.root).midi

                if note == 0:  # rest
                    melody += ([-1] * metadata.events_per_note)
                elif note == SUSTAIN:  # sustain
                    melody += ([-2] * metadata.events_per_note)
                else:
                    silent = False
                    new_pitch = tonic_midi + note_chord_offsets[note - 1]
                    melody += ([new_pitch] * metadata.events_per_note)

                if idx == metadata.notes_per_beat:
                    beat_idx += 1
                    idx = 0
                if beat_idx > current_chord_info.beats:
                    beat_idx = 1
                    chord_idx += 1

                idx += 1

            if silent:
                measure.fitness = -100
                continue

            # get fitness from RNN and cast to integer
            cumulative_fitness, _ = ff.evaluate_fitness(melody_as_array=melody)
            cumulative_fitness = int(cumulative_fitness)

            # compute change in fitness caused by the new measure
            if last_fitness:
                delta_fitness = cumulative_fitness - last_fitness
            else:
                delta_fitness = cumulative_fitness

            last_fitness = cumulative_fitness
            measure.fitness = delta_fitness

            for note in measure:
                if 0 < note < SUSTAIN:
                    if last_note:
                        jump_size = last_note - note
                        if jump_size == 0:
                            measure.fitness -= 2
                        if jump_size > 7:
                            measure.fitness -= 4 * jump_size
                            phrase.fitness -= 4 * jump_size
                    last_note = note

            total_measure_fitness += measure.fitness

        phrase.fitness = cumulative_fitness
        total_phrase_fitness += phrase.fitness

    print('phrase fitness:', total_phrase_fitness, 'measure fitness:', total_measure_fitness)
    return total_phrase_fitness + total_measure_fitness


def main():
    if '--debug' in sys.argv:
        print("waiting 10 seconds so you can attach a debugger...")
        time.sleep(10)

    measure_pop_size = 32
    smallest_note = 8
    # one measure of each chord for 4 beats each
    chords = [MyChord('C3', 8, 'maj7'),
              MyChord('F3', 4, 'min7'),
              MyChord('B-3', 4, 'maj7'),
              MyChord('C3', 8, 'maj7'),
              MyChord('B-3', 4, 'min7'),
              MyChord('E-3', 4, 'maj7'),
              MyChord('A-3', 8, 'maj7'),
              MyChord('A3', 4, 'min7'),
              MyChord('D3', 4, 'maj7'),
              MyChord('D3', 4, 'min7'),
              MyChord('G3', 4, 'maj7'),
              MyChord('C3', 2, 'maj7'),
              MyChord('E-3', 2, 'maj7'),
              MyChord('A-3', 2, 'maj7'),
              MyChord('D-3', 2, 'maj7'),
              ]

    metadata = Metadata('C', chords, '4/4', 140, smallest_note, 60)
    measures_per_phrase = 16

    phrase_genome_len = log(measure_pop_size, 2)
    if not phrase_genome_len.is_integer():
        sys.exit("Measure pop size must be power of 2. %i is not." % measure_pop_size)
    phrase_genome_len = int(phrase_genome_len)

    measures = MeasurePopulation(measure_pop_size)
    for itr in range(measures.size):
        m = Measure(length=metadata.notes_per_measure, number_size=NOTE_BITS)
        m.initialize()
        measures.genomes.append(m)

    phrases = PhrasePopulation(24)
    for itr in range(phrases.size):
        p = Phrase(length=measures_per_phrase, number_size=phrase_genome_len)
        p.initialize()
        phrases.genomes.append(p)

    start_gen = 0
    if '--resume' in sys.argv:
        gen_idx = sys.argv.index('--resume') + 1
        gen_num = sys.argv[gen_idx]
        print("Loading measure & phrase population " + gen_num + " from files")
        measures.load('measures_' + gen_num + '.np')
        phrases.load('phrases_' + gen_num + '.np')
        start_gen = int(gen_num) + 1
    if '--manual' in sys.argv:
        manual = True
        ff = None
        print("Using manual fitness function")
        nbinput = NonBlockingInput()
        metadata.backing_velocity = 4
    else:
        manual = False
        nbinput = None
        ff = FitnessFunction(chords)
        print("Using automatic fitness function")

    if '--backing' in sys.argv:
        _backing_filename_idx = sys.argv.index('--backing') + 1
        backing_filename = sys.argv[_backing_filename_idx]
        if not os.path.exists(backing_filename):
            sys.exit(backing_filename + " not found.")
        metadata.backing_stream = music21.converter.parse(backing_filename)
        set_stream_velocity(metadata.backing_stream, metadata.backing_velocity)
    else:
        metadata.backing_stream = None

    if '--play' in sys.argv:
        metadata.backing_velocity = 4
        if metadata.backing_stream:
            set_stream_velocity(metadata.backing_stream, metadata.backing_velocity)
        print("playing generation")
        phrases.play(measures, metadata)
        return
    elif '--render' in sys.argv:
        _pos = sys.argv.index('--render')
        filename = sys.argv[_pos + 1]
        print("rendering generation")
        if os.path.exists(filename):
            if raw_input("overwrite " + filename + "? [y/n]") == 'y':
                phrases.render_midi(measures, metadata, filename)
                return
            else:
                print("Ignoring.")
                return
        else:
            phrases.render_midi(measures, metadata, filename)
            return

    if '--always_render' in sys.argv:
        always_render = True
    else:
        always_render = False

    num_generations = 15
    if '--generations' in sys.argv:
        _pos = sys.argv.index('--generations')
        num_generations = int(sys.argv[_pos + 1])

    print("Running " + str(num_generations) + " generations.")
    last_time = time.time()
    t0 = last_time
    max_f = -sys.maxsize
    for itr in range(start_gen, start_gen + num_generations):

        # assign fitness
        if manual:
            manual_fitness(phrases, measures, metadata, nbinput)
        else:
            f = automatic_fitness(phrases, measures, metadata, ff)
            if f > max_f:
                max_f = f
                print('next best gen is ', itr)

        # save progress
        measures.save('measures_%i.np' % itr)
        phrases.save('phrases_%i.np' % itr)
        if always_render:
            print("Rendering gen_%i.mid" % itr)
            phrases.render_midi(measures, metadata, 'gen_%i.mid' % itr, best_n_phrases=1)

        # do mutation on measures
        measures = mutate_and_cross(measures, Measure.mutate)
        phrases = mutate_and_cross(phrases, Phrase.mutate, measures, metadata, ff)

        # TODO: Initialize fitness of new measure to the mean of the not-new measures?
        t_now = time.time()
        print("Generation %i completed in %3.3f seconds." % (itr, t_now - last_time))
        last_time = t_now

    t1 = time.time()
    print("Training Time:", t1 - t0)
    print("Done. (hit any key to exit)")

if __name__ == '__main__':
    main()
