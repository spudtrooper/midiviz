import pretty_midi

MIN_FADE_TIME = 0.5  # minimum fade time in seconds


def load_event_data(midi_path):
    midi_data = pretty_midi.PrettyMIDI(midi_path)

    # Extract track-wise notes and their timings
    track_count = len(midi_data.instruments)
    events = []

    max_velocity = 0
    for idx, instrument in enumerate(midi_data.instruments):
        for note in instrument.notes:
            max_velocity = max(max_velocity, note.velocity)
            start_time = note.start
            end_time = note.end
            events.append(
                (
                    start_time,
                    "on",
                    idx,
                    note.velocity,
                    max(end_time - start_time, MIN_FADE_TIME),
                )
            )
            events.append((end_time, "off", idx))

    # Sort events by time
    events.sort(key=lambda x: x[0])

    return (events, track_count)
