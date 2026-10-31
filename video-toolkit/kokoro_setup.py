"""Load Kokoro with an espeak-ng data path that espeak can actually use.

espeak-ng keeps its data path in a ~160-character buffer. When the venv lives in a deep
directory, the path to espeakng_loader's data exceeds it, espeak silently falls back to the
build machine's path, and the first phonemization dies with "Error processing file ... phontab".
Copy the data to a short path (KOKORO_ESPEAK_DATA, else the system temp dir) in that case."""
import os
import shutil
import tempfile
from pathlib import Path

import espeakng_loader
from kokoro_onnx import Kokoro
from kokoro_onnx.config import EspeakConfig


def load_kokoro(root: Path) -> Kokoro:
    data = espeakng_loader.get_data_path()
    if len(data) > 140:
        short = os.environ.get("KOKORO_ESPEAK_DATA") or os.path.join(tempfile.gettempdir(), "kokoro-espeak-data")
        if not os.path.isfile(os.path.join(short, "phontab")):
            shutil.copytree(data, short, dirs_exist_ok=True)
        data = short
    return Kokoro(str(root / "voices" / "kokoro-v1.0.onnx"), str(root / "voices" / "voices-v1.0.bin"),
                  espeak_config=EspeakConfig(data_path=data))
