import time
import sys
import music21
import rtmidi
from converter import Metadata


def main():
    metadata = Metadata(None, None, None, 100, 8)

    stream = music21.stream.Stream()
    p1 = music21.stream.Part()
    p1.append(music21.instrument.Piano())
    p2 = music21.stream.Part()
    p2.append(music21.instrument.Trumpet())
    p2.append(music21.note.Note("C3"))
    p2.append(music21.note.Note("E3"))
    p2.append(music21.note.Note("G3"))
    p2.append(music21.note.Note("E3"))
    p2.append(music21.note.Note("C3", type='whole'))
    p1.append(music21.chord.Chord([60, 64, 67, 72], type='whole'))
    p1.append(music21.chord.Chord([60, 64, 67, 72], type='whole'))
    stream.append(p1)
    stream.append(p2)

    midi_out = get_virtual_midi_port()
    send_stream_to_virtual_midi(midi_out, stream, metadata)

    # For comparison...
    # sp = music21.midi.realtime.StreamPlayer(s)
    # sp.play()


def get_virtual_midi_port():
    midi_out = rtmidi.MidiOut()
    ports = midi_out.get_ports()

    if sys.platform == 'linux':
        midi_out.open_virtual_port('GenJam-VIRTUAL-MIDI')

    elif sys.platform == 'windows':
        vport = 'loopMIDI Port 1'

        if vport in ports:
            port_idx = ports.index(vport)
            midi_out.open_port(port_idx)

        else:
            print("%s not found. Is loopMidi running?" % vport)
            return None

    return midi_out


def send_stream_to_virtual_midi(midi_out : rtmidi.MidiOut, stream : music21.stream.Stream, metadata : Metadata):
    midi_file = music21.midi.translate.streamToMidiFile(stream)
    for event in midi_file:
        c = event.channel
        if event.type == 'DeltaTime':
            sleep_time = event.time * metadata.ms_per_beat / 1000 / 1024
            time.sleep(sleep_time)
        elif event.type == 'NOTE_ON':
            midi_out.send_message([(0x9 << 4) | c, event.pitch, event.velocity])
        elif event.type == 'NOTE_OFF':
            midi_out.send_message([(0x8 << 4) | c, event.pitch, event.velocity])


if __name__ == "__main__":
    main()