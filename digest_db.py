#!/usr/bin/python

from collections import namedtuple
import sqlite3


SoloMetadata = namedtuple('SoloMetadata', ['melid', 'tempoclass', 'signature', 'chord_changes'])

conn = sqlite3.connect('wjazzd.db')

c = conn.cursor()
keys = ', '.join(SoloMetadata._fields)
print(keys)
solos = c.execute('select %s from solo_info' % keys)

# filter out bad entries
valid_solos = []
for row in solos:
    solo = SoloMetadata(*row)
    if solo.melid and solo.tempoclass and solo.signature and solo.chord_changes:
        valid_solos.append(solo)


print(len(valid_solos), 'valid solo.')
