
# coding: utf-8

# # Distrobution of Populations

# In[2]:

import matplotlib.pyplot as plt
from itertools import cycle
import numpy as np


def pop_hist(filename, title, bins):
    pop_f = open(filename,'r')
    pop = [l.strip('\n') for l in pop_f.readlines()]
    genes = []
    for genome in pop:
        genes += [int(g) for g in genome.split(' ')[:-1]]
    plt.figure()
    plt.title(title)
    plt.hist(genes, bins=bins)


pop_hist('phrases.np', 'Phrases', 64)
pop_hist('measures.np', 'Measures',16)


# # Distrobutions of Pitches
def pitch_hist(filename, title):
    pop_f = open(filename,'r')
    pop = [l.strip('\n') for l in pop_f.readlines()]
    pitches = []
    for genome in pop:
<<<<<<< HEAD
        for g_s in genome.split(' ')[:-1]:
            g_i = int(g_s)
            if 1 < g_i < 15:
                pitches.append(g_i)
    plt.figure()
    plt.title(title)
    plt.hist(pitches)


pitch_hist('measures.np', 'Pitches from 1-15 Used')


# # Distrobution of Durations
def duration_hist(filename, title):
    pop_f = open(filename,'r')
=======
        # -1 is to ignore fitness
        for g in genome.split(' ')[:-1]:
            counts[int(g)] += 1
    counts_over_time[:, gen_num] = counts
fig = plt.figure()
ax = fig.add_subplot(111)
stuff = ax.stackplot(np.arange(max_gen), *counts_over_time)
lgd = ax.legend(stuff[::-1],
                ['rest', 'note 1', 'note 2', 'note 3', 'note 4', 'note 5', 'note 6', 'note 7', 'note 8', 'note 9',
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
>>>>>>> d31deae... working on graphs for manual training
    pop = [l.strip('\n') for l in pop_f.readlines()]
    durations = []
    note_on = False
    duration = -1
    for genome in pop:
        for g_s in genome.split(' ')[:-1]:
            g_i = int(g_s)
            if g_i == 0:
                if duration != -1:
                    durations.append(duration)
                note_on = False
                duration = 0
            elif 1 < g_i < 15:
                note_on = True
            elif note_on and g_i == 15:
                duration += 1

<<<<<<< HEAD
    plt.figure()
    plt.title(title)
    plt.hist(durations)

duration_hist('measures.np', 'Durations Used')

=======
    counts_over_time[:, gen_num] = counts

plt.figure()
plt.yticks([])
stuff = plt.stackplot(np.arange(max_gen), *counts_over_time)
plt.legend(stuff, ['8th', 'quarter', 'dotted quarter', 'half', 'half tied to 8th', 'dotted half', 'double dotted half',
                   'whole'])
print(stuff)
plt.legend(stuff[::-1], ['8th', 'quarter', 'dotted quarter', 'half', 'half tied to 8th', 'dotted half', 'double dotted half',
    'whole'][::-1])
plt.yticks([])
plt.xlabel("generation")
plt.title("Durations of Notes in Number of 8th Notes")
plt.savefig('durations_used.png', bbox_inches='tight')

>>>>>>> d31deae... working on graphs for manual training
plt.show()
