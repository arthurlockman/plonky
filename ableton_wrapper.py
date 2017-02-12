import time
import music21
import rtmidi
from converter import Metadata


def  main():
    metadata = Metadata(None, None, None, 100, 8)

    stream = music21.stream.Stream()
    s = music21.corpus.parse('bach/bwv57.8')

    success = send_stream_to_ableton(s, metadata)

    # For comparison...
    # sp = music21.midi.realtime.StreamPlayer(s)
    # sp.play()


def send_stream_to_ableton(stream : music21.stream.Stream, metadata : Metadata):
    midi_out = rtmidi.MidiOut()
    ports = midi_out.get_ports()
    vport = 'loopMIDI Port 1'
    if vport in ports:
        port_idx = ports.index(vport)
        midi_out.open_port(port_idx)

    else:
        print("%s not found. Is loopMidi running?" % vport)
        return -1

    midi_file = music21.midi.translate.streamToMidiFile(stream)
    midi_track = midi_file.tracks[0]
    for event in midi_track.events:
        print(event)
        if event.type == 'DeltaTime':
            sleep_time = event.time * metadata.ms_per_beat / 1000 / 1024
            time.sleep(sleep_time)
        elif event.type == 'NOTE_ON':
            midi_out.send_message([0x90, event.pitch, event.velocity])
        elif event.type == 'NOTE_OFF':
            midi_out.send_message([0x80, event.pitch, event.velocity])


if __name__ == "__main__":
    main()