#!/usr/bin/python

from collections import namedtuple
import sqlite3


SoloMetadata = namedtuple('SoloMetadata', ['melid', 'instrument', 'tempoclass', 'signature', 'chord_changes'])
legal_instruments = ['ts', 'as', 'bs', 'tp', 'tb', 'ts-c', 'cor', 'ss']

conn = sqlite3.connect('wjazzd.db')

c = conn.cursor()
solo_table_keys = ', '.join(SoloMetadata._fields)
solos = c.execute('select %s from solo_info' % solo_table_keys)

# filter out bad entries
valid_solos = []
for row in solos:
    solo = SoloMetadata(*row)

    if solo.melid and solo.tempoclass and solo.signature \
       and solo.chord_changes and solo.instrument in legal_instruments:
        valid_solos.append(solo)

# collect midi
MelodyMetadata = namedtuple('MelodyMetadata', ['melid', 'eventid', 'onset', 'pitch', 'duration', 'loud_cent'])
melody_table_keys = ', '.join(MelodyMetadata._fields)
demo_solo = valid_solos[0]
melody = c.execute('select %s from melody where melid=?' % melody_table_keys, str(demo_solo.melid))

for row in melody:
    event = MelodyMetadata(*row)
    print(event)
