// Render stills or video ranges of scenes.html with headless Chromium.
//   node render.js --stills 3,60,70            -> build/still_<t>.png
//   node render.js --ranges 0-5.8,53.6-76 --out build/sample.mp4 [--fps 24] [--scale 1.5]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const BUILD = path.join(ROOT, 'build');
const FFMPEG = process.env.FFMPEG;
const arg = (k, d) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : d; };

function run(cmd, args) {
  return new Promise((res, rej) => {
    const p = spawn(cmd, args, { stdio: ['ignore', 'inherit', 'inherit'] });
    p.on('close', c => (c === 0 ? res() : rej(new Error(`${cmd} exited ${c}`))));
  });
}

(async () => {
  const timeline = JSON.parse(fs.readFileSync(path.join(BUILD, 'timeline.json'), 'utf8'));
  const fps = Number(arg('--fps', 24));
  const scale = Number(arg('--scale', 1.5));
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || undefined });
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: scale });
  page.on('pageerror', e => { console.error('PAGE ERROR', e.message); process.exit(1); });
  await page.goto('file://' + path.join(ROOT, 'scenes.html'));
  await page.evaluate(tl => init(tl), timeline);
  const stage = await page.$('#stage');

  const stills = arg('--stills');
  if (stills) {
    for (const t of stills.split(',').map(Number)) {
      await page.evaluate(x => renderAt(x), t);
      await stage.screenshot({ path: path.join(BUILD, `still_${t}.png`) });
    }
    await browser.close();
    return;
  }

  const ranges = arg('--ranges', `0-${timeline.duration}`).split(',').map(r => r.split('-').map(Number));
  const out = path.resolve(arg('--out', path.join(BUILD, 'video.mp4')));
  const silent = out.replace(/\.mp4$/, '.video.mp4');
  const ff = spawn(FFMPEG, ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-tune', 'animation', '-crf', '21', '-pix_fmt', 'yuv420p', '-r', String(fps), silent], { stdio: ['pipe', 'inherit', 'inherit'] });
  const done = new Promise((res, rej) => ff.on('close', c => (c === 0 ? res() : rej(new Error('ffmpeg ' + c)))));
  let n = 0; const t0 = Date.now();
  const total = ranges.reduce((a, [s, e]) => a + Math.round((e - s) * fps), 0);
  for (const [a, b] of ranges) {
    const frames = Math.round((b - a) * fps);
    for (let f = 0; f < frames; f++) {
      await page.evaluate(x => renderAt(x), a + f / fps);
      const buf = await stage.screenshot({ type: 'jpeg', quality: 93 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (++n % 240 === 0) console.log(`${n}/${total} frames, ${((Date.now() - t0) / n).toFixed(0)} ms/frame`);
    }
  }
  ff.stdin.end();
  await done;
  await browser.close();

  if (process.argv.includes('--video-only')) { fs.renameSync(silent, out); console.log(`wrote ${out} (${n} frames, video only)`); return; }
  // audio: same ranges cut from the narration, concatenated, then muxed
  const narr = path.join(BUILD, 'narration.wav');
  const parts = ranges.map(([a, b], i) => `[0:a]atrim=${a}:${b},asetpts=PTS-STARTPTS[a${i}]`).join(';');
  const cat = ranges.map((_, i) => `[a${i}]`).join('') + `concat=n=${ranges.length}:v=0:a=1,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[aout]`;
  await run(FFMPEG, ['-y', '-loglevel', 'error', '-i', narr, '-i', silent, '-filter_complex', `${parts};${cat}`,
    '-map', '1:v', '-map', '[aout]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', out]);
  fs.unlinkSync(silent);
  console.log(`wrote ${out} (${n} frames in ${((Date.now() - t0) / 1000).toFixed(0)}s)`);
})().catch(e => { console.error(e); process.exit(1); });
