
# coding: utf-8

# # Distrobution of Populations

# In[2]:

import matplotlib.pyplot as plt
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

    plt.figure()
    plt.title(title)
    plt.hist(durations)

duration_hist('measures.np', 'Durations Used')

plt.show()
