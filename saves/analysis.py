import matplotlib.pyplot as plt
import numpy as np
import sys

measure_pop_size = 32
phrase_pop_size = 48
max_gen = 15
max_note = 16
max_duration = 16

# MEASURES
counts_over_time = np.ndarray((measure_pop_size, max_gen))
for gen_num in range(0, max_gen):
    filename = 'phrases_%i.np' % gen_num
    pop_f = open(filename,'r')
    pop = [l.strip('\n') for l in pop_f.readlines()]
    counts = np.zeros(measure_pop_size)
    for genome in pop:
        # -1 is to ignore fitness
        for g in genome.split(' ')[:-1]:
            counts[int(g)] += 1
    counts_over_time[:,gen_num] = counts
plt.figure()
plt.yticks([])
plt.stackplot(np.arange(max_gen), *counts_over_time)
plt.title('measures used in phrase population')
plt.xlabel("generation")
plt.savefig('phrase_distribution.png')

# NOTES
counts_over_time = np.ndarray((max_note, max_gen))
for gen_num in range(0, max_gen):
    filename = 'measures_%i.np' % gen_num
    pop_f = open(filename,'r')
    pop = [l.strip('\n') for l in pop_f.readlines()]
    counts = np.zeros(max_note)
    for genome in pop:
        # -1 is to ignore fitness
        for g in genome.split(' ')[:-1]:
            counts[int(g)] += 1
    counts_over_time[:,gen_num] = counts
plt.figure()
stuff = plt.stackplot(np.arange(max_gen), *counts_over_time)
plt.title('notes, rests, and sustains, used in measures population')
plt.xlabel("generation")
plt.savefig('measures_distribution.png')

# DURATIONS
counts_over_time = np.ndarray((max_duration, max_gen))
for gen_num in range(0, max_gen):
    filename = 'measures_%i.np' % gen_num
    pop_f = open(filename,'r')
    pop = [l.strip('\n') for l in pop_f.readlines()]
    counts = np.zeros(max_duration)
    note_on = False
    duration = -1
    for genome in pop:
        for g_s in genome.split(' ')[:-1]:
            g_i = int(g_s)
            if 0 < g_i < (max_note - 1):
                if note_on:
                    counts[duration - 1] += 1
                duration = 1
                note_on = True
            elif note_on and g_i == (max_note - 1):
                duration += 1

    counts_over_time[:,gen_num] = counts

plt.figure()
plt.yticks([])
stuff = plt.stackplot(np.arange(max_gen), *counts_over_time)
plt.legend(stuff, ['8th', 'quarter', 'dotted quarter', 'half', 'half tied to 8th', 'dotted half', 'double dotted half', 'whole'])
plt.yticks([])
plt.xlabel("generation")
plt.title("Durations of notes in number of 8th notes")
plt.savefig('durations_used.png')


#plt.show()
