"""Synthesize narration line by line with Kokoro and build the timeline.

Usage: venv/bin/python tts.py [voice-name] [speed] [lang]
Writes build/narration.wav and build/timeline.json.
"""
import json
import sys
import wave
from pathlib import Path

import numpy as np
from kokoro_onnx import Kokoro

ROOT = Path(__file__).parent
BUILD = ROOT / "build"
VOICE = sys.argv[1] if len(sys.argv) > 1 else "bf_emma"
SPEED = float(sys.argv[2]) if len(sys.argv) > 2 else 0.9
LANG = sys.argv[3] if len(sys.argv) > 3 else "en-gb"

LEAD = {"title": 1.6}      # silence before a scene's first line
DEFAULT_LEAD = 0.7
GAP = 0.45                 # between lines in a scene
TAIL = 0.9                 # after a scene's last line


def main():
    BUILD.mkdir(exist_ok=True)
    script = json.loads((ROOT / "script.json").read_text())
    kokoro = Kokoro(str(ROOT / "voices" / "kokoro-v1.0.onnx"), str(ROOT / "voices" / "voices-v1.0.bin"))
    rate = 24000

    audio = []
    t = 0.0
    scenes = []

    def silence(sec):
        audio.append(np.zeros(int(round(sec * rate)), dtype=np.int16))

    for scene in script["scenes"]:
        start = t
        lines = []
        if not scene["lines"]:
            hold = scene.get("hold", 4.0)
            silence(hold)
            t += hold
        else:
            lead = LEAD.get(scene["id"], DEFAULT_LEAD)
            silence(lead)
            t += lead
            for i, line in enumerate(scene["lines"]):
                samples, rate = kokoro.create(line.get("say", line["cap"]), voice=VOICE, speed=SPEED, lang=LANG)
                pcm = (np.clip(samples, -1, 1) * 32767).astype(np.int16)
                dur = len(pcm) / rate
                audio.append(pcm)
                lines.append({"cap": line["cap"], "start": round(t - start, 3), "end": round(t - start + dur, 3)})
                t += dur
                pad = GAP if i < len(scene["lines"]) - 1 else TAIL
                silence(pad)
                t += pad
        scenes.append({"id": scene["id"], "step": scene["step"], "label": scene["label"],
                       "start": round(start, 3), "end": round(t, 3), "lines": lines})

    pcm = np.concatenate(audio)
    with wave.open(str(BUILD / "narration.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm.tobytes())
    timeline = {"title": script["title"], "duration": round(t, 3), "scenes": scenes}
    (BUILD / "timeline.json").write_text(json.dumps(timeline, indent=1))
    words = sum(len(l["cap"].split()) for s in script["scenes"] for l in s["lines"])
    print(f"voice={VOICE} speed={SPEED} words={words} duration={t:.1f}s ({t/60:.2f} min)")
    for s in scenes:
        print(f"  {s['id']:8s} {s['start']:7.1f} -> {s['end']:7.1f}  ({s['end']-s['start']:.1f}s)")


if __name__ == "__main__":
    main()
