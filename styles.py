# Intervalele gamelor, în semitonuri față de tonică
SCALES = {
    "major":            [0, 2, 4, 5, 7, 9, 11],
    "minor":            [0, 2, 3, 5, 7, 8, 10],
    "pentatonic_major": [0, 2, 4, 7, 9],
    "pentatonic_minor": [0, 3, 5, 7, 10],
    "blues":            [0, 3, 5, 6, 7, 10],
    "dorian":           [0, 2, 3, 5, 7, 9, 10],
}

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# key = tonica (0 = Do, 2 = Re, 4 = Mi, 7 = Sol, 9 = La)
# program = instrument General MIDI
# range = registrul în care rămân notele (cea mai joasă, cea mai înaltă)
STYLES = {
    "Clasic": {
        "model": "attention_rnn", "temperature": 0.8, "qpm": 90,
        "key": 0, "scale": "major", "primer": [60, 64, 67, 72],
        "program": 0, "drums": False, "range": (55, 84),
    },
    "Jazz": {
        "model": "lookback_rnn", "temperature": 1.1, "qpm": 120,
        "key": 2, "scale": "dorian", "primer": [62, 65, 69, 72],
        "program": 66, "drums": True, "range": (55, 82),
    },
    "Blues": {
        "model": "lookback_rnn", "temperature": 1.0, "qpm": 80,
        "key": 9, "scale": "blues", "primer": [57, 60, 62, 63],
        "program": 27, "drums": True, "range": (52, 79),
    },
    "Rock": {
        "model": "basic_rnn", "temperature": 1.0, "qpm": 140,
        "key": 4, "scale": "pentatonic_minor", "primer": [64, 67, 69, 71],
        "program": 29, "drums": True, "range": (52, 79),
    },
    "Ambient": {
        "model": "attention_rnn", "temperature": 0.7, "qpm": 60,
        "key": 9, "scale": "minor", "primer": [69, 72, 76],
        "program": 89, "drums": False, "range": (57, 81),
    },
    "Pop": {
        "model": "basic_rnn", "temperature": 0.9, "qpm": 115,
        "key": 7, "scale": "pentatonic_major", "primer": [67, 69, 71, 74],
        "program": 81, "drums": True, "range": (60, 86),
    },
}


def snap_to_scale(pitch, key, scale_name, low, high):
    """Mută nota pe cea mai apropiată notă din gamă și o aduce în registru."""
    allowed = {(key + i) % 12 for i in SCALES[scale_name]}
    # căutăm cea mai apropiată notă permisă: 0, -1, +1, -2, +2, ...
    for delta in range(7):
        if (pitch - delta) % 12 in allowed:
            pitch = pitch - delta
            break
        if (pitch + delta) % 12 in allowed:
            pitch = pitch + delta
            break
    # o mutăm cu câte o octavă (12 semitonuri) până intră în registru
    while pitch < low:
        pitch += 12
    while pitch > high:
        pitch -= 12
    return pitch