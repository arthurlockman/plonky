import matplotlib.pyplot as plt
import numpy as np
import sys

measure_pop_size = 32
phrase_pop_size = 48
max_gen = 15

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
    print(np.sum(counts))
plt.figure()
plt.stackplot(np.arange(max_gen), *counts_over_time)
plt.xlabel('measures used in phrase population')
plt.savefig('phrase_distrobution.png')

# TODO: measures
mfile = 'measures_%i.np' % gen_num

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
            if 0 <= g_i < 15:
                if note_on:
                    durations.append(duration)
                duration = 1
                note_on = True
            elif note_on and g_i == 15:
                duration += 1

    plt.figure()
    plt.hist(durations, bins=list(range(1,8)))
    plt.xlabel("Durations in number of 8th notes")
    plt.savefig(gen_num + '_durations_used.png')

#duration_hist(mfile, 'Durations Used')

plt.show()
