from __future__ import print_function, division

import matplotlib.pyplot as plt
import numpy as np
import music21
import improv_fitness
from converter import MyChord


# arpeggio tonic
if 0:
    chords = [
       MyChord('C3', 4, '')
    ]
    ff = improv_fitness.FitnessFunction(chords)
    arpeggio_fitness = []
    arpeggio_tonics = []
    for tonic in range(0, 127-16):
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
    plt.plot(arpeggio_tonics, arpeggio_fitness, linestyle='None', marker='o', label='arpeggio')
    plt.ylabel("Fitness"),
    plt.xlabel('arpeggio tonic')
    plt.grid()
    plt.xticks(range(0, 127, 12))
    plt.savefig('arpeggio_tonic.png')

# arpeggio lengths
if 0:

    arpeggio_fitness = []
    arpeggio_lengths = []
    for _ in range(0, 50):
        tonic = 60
        chords = []
        melody = []
        # number of arpeggios
        num_arpeggios = np.random.randint(1, 16) * 4
        for i in range(num_arpeggios):
            melody.append(tonic)
            melody.append(tonic + 4)
            melody.append(tonic + 7)
            melody.append(tonic + 12)
            melody.append(tonic + 16)
            melody.append(tonic + 12)
            melody.append(tonic + 7)
            melody.append(tonic + 4)
            chords.append(MyChord('C3', 4, ''))

        ff = improv_fitness.FitnessFunction(chords)
        f, l = ff.evaluate_fitness(melody)
        arpeggio_fitness.append(f / l)
        arpeggio_lengths.append(num_arpeggios)

    plt.figure()
    plt.scatter(arpeggio_lengths, arpeggio_fitness)
    plt.ylabel("Fitness")
    plt.title("Major Triad Arpeggios")
    plt.xlabel("Arpeggio Length")
    plt.savefig('arpeggio_length.png')

if 0:
    random_fitness = []
    lengths = []
    for num_measures in range(1, 50):

        chords = []
        for _ in range(num_measures):
            chords.append(MyChord('C3', 4, ''))

        num_notes = num_measures * 2

        for _ in range(5):
            melody = []
            for i in range(num_notes):
                pitch = np.random.randint(0, 127)
                duration = np.random.choice([1, 2, 4, 8])
                melody.append(pitch)
                print('>', pitch, duration)
                for j in range(duration):
                    melody.append(-1)
                    i += 1

            print(num_measures, len(chords), len(melody))
            ff = improv_fitness.FitnessFunction(chords)
            f, l = ff.evaluate_fitness(melody)
            random_fitness.append(f / l)
            lengths.append(num_measures)

    plt.figure()
    plt.plot(lengths, random_fitness, linestyle='None', marker='o', label='random')
    plt.title("Random Midi")
    plt.ylabel("Fitness")
    plt.xlabel('Number of Measures')
    plt.savefig('ranodm_midi_length.png')

# note lengths
if 1:
    measures = 10
    chords = []
    for i in range(measures):
        chords.append(MyChord('C3', 4, ''))
    ff = improv_fitness.FitnessFunction(chords)

    lengths = []
    fitness = []
    for i in range(1, 9):
        melody = []
        for _ in range(5):
            notes = measures * i
            for j in range(notes):
                pitch = np.random.randint(40, 90)
                melody.append(pitch)
                for k in range(i):
                    melody.append(-2)

            f, l = ff.evaluate_fitness(melody)
            fitness.append(f/l)
            lengths.append(i)

    plt.figure()
    plt.scatter(lengths, fitness)
    plt.title("Note Lengths")
    plt.ylabel('fitness')
    plt.xlabel('length, 1 == whole, 16=16ths')
    plt.savefig('note_duration.png')

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
