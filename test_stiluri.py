from styles import STYLES
from generator import generate_melody, save_midi

for nume in STYLES:
    print(f"Generez {nume}...")
    melodie = generate_melody(nume, num_bars=8)
    cale = save_midi(melodie, f"{nume.lower()}.mid")
    print(f"  -> {len(melodie.notes)} note, salvat în {cale}")