import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import note_seq
from note_seq.protobuf import music_pb2, generator_pb2
from magenta.models.shared import sequence_generator_bundle
from magenta.models.melody_rnn import melody_rnn_sequence_generator

BASE = os.path.dirname(os.path.abspath(__file__))

# 1. Încărcăm modelul basic_rnn
bundle = sequence_generator_bundle.read_bundle_file(
    os.path.join(BASE, "models", "basic_rnn.mag"))
generator_map = melody_rnn_sequence_generator.get_generator_map()
generator = generator_map["basic_rnn"](checkpoint=None, bundle=bundle)
generator.initialize()

# 2. Construim primer-ul: Do Re Mi Fa, câte o pătrime fiecare
qpm = 120                       # tempo: 120 pătrimi pe minut
durata = 60.0 / qpm             # o pătrime = 0.5 secunde
primer = music_pb2.NoteSequence()
primer.tempos.add(qpm=qpm)
primer.ticks_per_quarter = note_seq.STANDARD_PPQ
for i, pitch in enumerate([60, 62, 64, 65]):
    primer.notes.add(pitch=pitch,
                     start_time=i * durata,
                     end_time=(i + 1) * durata,
                     velocity=80)
primer.total_time = 4 * durata

# 3. Stabilim cât generăm
seconds_per_step = 60.0 / qpm / 4          # o șaisprezecime
num_steps = 128                            # 8 măsuri
start = primer.total_time + seconds_per_step
end = primer.total_time + num_steps * seconds_per_step

options = generator_pb2.GeneratorOptions()
options.args["temperature"].float_value = 2.0
options.generate_sections.add(start_time=start, end_time=end)

# 4. Generăm!
melodie = generator.generate(primer, options)
print("Note generate:", len(melodie.notes))
print("Durata:", round(melodie.total_time, 1), "secunde")

# 5. Salvăm ca MIDI
os.makedirs(os.path.join(BASE, "output"), exist_ok=True)
cale = os.path.join(BASE, "output", "prima_melodie.mid")
note_seq.sequence_proto_to_midi_file(melodie, cale)
print("Salvat în:", cale)