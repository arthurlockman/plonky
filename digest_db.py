#!/usr/bin/python

from music21 import midi
from collections import namedtuple
import sqlite3


SoloMetadata = namedtuple('SoloMetadata', ['melid', 'title', 'instrument', 'avgtempo', 'signature', 'chord_changes'])
legal_instruments = ['ts', 'as', 'bs', 'tp', 'tb', 'ts-c', 'cor', 'ss']

conn = sqlite3.connect('wjazzd.db')

c = conn.cursor()
solo_table_keys = ', '.join(SoloMetadata._fields)
solos = c.execute('select %s from solo_info' % solo_table_keys)

# filter out bad entries
valid_solos = []
for row in solos:
    solo = SoloMetadata(*row)

    if solo.melid and solo.avgtempo and solo.signature \
       and solo.chord_changes and solo.instrument in legal_instruments:
        valid_solos.append(solo)

# collect midi
MelodyMetadata = namedtuple('MelodyMetadata', ['melid', 'eventid', 'onset', 'pitch', 'duration', 'loud_cent'])
melody_table_keys = ', '.join(MelodyMetadata._fields)


all_melody = c.execute('select loud_cent from melody')
demo_solo = valid_solos[0]
print(demo_solo.title)
melody = c.execute('select %s from melody where melid=?' % melody_table_keys, str(demo_solo.melid))

ticks_per_quarter_note = 1024
quarter_notes_per_beat = int(demo_solo.signature.split('/')[1]) / 8
beats_per_minute = demo_solo.avgtempo
ticks_per_second = ticks_per_quarter_note * quarter_notes_per_beat * beats_per_minute / 60
last_event_time = 0
track = midi.MidiTrack(1)
for row in melody:
    event = MelodyMetadata(*row)

    # each 'event' consists of an ON, DeltaTime, OFF , then another DeltaTime message

    # somehow convert seconds to midi ticks
    off_time = int((event.onset - last_event_time) * ticks_per_second)
    on_time = int(event.duration * ticks_per_second)
    delta_off = midi.DeltaTime(track, time=off_time, channel=None)
    on = midi.MidiEvent(track, type='NOTE_ON', time=None, channel=1)
    on.pitch = int(event.pitch)
    on.velocity = 100  # event.loud_cent * 127

    delta_on = midi.DeltaTime(track, time=on_time, channel=None)
    off = midi.MidiEvent(track, type='NOTE_OFF', time=None, channel=1)
    off.pitch = int(event.pitch)
    off.velocity = 100  # event.loud_cent * 127


    last_event_time = event.onset

    track.events.append(delta_off)
    track.events.append(on)
    track.events.append(delta_on)
    track.events.append(off)

end = midi.MidiEvent(track)
end.type = "END_OF_TRACK"
end.channel = 1
end.data = ''  # must set data to empty string
track.events.append(end)

midi_file = midi.MidiFile()
midi_file.ticksPerQuarterNote = ticks_per_quarter_note
midi_file.tracks.append(track)
midi_file.open('output.mid', 'wb')
midi_file.write()
midi_file.close()
