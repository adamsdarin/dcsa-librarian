# Video toolkit

Narrated, captioned cartoon explainer videos, rendered frame by frame in headless Chromium.
Built for the personnel-clearance (PCL) walkthrough; `examples/pcl/` holds that video's script and scenes.
This is not Librarian code. It lives here so follow-on video sessions can start from a branch.

## Setup (about 5 minutes; nothing here is committed)

```bash
cp -r video-toolkit "$WORK" && cd "$WORK"          # work in a scratch copy, not in the repo
python3 -m venv venv && ./venv/bin/pip install -q kokoro-onnx soundfile imageio-ffmpeg numpy
mkdir -p voices build && for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  curl -sSL -o voices/$f https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f; done
export NODE_PATH=/opt/node22/lib/node_modules      # global playwright; Chromium is preinstalled
export FFMPEG=$(./venv/bin/python -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
```

## Files you write per video
- `script.json`: scenes, each with lines. `cap` is the caption; optional `say` is what the voice reads (acronyms spelled out).
- `scenes.js`: one `SCENES.<id>` function per scene id. Key every animation to the line starts `L[i]`,
  so re-voicing the script never breaks sync. Reassign `STEPS`, `BAR_BRACKET` (or `null`) and `BAR_SCENES`
  here for your own progress bar. `examples/pcl/scenes.js` shows every prop and pattern.

## Pipeline
1. `./venv/bin/python tts.py bf_emma 0.95 en-gb` writes `build/narration.wav` and `build/timeline.json`, and prints the runtime.
2. `./venv/bin/python audit_say.py` checks acronym pronunciation. Then `./venv/bin/python stills.py "s1:3,s1:9,..."` renders stills at scene-local times and tiles them 2x2 in `build/sheet_*.png`. Review every scene this way.
3. `node render.js --ranges 0-5.8,54-80 --out build/sample.mp4` renders a short sample with audio.
4. `OUT_NAME=my-video ./render_full.sh` does the full render: 4 parallel frame-aligned chunks, then concat and loudness-normalized audio (about 5–8 minutes on 4 cores).

## Owner preferences (settled in the PCL session)
- Voice: Kokoro `bf_emma`, speed 0.95, lang `en-gb`. The owner rejected the Piper voices.
- Target about 5 minutes (roughly 700 words at this voice). Burned-in captions, step badge, and a journey bar.
- Checkpoints: send the script (with sources) plus a 20–30 second sample and **wait for approval** before the full build.
  The owner may send script edits pasted as a table; diff them carefully against your draft. Missing them once cost a round.
- Verify every factual claim against the library (Google Drive) or the official source (eCFR API needs `--compressed`).
  Prefer terms that won't go stale; list the ones that will, and why.
- No agency seals or logos; label the video "Unofficial training aid".

## Pitfalls already hit
- `P.globe(r)` and `P.dollar(r)` take a radius; most other props take a width. Passing 40 to a radius makes giant icons.
- A prop held in a hand rotates with the arm. Wrap it in `inHand(armAngle, svg)` to keep it upright.
- `pop()` scales around its x,y, so draw the popped content centered on the origin. For big groups, fade (`op`) instead.
- Red "no" marks and stamps must sit beside text, not on it. Keep captions at two lines or fewer (split long lines in `script.json`).
- Pronunciation: run `./venv/bin/python audit_say.py` after every script edit. **Never space out an acronym ending in "A"**:
  "D C S A may" is read as "D C S a-may" (the owner caught this at 2:13 of the PCL video). Unspaced caps ("DCSA") are
  spelled correctly. Spacing is fine where it's needed and the last letter isn't A ("F S O", "S O R", "S F eighty-six").
  **Possessives:** an all-caps acronym loses its "'s" ("DOHA's" becomes "Doha-r"). Write "Doha's" for a spoken word,
  or spaced letters for a letter acronym ("D C S A's" is safe because "A's" is not followed by a separate word).
  The owner flagged four misreads by ear before these rules existed; the audit now catches both patterns.
  Read phone numbers as digit groups.
- Piper and Kokoro peak at full scale; `render.js` and `render_full.sh` apply `loudnorm` (I=-16, TP=-1.5).
