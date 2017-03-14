import matplotlib.pyplot as plt
from itertools import cycle
import numpy as np
import sys

measure_pop_size = 32
phrase_pop_size = 48
max_gen = 6
max_note = 16
max_duration = 16

# MEASURES
counts_over_time = np.ndarray((measure_pop_size, max_gen))
for gen_num in range(0, max_gen):
    filename = 'phrases_%i.np' % gen_num
    pop_f = open(filename, 'r')
    pop = [l.strip('\n') for l in pop_f.readlines()]
    counts = np.zeros(measure_pop_size)
    for genome in pop:
        # -1 is to ignore fitness
        for g in genome.split(' ')[:-1]:
            counts[int(g)] += 1
    counts_over_time[:, gen_num] = counts
plt.figure()
plt.yticks([])
plt.stackplot(np.arange(max_gen), *counts_over_time)
plt.title('Measures Used in Phrase Population')
plt.xlabel("generation")
plt.savefig('phrase_distribution.png', bbox_inches='tight')

# NOTES
counts_over_time = np.ndarray((max_note - 1, max_gen))
for gen_num in range(0, max_gen):
    filename = 'measures_%i.np' % gen_num
    pop_f = open(filename, 'r')
    pop = [l.strip('\n') for l in pop_f.readlines()]
    counts = np.zeros(max_note -1)
    for genome in pop:
        # -1 is to ignore fitness
        for g in genome.split(' ')[:-1]:
            if int(g) > 0:
                counts[int(g) - 1] += 1
    counts_over_time[:, gen_num] = counts
fig = plt.figure()
ax = fig.add_subplot(111)
stuff = ax.stackplot(np.arange(max_gen), *counts_over_time)
lgd = ax.legend(stuff[::-1],
                ['note 1', 'note 2', 'note 3', 'note 4', 'note 5', 'note 6', 'note 7', 'note 8', 'note 9',
                    'note 10', 'note 11', 'note 12', 'note 13', 'note 14', 'sustain'][::-1], loc='center left',
                bbox_to_anchor=(1, 0.5))
ax.set_title('Notes, Rests, and Sustains, Used in Measures Population')
ax.set_xlabel("generation")
plt.savefig('measures_distribution.png', bbox_extra_artists=(lgd,), bbox_inches='tight')

# DURATIONS
counts_over_time = np.ndarray((max_duration, max_gen))
for gen_num in range(0, max_gen):
    filename = 'measures_%i.np' % gen_num
    pop_f = open(filename, 'r')
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

    counts_over_time[:, gen_num] = counts

plt.figure()
plt.yticks([])
stuff = plt.stackplot(np.arange(max_gen), *counts_over_time)
plt.legend(stuff, ['8th', 'quarter', 'dotted quarter', 'half', 'half tied to 8th', 'dotted half', 'double dotted half',
                   'whole'])
plt.legend(stuff[::-1], ['8th', 'quarter', 'dotted quarter', 'half', 'half tied to 8th', 'dotted half', 'double dotted half',
    'whole'][::-1])
plt.yticks([])
plt.xlabel("generation")
plt.title("Durations of Notes in Number of 8th Notes")
plt.savefig('durations_used.png', bbox_inches='tight')

plt.show()
