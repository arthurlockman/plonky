from __future__ import print_function, division

import os

import matplotlib.pyplot as plt
import numpy as np
import music21
import fitness

ff = fitness.FitnessFunction()

# random versus good jazz solos
if 1:
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

    for _ in range(20):
        f, num_arpeggios = random_midi(ff)
        random_fitness.append(f / num_arpeggios)

    jazz_fitness = []
    for filename in os.listdir("jazz_midis"):
        if filename.endswith(".mid"):
            try:
                f, num_arpeggios = ff.evaluate_fitness("jazz_midis/" + filename)
                jazz_fitness.append(f / num_arpeggios)
            except Exception:
                #print(filename + " is invalid")
                pass
        if len(jazz_fitness) == N:
            break

    plt.figure()
    plt.plot(random_fitness, linestyle='None', marker='o', label='random')
    plt.plot(jazz_fitness, linestyle='None', marker='o', label='real jazz')
    plt.ylabel("Fitness")
    plt.xlabel('sample')
    plt.legend()

# arpeggio tonic
if 0:
    arpeggio_fitness = []
    for tonic in range(0, 110):
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
        arpeggio_fitness.append(f / l)

    plt.figure()
    plt.plot(arpeggio_fitness, linestyle='None', marker='o', label='arpeggio')
    plt.ylabel("Fitness"),
    plt.xlabel('arpeggio tonic')

# arpeggio lengths
if 0:
    arpeggio_fitness = []
    arpeggio_lengths = []
    for _ in range(0, 50):
        tonic = 60
        s = music21.stream.Stream()
        # number of arpeggios
        num_arpeggios = np.random.randint(1, 16) * 4
        for i in range(num_arpeggios):
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
        arpeggio_fitness.append(f / l)
        arpeggio_lengths.append(num_arpeggios)

    plt.figure()
    plt.scatter(arpeggio_lengths, arpeggio_fitness)
    plt.ylabel("Fitness")
    plt.title("Major Triad Arpeggios")
    plt.xlabel("Arpeggio Length")

if 0:
    random_fitness = []
    lengths = []
    for num_measures in range(1, 50):
        num_notes = num_measures * 4

        for _ in range(5):
            s = music21.stream.Stream()
            for i in range(num_notes):
                n = music21.note.Note(np.random.randint(0, 127))
                n.duration.quarterLength = np.random.choice([1/4, 1/2, 1, 2, 4])
                s.append(n)

            mf = music21.midi.translate.streamToMidiFile(s)
            mf.open('.temp.mid', 'wb')
            mf.write()
            mf.close()
            f, l = ff.evaluate_fitness(".temp.mid")
            random_fitness.append(f / l)
            lengths.append(num_measures)

    plt.figure()
    plt.plot(lengths, random_fitness, linestyle='None', marker='o', label='random')
    plt.title("Random Midi")
    plt.ylabel("Fitness")
    plt.xlabel('Number of Measures')

# note lengths
if 0:
    measures = 10
    lengths = []
    fitness = []
    for i in range(1, 17):
        s = music21.stream.Stream()

        for _ in range(5):
            notes = measures * i
            for j in range(notes):
                pitch = np.random.randint(40, 90)
                n = music21.note.Note(pitch)
                n.quarterLength += 4 / i
                s.append(n)

            mf = music21.midi.translate.streamToMidiFile(s)
            mf.open('.temp.mid', 'wb')
            mf.write()
            mf.close()
            f, l = ff.evaluate_fitness(".temp.mid")
            fitness.append(f/l)
            lengths.append(i)

    plt.figure()
    plt.scatter(lengths, fitness)
    plt.title("Note Lengths")
    plt.ylabel('fitness')
    plt.xlabel('length, 1 == whole, 16=16ths')

# arpeggio tonic
if 0:
    tonic = 60

    # C major triad arpeggio
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
    print('1 Measure Major Triad Apreggio', f/l)

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
    print('2 Measure Major Triad Apreggio', f/l)

    # C major scale
    s = music21.stream.Stream()
    s.append(music21.note.Note(tonic))
    s.append(music21.note.Note(tonic + 2))
    s.append(music21.note.Note(tonic + 4))
    s.append(music21.note.Note(tonic + 5))
    s.append(music21.note.Note(tonic + 7))
    s.append(music21.note.Note(tonic + 9))
    s.append(music21.note.Note(tonic + 11))
    s.append(music21.note.Note(tonic + 12))

    mf = music21.midi.translate.streamToMidiFile(s)
    mf.open('.temp.mid', 'wb')
    mf.write()
    mf.close()
    f, l = ff.evaluate_fitness(".temp.mid")
    print('1 measures C scale', f/l)

    s.append(music21.note.Note(tonic + 12))
    s.append(music21.note.Note(tonic + 14))
    s.append(music21.note.Note(tonic + 16))
    s.append(music21.note.Note(tonic + 17))
    s.append(music21.note.Note(tonic + 19))
    s.append(music21.note.Note(tonic + 21))
    s.append(music21.note.Note(tonic + 23))
    s.append(music21.note.Note(tonic + 24))

    mf = music21.midi.translate.streamToMidiFile(s)
    mf.open('.temp.mid', 'wb')
    mf.write()
    mf.close()
    f, l = ff.evaluate_fitness(".temp.mid")
    print('2 measures C scale', f/l)

    # just the note C
    s = music21.stream.Stream()
    s.append(music21.note.Note(tonic))
    s.append(music21.note.Note(tonic))
    s.append(music21.note.Note(tonic))
    s.append(music21.note.Note(tonic))
    s.append(music21.note.Note(tonic))
    s.append(music21.note.Note(tonic))
    s.append(music21.note.Note(tonic))
    s.append(music21.note.Note(tonic))

    mf = music21.midi.translate.streamToMidiFile(s)
    mf.open('.temp.mid', 'wb')
    mf.write()
    mf.close()
    f, l = ff.evaluate_fitness(".temp.mid")
    print('1 measures Just C', f/l)

    s.append(music21.note.Note(tonic))
    s.append(music21.note.Note(tonic))
    s.append(music21.note.Note(tonic))
    s.append(music21.note.Note(tonic))
    s.append(music21.note.Note(tonic))
    s.append(music21.note.Note(tonic))
    s.append(music21.note.Note(tonic))
    s.append(music21.note.Note(tonic))

    mf = music21.midi.translate.streamToMidiFile(s)
    mf.open('.temp.mid', 'wb')
    mf.write()
    mf.close()
    f, l = ff.evaluate_fitness(".temp.mid")
    print('2 measures Just C', f/l)

plt.show()
