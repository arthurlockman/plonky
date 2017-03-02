from __future__ import print_function, division

import matplotlib.pyplot as plt
import numpy as np
import music21
import improv_fitness
from converter import MyChord

roots = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
shapes = ['maj7', 'min7', 'maj', 'min', 'dim']

# real jazz vs random melody + random chords
if 0:
    tonic_fitness = []
    print("Just the tonic")
    for _ in range(7):
        melody = []
        raw_chords = []
        l = np.random.randint(100, 400)
        for i in range(l):
            chord_idx = np.random.randint(0, len(roots))
            chord = roots[chord_idx]
            melody.append(60 + chord_idx)
            raw_chords.append(chord)

        ff = improv_fitness.FitnessFunction(raw_chords=raw_chords)
        f, l = ff.evaluate_fitness(melody)
        print("%3.3f" % (f/l))
        tonic_fitness.append(f / l)


    random_fitness = []
    print("random notes")
    for _ in range(7):
        melody = []
        raw_chords = []
        l = np.random.randint(20, 200)
        for i in range(l):
            melody += [np.random.randint(0, 127)] * 4
            chord = np.random.choice(roots) + np.random.choice(shapes)
            raw_chords += [chord] * 4

        ff = improv_fitness.FitnessFunction(raw_chords=raw_chords)
        f, l = ff.evaluate_fitness(melody)
        print("%3.3f" % (f/l))
        random_fitness.append(f / l)

    jazz_fitness = []
    real_jazz = {
        'DonByas_HarvardBlues-1_FINAL.mid':
            ['Db7']*16 +
            ['Db7']*16 +
            ['Gb7']*8 + ['Go']*8 +
            ['Db']*8 + ['Db7']*8 +
            ['Bb-7']*8 + ['Db7']*8 +
            ['Gb7']*16 +
            ['Gb7']*8 + ['Go']*8 +
            ['Db7']*16 +
            ['Db7']*8 + ['Ao']*8 +
            ['Ab7']*16 +
            ['Gb7']*16 +
            ['Db7']*16 +
            ['Db7']*16,
        'BixBeiderbecke_Margie_FINAL.mid':
            ['Eb'] * 16 * 3 +
            ['Eb7'] * 16 +
            ['Ab'] * 16 * 2 +
            ['G7'] * 16 * 2 +
            ['Eb'] * 16 * 2 +
            ['Eb'] * 4 + ['Eb7'] * 4 + ['D7'] * 4 + ['Db7'] * 4  +
            ['C7'] * 16 +
            ['F-7'] * 16 +
            ['Bb7'] * 16 +
            ['Eb'] * 16,
        'BixBeiderbecke_RoyalGardenBlues_FINAL.mid':
            ['Bb'] * 16 +
            ['Bb'] * 16 +
            ['Bb'] * 16 +
            ['Bb'] * 16 +
            ['Eb'] * 16 +
            ['Eb'] * 16 +
            ['Bb'] * 16 +
            ['G7'] * 16 +
            ['C-7'] * 16 +
            ['F7'] * 16 +
            ['Bb'] * 16 +
            ['Bb'] * 16 +
            ['Bb'] * 16,
        'KidOry_MuskratRamble_FINAL.mid':
            ['Ab'] * 16 +
            ['Ab'] * 16 +
            ['Ab'] * 8 + ['Abo'] * 8 +
            ['Eb7'] * 16 +
            ['Eb7'] * 16 +
            ['Ab'] * 16 +
            ['Ab'] * 16 +
            ['Bb7'] * 16 +
            ['Eb7'] * 16 +
            ['Ab'] * 16 +
            ['Ab'] * 16 +
            ['F7'] * 16 +
            ['Bb-'] * 16 +
            ['Bb7'] * 8 + ['Eb7'] * 8 +
            ['Ab'] * 16,
        'KidOry_GutBucketBlues_FINAL.mid':
           ['C'] * 16 +
           ['F'] * 16 +
           ['C'] * 16 +
           ['C'] * 16 +
           ['F'] * 16 +
           ['F'] * 16 +
           ['C'] * 16 +
           ['C'] * 16 +
           ['G7'] * 16 +
           ['F'] * 16 +
           ['C'] * 16 +
           ['C'] * 16,
        'LouisArmstrong_CornetChopSuey_FINAL.mid':
           ['F'] * 16 +
           ['F'] * 16 +
           ['F'] * 16 +
           ['C7'] * 16 +
           ['F'] * 16 +
           ['Bb'] * 8 + ['Bb-'] * 8 +
           ['F'] * 16 +
           ['G7'] * 4 + ['C7'] * 4 + ['F'] * 8 +
           ['F'] * 16 +
           ['F'] * 16 +
           ['F'] * 16 +
           ['C7'] * 16 +
           ['F'] * 16 +
           ['Bb'] * 16 + ['Bb-'] * 16 +
           ['F'] * 16 +
           ['G7'] * 4 + ['C7'] * 4 + ['F'] * 8,
        'LouisArmstrong_GutBucketBlues_FINAL.mid':
            # something is weird about this one.... it needs 16 extra chords?
            ['C7'] * 32 +
            ['C7'] * 16 +
            ['F7'] * 16 +
            ['C7'] * 16 +
            ['C7'] * 16 +
            ['F7'] * 16 +
            ['F7'] * 16 +
            ['C7'] * 16 +
            ['C7'] * 16 +
            ['G7'] * 16 +
            ['F7'] * 16 +
            ['C7'] * 16 +
            ['G7'] * 16,
    }

    print("real jazz solos")
    for midi_filename, chords in real_jazz.iteritems():
        ff = improv_fitness.FitnessFunction(raw_chords=chords)
        f, length = ff.evaluate_fitness_midi("jazz_midis/" + midi_filename)
        jazz_fitness.append(f / length)
        print(midi_filename.strip("_FINAL.mid"), '%3.3f' % (f/l))

    plt.figure()
    plt.boxplot([tonic_fitness, random_fitness, jazz_fitness], 0, '')
    plt.ylabel("Fitness")
    plt.xticks([1,2,3], ['tonic', 'random', 'real jazz'])
    plt.savefig('random_vs_real_jazz.png')

# arpeggio tonic
if 1:
    chords = [
       MyChord('C3', 4, '')
    ]
    ff = improv_fitness.FitnessFunction(chords)
    arpeggio_fitness = []
    arpeggio_tonics = []
    min_note = 12 * 2
    max_note = 127 - 16 - 12 * 2
    for tonic in range(min_note, max_note):
        melody = []
        melody.append(tonic)
        melody.append(tonic + 4)
        melody.append(tonic + 7)
        melody.append(tonic + 12)
        melody.append(tonic + 16)
        melody.append(tonic + 12)
        melody.append(tonic + 7)
        melody.append(tonic + 4)

        f, l = ff.evaluate_fitness(melody)
        arpeggio_fitness.append(f / l)
        arpeggio_tonics.append(tonic)

    plt.figure()
    plt.plot(arpeggio_tonics, arpeggio_fitness, linestyle='None', marker='o', markersize=3, label='arpeggio')
    plt.ylabel("Fitness"),
    plt.xlabel('arpeggio tonic')
    plt.grid()
    plt.xticks(range(min_note, max_note, 12))
    plt.savefig('arpeggio_tonic.png')

plt.show()
