import os
import urllib.request

# adresa de unde Google oferă modelele
BASE_URL = "http://download.magenta.tensorflow.org/models/"

MODELS = [
    "basic_rnn.mag",
    "lookback_rnn.mag",
    "attention_rnn.mag",
    "drum_kit_rnn.mag",
]

# folderul models/ de lângă acest fișier
MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")


def download_all():
    os.makedirs(MODELS_DIR, exist_ok=True)      # creează folderul dacă nu există
    for name in MODELS:
        path = os.path.join(MODELS_DIR, name)
        if os.path.exists(path):                # nu descărcăm de două ori
            print(f"[OK] {name} există deja")
            continue
        print(f"[...] Descarc {name}")
        urllib.request.urlretrieve(BASE_URL + name, path)
        size_mb = os.path.getsize(path) / 1e6
        print(f"[OK] {name} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    download_all()