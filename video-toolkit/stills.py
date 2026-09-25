"""Render stills at scene-local times and tile them 2x2 into contact sheets.
Usage: venv/bin/python stills.py scene:local[,scene:local...]"""
import json, subprocess, sys, os
tl = json.load(open("build/timeline.json"))
start = {s["id"]: s["start"] for s in tl["scenes"]}
pairs = [p.split(":") for p in sys.argv[1].split(",")]
times = [round(start[sc] + float(t), 2) for sc, t in pairs]
env = dict(os.environ, NODE_PATH="/opt/node22/lib/node_modules")
subprocess.run(["node", "render.js", "--stills", ",".join(map(str, times)), "--scale", "1"], check=True, env=env)
ff = os.environ["FFMPEG"]
for k in range(0, len(times), 4):
    grp = times[k:k + 4]
    while len(grp) < 4: grp.append(grp[-1])
    ins = sum([["-i", f"build/still_{t}.png"] for t in grp], [])
    fc = "".join(f"[{i}]scale=960:540[v{i}];" for i in range(4)) + "[v0][v1][v2][v3]xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0"
    out = f"build/sheet_{k//4:02d}.png"
    subprocess.run([ff, "-loglevel", "error", "-y", *ins, "-filter_complex", fc, out], check=True)
    print(out, [f"{sc}:{t}" for sc, t in pairs[k:k + 4]])
