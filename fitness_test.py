from __future__ import print_function, division

import os

import matplotlib.pyplot as plt
import numpy as np
import music21
import fitness

ff = fitness.FitnessFunction()

random_fitness = []
def random_midi(ff):
    s = music21.stream.Stream()
    l = np.random.randint(100, 400)
    for i in range(l):
        n = music21.note.Note(np.random.randint(0,127))
        n.duration.quarterLength = np.random.choice([1/4, 1/2, 1, 2, 4])
        s.append(n)

    mf = music21.midi.translate.streamToMidiFile(s)
    mf.open('.temp.mid', 'wb')
    mf.write()
    mf.close()
    return ff.evaluate_fitness(".temp.mid")

for i in range(100):
    f, l = random_midi(ff)
    print(f/l)
    random_fitness.append(f/l)

print('\n\n\n')
jazz_fitness = []
for filename in os.listdir("jazz_midis"):
    if filename.endswith(".mid"):
        try:
            f, l = ff.evaluate_fitness("jazz_midis/" + filename)
            print(f/l)
            jazz_fitness.append(f/l)
        except Exception:
            print(filename + " is invalid")


plt.plot(random_fitness, label='random')
plt.plot(jazz_fitness, label='real jazz')
plt.legend()
plt.show()
