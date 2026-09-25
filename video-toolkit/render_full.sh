#!/bin/bash
# Render the full video in 4 parallel frame-aligned chunks, concat, then mux the narration.
set -euo pipefail
cd "$(dirname "$0")"
export NODE_PATH=/opt/node22/lib/node_modules
export FFMPEG=$(./venv/bin/python -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
FPS=24
DUR=$(python3 -c "import json;print(json.load(open('build/timeline.json'))['duration'])")
read -r -a EDGES <<< "$(python3 -c "
n=int($DUR*$FPS); k=4
print(' '.join(f'{round(n*i/k)/$FPS:.6f}' for i in range(k+1)))")"
rm -f build/chunk_*.mp4
for i in 0 1 2 3; do
  node render.js --ranges "${EDGES[$i]}-${EDGES[$((i+1))]}" --out "build/chunk_$i.mp4" --fps $FPS --video-only > "build/chunk_$i.log" 2>&1 &
done
wait
for i in 0 1 2 3; do tail -1 "build/chunk_$i.log"; echo "file 'chunk_$i.mp4'"; done | grep -v "^file" 
for i in 0 1 2 3; do echo "file 'chunk_$i.mp4'"; done > build/chunks.txt
$FFMPEG -loglevel error -y -f concat -safe 0 -i build/chunks.txt -c copy build/video_silent.mp4
$FFMPEG -loglevel error -y -i build/video_silent.mp4 -i build/narration.wav -map 0:v -map 1:a -c:v copy \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000" -c:a aac -b:a 160k -shortest -movflags +faststart build/${OUT_NAME:-video}.mp4
$FFMPEG -hide_banner -i build/${OUT_NAME:-video}.mp4 2>&1 | grep -E "Duration|Stream"
ls -la build/${OUT_NAME:-video}.mp4
