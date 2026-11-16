import os
import note_seq
from note_seq.protobuf import music_pb2, generator_pb2
from magenta.models.shared import sequence_generator_bundle
from magenta.models.melody_rnn import melody_rnn_sequence_generator

from styles import STYLES, snap_to_scale

BASE = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE, "models")
STEPS_PER_QUARTER = 4

_cache = {}   # ținem modelele încărcate, ca să nu le reîncărcăm de fiecare dată


def load_melody_generator(model_name):
    if model_name not in _cache:
        bundle = sequence_generator_bundle.read_bundle_file(
            os.path.join(MODELS_DIR, model_name + ".mag"))
        gen_map = melody_rnn_sequence_generator.get_generator_map()
        generator = gen_map[model_name](checkpoint=None, bundle=bundle)
        generator.initialize()
        _cache[model_name] = generator
    return _cache[model_name]


def make_primer(pitches, qpm):
    """Construiește secvența de start: notele date, câte o optime fiecare."""
    seq = music_pb2.NoteSequence()
    seq.tempos.add(qpm=qpm)
    seq.ticks_per_quarter = note_seq.STANDARD_PPQ
    durata = 60.0 / qpm / 2
    for i, p in enumerate(pitches):
        seq.notes.add(pitch=p, start_time=i * durata,
                      end_time=(i + 1) * durata, velocity=90)
    seq.total_time = len(pitches) * durata
    return seq


def run_generator(generator, primer, qpm, num_bars, temperature):
    seconds_per_step = 60.0 / qpm / STEPS_PER_QUARTER
    num_steps = num_bars * 4 * STEPS_PER_QUARTER          # măsuri de 4/4
    options = generator_pb2.GeneratorOptions()
    options.args["temperature"].float_value = temperature
    options.generate_sections.add(
        start_time=primer.total_time + seconds_per_step,
        end_time=primer.total_time + num_steps * seconds_per_step)
    return generator.generate(primer, options)


def generate_melody(style_name, num_bars=16, temperature=None):
    """Generează o melodie în stilul cerut."""
    style = STYLES[style_name]
    temp = temperature if temperature is not None else style["temperature"]

    generator = load_melody_generator(style["model"])
    primer = make_primer(style["primer"], style["qpm"])
    melodie = run_generator(generator, primer, style["qpm"], num_bars, temp)

    # aplicăm stilul: gamă, registru, instrument
    low, high = style["range"]
    for nota in melodie.notes:
        nota.pitch = snap_to_scale(nota.pitch, style["key"],
                                   style["scale"], low, high)
        nota.program = style["program"]
    return melodie


def save_midi(seq, filename):
    out_dir = os.path.join(BASE, "output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    note_seq.sequence_proto_to_midi_file(seq, path)
    return path