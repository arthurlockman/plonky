from __future__ import print_function, division

import os

import matplotlib.pyplot as plt
import numpy as np
import music21
import fitness

ff = fitness.FitnessFunction()
N = 20

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

for i in range(20):
    f, l = random_midi(ff)
    random_fitness.append(f/l)

jazz_fitness = []
for filename in os.listdir("jazz_midis"):
    if filename.endswith(".mid"):
        try:
            f, l = ff.evaluate_fitness("jazz_midis/" + filename)
            jazz_fitness.append(f/l)
        except Exception:
            #print(filename + " is invalid")
            pass
    if len(jazz_fitness) == N:
        break

arpeggio_fitness = []
for tonic in range(0, N):
    s = music21.stream.Stream()
    s.append(music21.note.Note(tonic))
    s.append(music21.note.Note(tonic + 4))
    s.append(music21.note.Note(tonic + 7))
    s.append(music21.note.Note(tonic + 12))
    s.append(music21.note.Note(tonic + 16))
    s.append(music21.note.Note(tonic + 12))
    s.append(music21.note.Note(tonic + 7))
    s.append(music21.note.Note(tonic + 4))

    mf = music21.midi.translate.streamToMidiFile(s)
    mf.open('.temp.mid', 'wb')
    mf.write()
    mf.close()
    f, l = ff.evaluate_fitness(".temp.mid")
    arpeggio_fitness.append(f/l)


plt.plot(random_fitness, label='random')
plt.plot(arpeggio_fitness, label='arpeggio')
plt.plot(jazz_fitness, label='real jazz')
plt.legend()
plt.show()
