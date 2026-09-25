// Scene definitions. Each receives ctx {t, local, L (line starts), Le (line ends), D} and returns SVG.
// Animations are keyed to line starts (L[i]), so re-voicing the script keeps everything in sync.

// ---------- extra cast ----------
CAST.rep = o => person({ skin: '#d2a679', hair: '#6b3e26', hairStyle: 'short', blazer: C.green, tie: C.yellow, pants: '#3d405b', seed: 6.1, ...o });
CAST.cow1 = o => person({ skin: '#e8b98f', hair: '#5a4632', hairStyle: 'short', top: '#a3b1c6', pants: '#6c757d', seed: 7.3, ...o });
CAST.cow2 = o => person({ skin: '#7d4e2d', hair: '#222', hairStyle: 'bun', top: '#c9b6d9', pants: '#6c757d', seed: 8.9, ...o });
CAST.neighbor = o => person({ skin: '#f3d1b0', hair: '#c9a15a', hairStyle: 'bob', top: C.orange, pants: '#495057', seed: 9.4, ...o });

// ---------- extra props ----------
const inHand = (armAngle, svg, dx = 0, dy = 0) => g(`rotate(${(-armAngle).toFixed(2)})`, g(`translate(${dx} ${dy})`, svg));
P.passport = (w = 56) => `<rect x="${-w / 2}" y="${-w * 0.7}" width="${w}" height="${w * 1.4}" rx="6" fill="${C.navy}" ${S2}/><circle cy="${-w * 0.15}" r="${w * 0.22}" fill="none" stroke="${C.yellow}" stroke-width="2.5"/>` + txt(0, w * 0.4, 'PASSPORT', w * 0.16, { fill: C.yellow, weight: 700 });
P.calendar = (big, small, w = 120, col = C.red) => {
  const h = w * 1.05;
  return `<rect x="${-w / 2}" y="${-h / 2}" width="${w}" height="${h}" rx="12" fill="${C.white}" ${S}/>` +
    `<path d="M${-w / 2} ${-h / 2 + 12} q0 -12 12 -12 h${w - 24} q12 0 12 12 v${h * 0.2} h${-w} z" fill="${col}" ${S}/>` +
    `<rect x="${-w * 0.3 - 4}" y="${-h / 2 - 10}" width="8" height="22" rx="4" fill="${C.ink}"/><rect x="${w * 0.3 - 4}" y="${-h / 2 - 10}" width="8" height="22" rx="4" fill="${C.ink}"/>` +
    txt(0, h * 0.08, big, w * 0.42, { weight: 700 }) + txt(0, h * 0.36, small, w * 0.16, { fill: C.gray, weight: 600 });
};
P.book = (label, sub = '', w = 110, col = C.purple) => {
  const h = w * 1.3;
  return `<rect x="${-w / 2}" y="${-h / 2}" width="${w}" height="${h}" rx="8" fill="${col}" ${S}/><rect x="${-w / 2 + 10}" y="${-h / 2 + 2}" width="8" height="${h - 4}" fill="rgba(0,0,0,0.22)"/>` +
    txt(5, -h * 0.1, label, w * 0.2, { fill: '#fff', weight: 700 }) + (sub ? txt(5, h * 0.13, sub, w * 0.13, { fill: '#ece4f7', weight: 600 }) : '');
};
P.magnifier = (r = 30) => `<path d="M${r * 0.7} ${r * 0.7} L${r * 1.9} ${r * 1.9}" stroke="${C.ink}" stroke-width="13" stroke-linecap="round"/><path d="M${r * 0.75} ${r * 0.75} L${r * 1.85} ${r * 1.85}" stroke="#9c6b45" stroke-width="7" stroke-linecap="round"/><circle r="${r}" fill="rgba(223,241,247,0.55)" stroke="${C.ink}" stroke-width="6"/>`;
P.handcuffs = (s = 1) => g(`scale(${s})`, `<path d="M-6 -2 h12" stroke="${C.ink}" stroke-width="5"/>` + [-16, 16].map(x => `<circle cx="${x}" r="12" fill="none" stroke="${C.ink}" stroke-width="10"/><circle cx="${x}" r="12" fill="none" stroke="#c0c7d1" stroke-width="5"/>`).join(''));
P.key = (s = 1, col = C.yellow) => g(`scale(${s})`, `<circle cx="-24" r="16" fill="${col}" ${S}/><circle cx="-24" r="5" fill="${C.ink}"/><rect x="-9" y="-6" width="50" height="12" rx="4" fill="${col}" ${S2}/><rect x="24" y="4" width="8" height="13" fill="${col}" ${S2}/><rect x="34" y="4" width="7" height="9" fill="${col}" ${S2}/>`);
P.hourglass = (p, h = 150) => {
  const w = h * 0.62, top = -h / 2 + 4, bot = h / 2 - 4, neck = 7;
  const wallX = y => (y < 0 ? lerp(w / 2, neck, (y - top) / (0 - top)) : lerp(neck, w / 2, y / bot));
  let s = `<path d="M${-w / 2} ${top} L${w / 2} ${top} L${neck} 0 L${w / 2} ${bot} L${-w / 2} ${bot} L${-neck} 0 Z" fill="#eaf6fb" ${S}/>`;
  const ys = lerp(top + 14, -3, p);
  if (p < 0.99) s += `<path d="M${-wallX(ys) + 3} ${ys} L${wallX(ys) - 3} ${ys} L${neck - 2} -2 L${-neck + 2} -2 Z" fill="${C.yellow}"/>`;
  const bh = (bot - 10) * Math.sqrt(p);
  s += `<path d="M${-w / 2 + 8} ${bot - 3} L${w / 2 - 8} ${bot - 3} L${w * 0.12} ${bot - 3 - bh} L${-w * 0.12} ${bot - 3 - bh} Z" fill="${C.yellow}"/>`;
  if (p < 0.99) s += `<path d="M0 0 V${bot - 3 - bh}" stroke="${C.yellow}" stroke-width="3"/>`;
  s += `<rect x="${-w / 2 - 12}" y="${top - 14}" width="${w + 24}" height="14" rx="5" fill="#9c6b45" ${S2}/><rect x="${-w / 2 - 12}" y="${bot}" width="${w + 24}" height="14" rx="5" fill="#9c6b45" ${S2}/>`;
  return s;
};
P.balance = (tilt, leftInner = '', rightInner = '') => {
  const Lb = 150, r = (tilt * Math.PI) / 180;
  const lx = -Lb * Math.cos(r), ly = -Lb * Math.sin(r), rx = Lb * Math.cos(r), ry = Lb * Math.sin(r);
  let s = `<rect x="-70" y="168" width="140" height="20" rx="7" fill="#9c6b45" ${S}/><rect x="-9" y="-6" width="18" height="176" fill="#b5835a" ${S2}/>`;
  const pan = (x, y) => `<path d="M${x.toFixed(1)} ${y.toFixed(1)} L${(x - 50).toFixed(1)} ${(y + 86).toFixed(1)} M${x.toFixed(1)} ${y.toFixed(1)} L${(x + 50).toFixed(1)} ${(y + 86).toFixed(1)}" stroke="${C.ink}" stroke-width="2.5"/>` +
    `<path d="M${(x - 66).toFixed(1)} ${(y + 86).toFixed(1)} h132 q-10 28 -66 28 q-56 0 -66 -28 z" fill="${C.yellow}" ${S}/>`;
  s += pan(lx, ly) + pan(rx, ry);
  s += `<path d="M${lx.toFixed(1)} ${ly.toFixed(1)} L${rx.toFixed(1)} ${ry.toFixed(1)}" stroke="${C.ink}" stroke-width="12" stroke-linecap="round"/><path d="M${lx.toFixed(1)} ${ly.toFixed(1)} L${rx.toFixed(1)} ${ry.toFixed(1)}" stroke="${C.yellow}" stroke-width="6" stroke-linecap="round"/><circle r="13" fill="${C.yellow}" ${S2}/>`;
  s += g(`translate(${lx.toFixed(1)} ${(ly + 84).toFixed(1)})`, leftInner) + g(`translate(${rx.toFixed(1)} ${(ry + 84).toFixed(1)})`, rightInner);
  return s;
};
P.gavel = (a = 0) => g(`rotate(${a.toFixed(2)} 0 70)`, `<rect x="-6" y="-8" width="12" height="80" rx="5" fill="#9c6b45" ${S2}/><rect x="-38" y="-34" width="76" height="30" rx="9" fill="#7a4e2d" ${S}/>`);
P.bench = (w = 300, h = 110, col = '#8a5a3b') => `<rect x="${-w / 2}" y="${-h}" width="${w}" height="${h}" rx="6" fill="${col}" ${S}/><rect x="${-w / 2 - 10}" y="${-h - 14}" width="${w + 20}" height="18" rx="6" fill="#a8744f" ${S}/><rect x="${-w / 2 + 20}" y="${-h + 26}" width="${w - 40}" height="${h - 46}" rx="6" fill="none" stroke="rgba(0,0,0,0.25)" stroke-width="3"/>`;
P.board = (title, rows, w = 330, h = 210) => {
  let s = `<rect x="-6" y="${h / 2}" width="12" height="80" fill="#9c6b45" ${S2}/><rect x="${-w / 2}" y="${-h / 2}" width="${w}" height="${h}" rx="12" fill="${C.white}" ${S}/>` +
    `<rect x="${-w / 2}" y="${-h / 2}" width="${w}" height="40" rx="12" fill="${C.navy}" ${S}/>` + txt(0, -h / 2 + 21, title, 20, { fill: '#fff', weight: 600 });
  rows.forEach((r, i) => { const y = -h / 2 + 68 + i * 38; s += `<circle cx="${-w / 2 + 28}" cy="${y}" r="7" fill="${C.teal}"/>` + txt(-w / 2 + 46, y + 1, r, 19, { anchor: 'start', weight: 500 }); });
  return s;
};
P.signpost = (hiA, hiB) => `<rect x="-9" y="-230" width="18" height="230" fill="#9c6b45" ${S2}/>` +
  `<path d="M-10 -215 H-190 L-222 -185 L-190 -155 H-10 Z" fill="${hiA ? C.yellow : C.cream}" ${S}/>` + txt(-110, -184, 'Hearing', 26, { weight: 600 }) +
  `<path d="M10 -135 H210 L242 -105 L210 -75 H10 Z" fill="${hiB ? C.yellow : C.cream}" ${S}/>` + txt(118, -104, 'Written record', 24, { weight: 600 });
P.door = (w = 170, h = 280) => `<rect x="${-w / 2 - 12}" y="${-h - 12}" width="${w + 24}" height="${h + 12}" rx="6" fill="#8a5a3b" ${S}/><rect x="${-w / 2}" y="${-h}" width="${w}" height="${h}" rx="4" fill="#b5835a" ${S}/>` +
  `<circle cx="${w / 2 - 22}" cy="${-h / 2}" r="8" fill="${C.yellow}" ${S2}/><rect x="${-w / 2 + 18}" y="${-h + 30}" width="${w - 36}" height="44" rx="6" fill="${C.red}" ${S2}/>` + txt(0, -h + 53, 'CLASSIFIED', 20, { fill: '#fff', weight: 700 });
P.cabinet = (open, labels) => {
  const w = 230, dh = 88;
  let s = `<rect x="${-w / 2}" y="${-dh * 3 - 20}" width="${w}" height="${dh * 3 + 20}" rx="10" fill="#a3b1c6" ${S}/>`;
  labels.forEach((lab, i) => {
    const y = -dh * 3 - 10 + i * dh, o = open[i] || 0, pull = 30 * o;
    if (o > 0) {
      s += `<rect x="${-w / 2 + 12}" y="${y}" width="${w - 24}" height="${pull + 12}" fill="#44505f"/>`;
      for (let k = 0; k < 3; k++) s += `<rect x="${-w / 2 + 26 + k * 58}" y="${y + 6}" width="46" height="${pull + 4}" rx="3" fill="${C.yellow}" ${S2}/>`;
    }
    s += `<rect x="${-w / 2 + 10}" y="${y + pull}" width="${w - 20}" height="${dh - 12}" rx="8" fill="#c8d1dd" ${S}/>` +
      `<rect x="-26" y="${y + 14 + pull}" width="52" height="10" rx="5" fill="${C.ink}"/>` + txt(0, y + 50 + pull, lab, 18, { weight: 600 });
  });
  return s;
};
P.radar = (u, r = 130) => {
  const a = (u * 110) % 360, ar = (a * Math.PI) / 180;
  let s = `<circle r="${r}" fill="#123524" ${S}/>`;
  for (const k of [0.33, 0.66]) s += `<circle r="${r * k}" fill="none" stroke="#2f7d4f" stroke-width="2"/>`;
  s += `<path d="M${-r} 0 H${r} M0 ${-r} V${r}" stroke="#2f7d4f" stroke-width="2"/>`;
  s += `<path d="M0 0 L${(Math.cos(ar) * r).toFixed(1)} ${(Math.sin(ar) * r).toFixed(1)} A${r} ${r} 0 0 0 ${(Math.cos(ar - 0.6) * r).toFixed(1)} ${(Math.sin(ar - 0.6) * r).toFixed(1)} Z" fill="rgba(87,220,130,0.35)"/>`;
  s += `<path d="M0 0 L${(Math.cos(ar) * r).toFixed(1)} ${(Math.sin(ar) * r).toFixed(1)}" stroke="#7dffa8" stroke-width="3"/>`;
  [[40, 0.5], [130, 0.8], [215, 0.35], [300, 0.62]].forEach(([deg, d]) => {
    const since = (((a - deg) % 360) + 360) % 360, glow = clamp(1 - since / 240);
    const br = (deg * Math.PI) / 180;
    s += `<circle cx="${(Math.cos(br) * r * d).toFixed(1)}" cy="${(Math.sin(br) * r * d).toFixed(1)}" r="7" fill="#9dffbf" opacity="${(0.15 + 0.85 * glow).toFixed(2)}"/>`;
  });
  return s;
};
P.rosette = (label = 'FCL') => {
  let s = `<path d="M-18 20 L-30 70 L-12 58 L-4 76 L4 30 Z M18 20 L30 70 L12 58 L4 76 L-4 30 Z" fill="${C.red}" ${S2}/>`;
  let pts = '';
  for (let i = 0; i < 24; i++) { const a = (i / 24) * Math.PI * 2, rr = i % 2 ? 40 : 46; pts += `${(Math.cos(a) * rr).toFixed(1)},${(Math.sin(a) * rr).toFixed(1)} `; }
  s += `<polygon points="${pts}" fill="${C.yellow}" ${S2}/><circle r="30" fill="${C.teal}" ${S2}/>` + txt(0, 1, label, 20, { fill: '#fff', weight: 700 });
  return s;
};
function card(w, h, inner, o = {}) {
  const { fill = C.white, dashed = false, stroke = C.ink } = o;
  return `<rect x="${-w / 2}" y="${-h / 2}" width="${w}" height="${h}" rx="18" fill="${fill}" stroke="${stroke}" stroke-width="${dashed ? 4 : 3.5}" ${dashed ? 'stroke-dasharray="14 9"' : ''}/>` + inner;
}
function flyer(u, a, d, p0, p1, p2, svg, spin = 0, s0 = 1, s1 = 1) {
  if (u < a || u > a + d) return '';
  const p = easeInOut(prog(u, a, d)), [x, y] = qb(p0, p1, p2, p);
  return g(at(x, y, lerp(s0, s1, p), spin * p), svg);
}
const shield = (col = C.teal) => `<path d="M0 -52 L44 -34 V6 Q44 42 0 58 Q-44 42 -44 6 V-34 Z" fill="${col}" ${S}/>` + g(at(0, 2, 1), P.check(20, C.green));
const tag = (x, y, s, o) => chip(x, y, s, { size: 18, ...o });

// ---------- Title ----------
SCENES.title = ({ local: u }) => {
  let s = bgNight(u);
  s += `<ellipse cx="640" cy="598" rx="190" ry="26" fill="rgba(255,255,255,0.12)"/>`;
  s += pop(u, 0.15, 640, 175, txt(0, 0, 'Your Security Clearance', 72, { fill: C.cream, weight: 700 }), 0.6);
  s += pop(u, 0.55, 640, 262, txt(0, 0, 'Step by Step', 50, { fill: C.yellow, weight: 700 }), 0.6);
  s += pop(u, 0.9, 640, 322, txt(0, 0, 'A 5-minute cartoon guide for new applicants', 24, { fill: '#cfe3f7', weight: 500 }), 0.5);
  s += slideIn(u, 0.4, 640, 800, 640, 596, actor('alex', 0, 0, 0.95, { t: u, armR: -150 + wob(u, 1.6, 22), mood: 'happy' }), 0.7);
  s += pop(u, 1.2, 830, 540, P.folder(120, '', C.yellow) + g(at(0, 8, 0.9), P.lock(36, C.red)), 0.5, 8);
  s += pop(u, 1.4, 450, 530, shield(), 0.5, -8);
  s += op(fade(u, 1.0, 0.6), txt(1250, 30, 'Unofficial training aid', 17, { fill: '#9fb8d6', anchor: 'end', weight: 500 }));
  return s;
};

// ---------- Meet Alex ----------
SCENES.meet = ({ local: u, L }) => {
  let s = bgSky(u);
  const wp = prog(u, 0.3, 2.0), ax = lerp(-120, 300, easeOut(wp)), walking = wp > 0 && wp < 0.97;
  const cheer = u > 2.5 && u < L[1] + 0.3;
  const armR = cheer ? -150 + wob(u, 1.4, 12) : -14;
  s += actor('alex', ax, 560, 1.0, {
    t: u, walk: walking, mood: 'happy', look: u > L[1] ? 5 : 0, armR,
    propR: cheer ? inHand(armR, P.doc(84, 104, 'Offer', { head: C.green, lines: 2, size: 15 }), 0, -58) : '',
  });
  s += confetti(u, 2.8, ax + 60, 300);
  s += op(1 - fade(u, L[1], 0.4), pop(u, 2.9, ax + 190, 240, chip(0, 0, 'Job accepted!', { fill: C.yellow, size: 24 }), 0.4));
  // what a clearance is
  const cardIn = `<g transform="translate(-160 0)">${shield()}</g>` +
    txt(40, -62, 'Security clearance =', 26, { weight: 700 }) +
    txt(40, -22, "the government's decision", 22, { weight: 500 }) +
    txt(40, 12, "that you're ELIGIBLE", 22, { weight: 700, fill: C.teal }) +
    txt(40, 46, 'for access to classified', 22, { weight: 500 }) + txt(40, 76, 'information', 22, { weight: 500 });
  s += pop(u, L[1] + 0.3, 690, 250, card(470, 220, cardIn), 0.5);
  // who decides
  s += slideIn(u, L[2] + 0.2, 1100, 760, 1100, 478, govBuilding(250, 'DCSA'), 0.7);
  s += op(fade(u, L[2] + 1.0), txt(1100, 505, 'Defense Counterintelligence', 18, { weight: 600 }) + txt(1100, 527, 'and Security Agency', 18, { weight: 600 }));
  if (u > L[2] + 2.2) {
    const p = easeOut(prog(u, L[2] + 2.2, 0.6));
    s += `<path d="M930 250 Q990 210 ${lerp(930, 1040, p).toFixed(1)} ${lerp(250, 300, p).toFixed(1)}" fill="none" stroke="${C.ink}" stroke-width="4" stroke-dasharray="10 8"/>`;
    s += pop(u, L[2] + 2.8, 990, 196, chip(0, 0, 'decides', { size: 18 }), 0.35);
  }
  return s;
};

// ---------- Before you start ----------
SCENES.basics = ({ local: u, L }) => {
  let s = bgSky(u);
  s += slideIn(u, L[0] + 0.2, 230, 780, 230, 482, officeBuilding(240, 250, 'Your Employer'), 0.7);
  s += pop(u, L[0] + 2.3, 345, 250, P.rosette('FCL'), 0.5, -8);
  s += op(fade(u, L[0] + 2.8), tag(230, 530, 'Facility clearance'));
  s += actor('alex', 560, 560, 0.95, { t: u, mood: 'happy', look: 5 });
  if (u > L[0] + 4.3) {
    const p = easeOut(prog(u, L[0] + 4.3, 0.6));
    s += `<path d="M370 330 Q430 290 ${lerp(370, 490, p).toFixed(1)} ${lerp(330, 350, p).toFixed(1)}" fill="none" stroke="${C.ink}" stroke-width="5" stroke-linecap="round"/>`;
    s += pop(u, L[0] + 4.8, 430, 270, chip(0, 0, 'sponsors you', { size: 18, fill: C.yellow }), 0.35);
  }
  // need-to-know, no "just in case"
  const f1 = 1 - fade(u, L[2] - 0.1, 0.4);
  if (u < L[2] + 0.4) {
    let n = pop(u, L[1] + 0.6, 830, 230, P.key(1.6), 0.45, -15) + op(fade(u, L[1] + 0.9), tag(830, 300, 'Need-to-know'));
    n += pop(u, L[1] + 3.6, 1080, 230, P.bubble(250, 80, txt(0, 0, 'Just in case?', 26, { weight: 600 }), 'left'), 0.45);
    n += pop(u, L[1] + 4.6, 1165, 305, P.stamp('NO', C.red, 34), 0.35, -10);
    s += op(f1, n);
  }
  // pre-employment and the 45-day rule
  if (u > L[2]) {
    const xs = [780, 990, 1200], y = 330;
    let tl = `<path d="M${xs[0]} ${y} H${lerp(xs[0], xs[2], easeOut(prog(u, L[3] + 0.2, 1.0)))}" stroke="${C.ink}" stroke-width="5" stroke-linecap="round"/>`;
    tl += pop(u, L[2] + 0.3, xs[0], 215, P.doc(80, 96, 'Offer', { head: C.green, lines: 2, size: 14 }), 0.4);
    tl += pop(u, L[2] + 0.3, xs[0], y, `<circle r="14" fill="${C.teal}" ${S2}/>`, 0.35) + op(fade(u, L[2] + 0.5), txt(xs[0], y + 36, 'Offer accepted', 18, { weight: 600 }));
    tl += op(fade(u, L[2] + 1.6), txt(xs[0], y + 60, 'process can start', 16, { weight: 500, fill: C.gray }));
    tl += pop(u, L[3] + 1.0, xs[1], y, `<circle r="14" fill="${C.yellow}" ${S2}/>`, 0.35) + op(fade(u, L[3] + 1.1), txt(xs[1], y + 36, 'Eligibility granted', 18, { weight: 600 }));
    tl += pop(u, L[3] + 1.6, xs[2], y, `<circle r="14" fill="${C.green}" ${S2}/>`, 0.35) + op(fade(u, L[3] + 1.7), txt(xs[2], y + 36, 'Start work', 18, { weight: 600 }));
    tl += op(fade(u, L[3] + 2.0), `<path d="M${xs[1]} ${y - 30} V${y - 46} H${xs[2]} V${y - 30}" fill="none" stroke="${C.red}" stroke-width="3"/>`);
    tl += pop(u, L[3] + 2.2, (xs[1] + xs[2]) / 2, 200, P.calendar('45', 'days', 96), 0.45);
    s += tl;
  }
  return s;
};

// ---------- Step 1: citizenship + FSO starts the request ----------
SCENES.s1 = ({ local: u, L }) => {
  const hand = L[0] + 2.2, handEnd = hand + 1.3;
  const click = L[1] + 2.4, launch = click + 0.35, land = launch + 1.5;
  let s = bgRoom(u);
  s += g(at(470, 440), P.desk(270));
  const pressed = u > click && u < click + 0.35;
  const screen1 = txt(0, -24, 'Investigation', 16, { weight: 600 }) + txt(0, -4, 'request', 16, { weight: 600 }) +
    `<rect x="-46" y="14" width="92" height="28" rx="14" fill="${pressed ? C.yellow : u > click ? C.green : C.teal}" ${S2}/>` +
    txt(0, 29, u > click ? 'Sent!' : 'Send', 15, { fill: '#fff', weight: 700 });
  s += g(at(470, 404), P.monitor(170, screen1));
  const tap = u > click - 0.6 && u < click + 0.3 ? wob(u, 3, 6) : 0;
  const fsoHold = u > handEnd && u < L[1] + 0.4;
  s += actor('fso', 265, 552, 0.95, {
    t: u, armR: -62 + tap, mood: 'happy', look: 4,
    armL: fsoHold ? 70 : 12, propL: fsoHold ? inHand(70, P.passport(40), 0, -8) : '',
  });
  s += nameTag(265, 285, 'FSO');
  s += op(fade(u, handEnd + 0.3) * (1 - fade(u, L[1] + 0.3, 0.4)),
    `<g transform="translate(470 250)">${chip(0, 0, 'U.S. citizenship verified', { size: 18, fill: C.yellow })}</g>` + pop(u, handEnd + 0.4, 596, 250, P.check(16), 0.3));
  // Alex, table, laptop
  s += `<rect x="860" y="452" width="180" height="16" rx="5" fill="#b5835a" ${S}/><rect x="940" y="468" width="20" height="74" fill="#9c6b45" ${S2}/>`;
  const got = u > land;
  const lscreen = got
    ? `<rect x="-92" y="-54" width="184" height="24" fill="${C.teal}"/>` + txt(0, -41, 'eApp  ·  NBIS', 15, { fill: '#fff', weight: 700 }) +
      g(at(-50, 4, 0.7), P.envelope(60)) + txt(26, -4, "You're", 17, { weight: 600 }) + txt(26, 18, 'invited!', 17, { weight: 600 })
    : txt(0, 0, 'Inbox', 18, { fill: C.gray });
  s += g(at(950, 452), P.laptop(210, lscreen));
  const offering = u > L[0] + 1.2 && u < hand;
  const mood = !got ? (u > L[1] ? 'neutral' : 'happy') : u < land + 0.6 ? 'surprised' : 'happy';
  s += actor('alex', 1135, 552, 0.95, {
    t: u, mood, look: -5,
    armL: offering ? 80 : got ? 40 + wob(u, 1.2, 4) : 14,
    propL: offering ? inHand(80, P.passport(40), 0, -8) : '',
  });
  s += nameTag(1135, 285, 'Alex');
  s += flyer(u, hand, handEnd - hand, [1060, 390], [720, 170], [345, 400], P.passport(44), 360);
  if (u > launch && u < land) {
    const p = easeInOut(prog(u, launch, land - launch));
    const [x, y] = qb([470, 330], [720, 60], [950, 380], p);
    s += g(at(x, y, 1 + 0.25 * Math.sin(p * Math.PI), p * 360), P.envelope(64));
  }
  s += burst(u, land, 950, 380, C.yellow, 10, 90);
  s += pop(u, land + 0.05, 820, 262, P.bubble(120, 54, txt(0, 0, 'Ding!', 26, { weight: 700, fill: C.red }), 'right'), 0.4);
  return s;
};

// ---------- Step 2: you complete the SF 86 in eApp ----------
const SF86_ROWS = [
  ['house', "Where you've lived"], ['briefcase', "Where you've worked"], ['cap', 'Where you studied'],
  ['globe', 'Foreign contacts'], ['plane', 'Foreign travel'], ['dollar', 'Finances'],
];
SCENES.s2 = ({ local: u, L: LL }) => {
  // lines: 0 intro, 1 sections, 2 gather records, 3 honesty, 4 releases + prints, 5 PVQ
  const REC = LL[2], L = [LL[0], LL[1], LL[3], LL[4], LL[5]];
  let s = bgRoom(u, { window: false });
  const W = { x: 400, y: 104, w: 830, h: 470 };
  const wp = popS(u, 0.25, 0.5);
  let win = `<rect x="0" y="0" width="${W.w}" height="${W.h}" rx="18" fill="${C.white}" ${S}/>` +
    `<path d="M0 18 Q0 0 18 0 H${W.w - 18} Q${W.w} 0 ${W.w} 18 V48 H0 Z" fill="${C.navy}" ${S}/>` +
    `<circle cx="26" cy="24" r="7" fill="${C.red}"/><circle cx="48" cy="24" r="7" fill="${C.yellow}"/><circle cx="70" cy="24" r="7" fill="${C.green}"/>` +
    txt(W.w / 2, 25, 'eApp', 22, { fill: '#fff', weight: 700 });
  win += op(fade(u, L[0] + 1.2), txt(W.w / 2, 86, 'SF 86 · Questionnaire for National Security Positions', 25, { weight: 600 }) +
    `<path d="M40 110 H${W.w - 40}" stroke="${C.light}" stroke-width="4"/>`);
  const phaseB = L[3] - 0.2;
  if (u < phaseB + 0.4) {
    const dim = u > L[2] ? lerp(1, 0.06, fade(u, L[2], 0.5)) : 1;
    let rows = '';
    SF86_ROWS.forEach(([icon, label], k) => {
      const col = k % 2, row = Math.floor(k / 2);
      const x = 70 + col * 390, y = 160 + row * 78;
      const a = L[1] + 0.2 + k * 0.55, done = REC + 1.0 + k * 0.3;
      rows += pop(u, a, x, y, P[icon](icon === 'globe' || icon === 'dollar' ? 20 : 40)) + op(fade(u, a + 0.1), txt(x + 40, y + 2, label, 23, { anchor: 'start', weight: 500 }));
      rows += op(fade(u, a), `<rect x="${x + 290}" y="${y - 15}" width="30" height="30" rx="7" fill="${C.white}" ${S2}/>`);
      if (u > done) rows += g(at(x + 305, y, popS(u, done, 0.3)), `<path d="M-9 0 L-2 8 L11 -9" fill="none" stroke="${C.green}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>`);
    });
    rows += op(fade(u, L[1] + 3.6), txt(W.w / 2, 400, '…and more', 22, { fill: C.gray, weight: 500 }));
    win += op(dim * (1 - fade(u, phaseB, 0.4)), rows);
    if (u > L[2] && u < phaseB + 0.4) {
      win += op(1 - fade(u, phaseB, 0.4), pop(u, L[2] + 0.25, W.w / 2, 215, P.stamp('COMPLETE + HONEST', C.teal, 40), 0.5, -8));
      win += op(1 - fade(u, phaseB, 0.4), pop(u, L[2] + 2.2, W.w / 2, 340,
        `<rect x="-250" y="-30" width="500" height="60" rx="30" fill="#fde2dc" ${S2}/>` + g(at(-212, 0, 0.8), P.cross(24)) +
        txt(18, 2, 'Omissions can hurt more than the issue', 22, { fill: C.red, weight: 600 }), 0.45));
    }
  }
  if (u > phaseB) {
    const fb = fade(u, phaseB + 0.1, 0.4);
    let b = g(at(210, 270), P.doc(190, 230, 'Release forms', { head: C.purple, lines: 4 }));
    const sig = prog(u, L[3] + 0.5, 1.6);
    b += `<path d="M150 348 c12 -26 22 -26 26 -6 s12 18 22 -10 s14 -18 20 4 s16 10 26 -8" fill="none" stroke="${C.navy}" stroke-width="4" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="${(1 - sig).toFixed(3)}"/>`;
    const [px, py] = [150 + sig * 94, 336 - Math.sin(sig * 18) * 10];
    if (sig > 0 && sig < 1) b += g(at(px, py), P.pen(62));
    b += txt(210, 410, 'Sign', 22, { weight: 600 });
    const scan = prog(u, L[3] + 1.4, 1.8);
    b += g(at(590, 290), P.scanner(220, scan));
    b += op(0.35 + 0.65 * fade(u, L[3] + 1.4, 0.3), g(at(590, 290, 0.95), P.fingerprint(32, scan > 0 ? C.navy : C.gray)));
    if (scan > 0 && scan < 1) b += `<rect x="512" y="${(256 + scan * 64).toFixed(1)}" width="156" height="5" rx="2.5" fill="${C.green}" opacity=".9"/>`;
    b += pop(u, L[3] + 3.3, 695, 232, P.check(22), 0.35);
    b += txt(590, 410, 'Electronic fingerprints', 22, { weight: 600 });
    win += op(fb, b);
  }
  s += g(`translate(${W.x + W.w / 2} ${W.y + W.h / 2}) scale(${wp.toFixed(4)}) translate(${-W.w / 2} ${-W.h / 2})`, win);
  if (u > L[4]) s += pop(u, L[4] + 0.2, 205, 178, g(`rotate(${(-5 + wob(u, 0.9, 2.5)).toFixed(2)})`, P.sticky(220, 118, ['Coming soon:', 'the PVQ', 'replaces SF 86'])), 0.45);
  const point = [L[1], L[2], L[3]].some(a => u > a && u < a + 1.6);
  const holding = u > REC + 0.2 && u < L[3];
  s += actor('alex', 205, 560, 0.95, {
    t: u, look: 5, mood: 'happy',
    armR: point ? -118 + wob(u, 2, 5) : -20,
    armL: holding ? 30 : u > L[4] + 0.3 && u < L[4] + 2.2 ? 160 + wob(u, 2, 5) : 12,
    propL: holding ? g(at(-18, 4, 0.55, 12), P.folder(90, '', C.yellow)) : '',
  });
  s += nameTag(205, 290, 'Alex');
  if (holding) s += op(fade(u, REC + 0.2), chip(105, 500, 'My records', { size: 17 }));
  return s;
};

// ---------- Step 3: FSO reviews ----------
SCENES.s3 = ({ local: u, L }) => {
  let s = bgRoom(u);
  const send = L[2] + 2.6, arrive = send + 1.3;
  s += actor('fso', 220, 552, 0.95, { t: u, mood: 'happy', look: 5, armR: u < L[1] ? -55 : -14 });
  s += nameTag(220, 285, 'FSO');
  // the form
  const docOut = u > send ? 0 : 1;
  let d = P.doc(210, 260, 'SF 86', { head: C.navy, lines: 5 });
  for (let k = 0; k < 5; k++) {
    const y = -130 + 48 + k * 40;
    if (u > L[0] + 1.0 + k * 0.35) d += g(at(80, y, popS(u, L[0] + 1.0 + k * 0.35, 0.25)), `<path d="M-8 0 L-2 7 L9 -8" fill="none" stroke="${C.green}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>`);
  }
  d += pop(u, L[0] + 2.8, 0, 96, P.stamp('COMPLETE', C.green, 26), 0.4, -8);
  d += pop(u, L[1] + 0.4, 0, -10, P.lock(64, C.yellow), 0.45);
  s += op(docOut, pop(u, 0.3, 520, 300, d, 0.5));
  if (u > L[0] + 0.3 && u < L[1]) {
    const p = prog(u, L[0] + 0.3, L[1] - L[0] - 0.3);
    s += g(at(470 + 90 * Math.sin(p * Math.PI * 2), 240 + p * 130, 1), P.magnifier(30));
  }
  // not shared: coworkers + NISPOM
  const fOut = 1 - fade(u, L[2], 0.4);
  if (u > L[1] && u < L[2] + 0.5) {
    let c = slideIn(u, L[1] + 0.1, 1300, 555, 890, 555, actor('cow1', 0, 0, 0.78, { t: u, mood: 'neutral', look: 3 }), 0.6);
    c += slideIn(u, L[1] + 0.3, 1400, 555, 1040, 555, actor('cow2', 0, 0, 0.78, { t: u, mood: 'surprised', look: -3 }), 0.6);
    c += pop(u, L[1] + 0.9, 965, 250, P.bubble(270, 70, txt(0, 0, "What's in Alex's form?", 20, { weight: 600 }), 'left'), 0.4);
    c += pop(u, L[1] + 1.8, 1118, 196, `<circle r="30" fill="#fff" stroke="${C.red}" stroke-width="8"/><path d="M-21 21 L21 -21" stroke="${C.red}" stroke-width="8" stroke-linecap="round"/>`, 0.35);
    c += pop(u, L[1] + 2.8, 1195, 400, P.book('NISPOM', '32 CFR 117', 104), 0.45, 6);
    s += op(fOut, c);
  }
  // release to DCSA
  s += slideIn(u, L[2] + 0.3, 1100, 780, 1100, 480, govBuilding(230, 'DCSA'), 0.7);
  s += flyer(u, send, arrive - send, [520, 300], [820, 120], [1090, 400], P.folder(110, 'SF 86 + prints', C.yellow), 0, 1, 0.6);
  s += burst(u, arrive, 1100, 390, C.yellow, 10, 80);
  s += pop(u, arrive + 0.1, 1100, 250, chip(0, 0, 'Released to DCSA', { size: 19, fill: C.yellow }), 0.4);
  return s;
};

// ---------- Step 4: DCSA checks the package ----------
SCENES.s4 = ({ local: u, L }) => {
  const a = L[0];
  const miss = a + 3.4, back0 = a + 4.3, fix = a + 5.4, fwd0 = a + 6.4, ok = a + 7.5;
  let s = bgRoom(u);
  s += actor('fso', 130, 552, 0.85, { t: u, mood: u > miss && u < ok ? 'neutral' : 'happy', look: 4 });
  s += nameTag(130, 310, 'FSO');
  const fixing = u > fix - 0.2 && u < fwd0;
  s += actor('alex', 290, 552, 0.85, { t: u, mood: 'happy', look: 4, armR: fixing ? -70 + wob(u, 3, 8) : -12, propR: fixing ? inHand(-70, P.pen(50), 0, 0) : '' });
  s += nameTag(290, 310, 'Alex');
  s += g(at(1100, 480, 0.85), govBuilding(230, 'DCSA'));
  // checklist panel
  const rows = ['SF 86', 'Signed releases', 'Fingerprints'];
  let pnl = card(400, 240, `<path d="M-200 -102 Q-200 -120 -182 -120 H182 Q200 -120 200 -102 V-78 H-200 Z" fill="${C.navy}" ${S}/>` + txt(0, -99, 'DCSA package check', 21, { fill: '#fff', weight: 600 }));
  rows.forEach((r, i) => {
    const y = -40 + i * 56;
    pnl += txt(-160, y, r, 22, { anchor: 'start', weight: 500 });
    const tOk = i === 1 ? ok : a + 1.3 + i * 0.5;
    if (i === 1 && u > miss && u < ok) pnl += g(at(140, y, popS(u, miss, 0.3)), P.cross(18)) + op(fade(u, miss + 0.2), txt(60, y, 'Missing!', 18, { fill: C.red, weight: 700 }));
    else if (u > tOk) pnl += g(at(140, y, popS(u, tOk, 0.3)), P.check(18));
    else pnl += `<rect x="124" y="${y - 16}" width="32" height="32" rx="8" fill="${C.white}" ${S2}/>`;
  });
  s += pop(u, 0.2, 690, 270, pnl, 0.5);
  s += flyer(u, back0, 1.0, [690, 300], [470, 120], [250, 360], P.folder(80, '', C.yellow), -20);
  if (u > back0 + 1.0 && u < fwd0) s += g(at(210, 360), P.folder(80, '', C.yellow));
  s += flyer(u, fwd0, 1.0, [250, 360], [470, 120], [690, 300], P.folder(80, '', C.yellow), 20);
  s += pop(u, ok + 0.2, 690, 440, chip(0, 0, 'Complete', { size: 22, fill: '#bfe8cc' }), 0.4);
  return s;
};

// ---------- Step 5: temporary eligibility ----------
SCENES.s5 = ({ local: u, L, D }) => {
  let s = bgRoom(u);
  s += g(at(190, 300), P.hourglass(prog(u, 0, D), 170));
  s += op(fade(u, 0.8), tag(190, 425, 'Investigation running…'));
  const handoff = L[1] + 3.0;
  const alexArm = u > handoff + 0.8 && u < L[2] ? -120 : -14;
  s += actor('alex', 1060, 555, 0.95, { t: u, mood: u > handoff + 0.8 && u < L[2] ? 'happy' : 'neutral', look: -5, armR: alexArm });
  s += nameTag(1060, 290, 'Alex');
  const tcard = card(330, 190,
    txt(0, -42, 'TEMPORARY', 38, { weight: 700, fill: C.teal, extra: 'letter-spacing="2"' }) + txt(0, 2, 'eligibility', 26, { weight: 600 }) +
    op(fade(u, L[0] + 5.8), txt(0, 48, '(you may hear "interim")', 19, { weight: 500, fill: C.gray })), { dashed: true, stroke: C.teal });
  if (u < handoff) s += pop(u, L[0] + 2.8, 620, 260, tcard, 0.5);
  else if (u < L[2]) {
    const p = easeInOut(prog(u, handoff, 0.9));
    s += g(at(lerp(620, 1192, p), lerp(260, 402, p), lerp(1, 0.42, p), lerp(0, 8, p)), tcard);
  }
  // early checks
  if (u > L[1] && u < L[2] + 0.4) {
    let e = pop(u, L[1] + 0.3, 520, 450, P.doc(50, 62, '', { lines: 3 }), 0.35) + pop(u, L[1] + 0.6, 600, 450, P.fingerprint(24), 0.35) + pop(u, L[1] + 0.9, 680, 446, P.magnifier(18), 0.35);
    e += op(fade(u, L[1] + 1.0), txt(600, 510, 'your form + early checks', 18, { weight: 600 }));
    e += op(fade(u, handoff + 1.0), tag(890, 250, 'Start sooner', { fill: C.yellow }));
    s += op(1 - fade(u, L[2], 0.4), e);
  }
  // limits and "not a denial"
  if (u > L[2]) {
    s += pop(u, L[2] + 0.4, 620, 230, card(430, 150,
      txt(0, -44, 'Limits', 26, { weight: 700 }) +
      txt(0, -4, 'RD, COMSEC and NATO need final eligibility', 17, { weight: 500 }) +
      txt(0, 28, 'Not over 1 year unless DCSA approves', 17, { weight: 500 })), 0.45);
    s += pop(u, L[2] + 2.4, 620, 420, g('rotate(-3)', P.sticky(300, 90, ['No temporary?', 'That is NOT a denial.'])), 0.45);
    s += op(fade(u, L[2] + 4.6), tag(190, 488, 'Wait for the final decision', { fill: C.yellow }));
  }
  return s;
};

// ---------- Step 6: investigation ----------
SCENES.s6 = ({ local: u, L }) => {
  let s = bgRoom(u);
  const armR = -58 + wob(u, 0.5, 4);
  s += actor('investigator', 250, 555, 0.95, { t: u, mood: 'happy', look: 5, armR, propR: inHand(armR, P.magnifier(24), 0, -10) });
  s += nameTag(250, 290, 'DCSA investigator', C.cream);
  // records
  if (u < L[1] + 0.4) {
    const rc = (x, icon, label, a) => pop(u, a, x, 250, card(230, 150, g(at(0, -22), icon) + txt(0, 44, label, 22, { weight: 600 })), 0.45);
    s += op(1 - fade(u, L[1], 0.4), rc(720, P.handcuffs(1.3), 'Criminal history', L[0] + 3.4) + rc(990, P.dollar(28), 'Credit', L[0] + 4.8));
  }
  // interviews
  if (u > L[1] && u < L[2] + 0.4) {
    let iv = '';
    [['alex', 760, 'You'], ['neighbor', 930, 'References'], ['cow1', 1100, 'People who know you']].forEach(([who, x, lab], k) => {
      const a = L[1] + 0.8 + k * 0.9;
      iv += slideIn(u, a, x, 760, x, 555, actor(who, 0, 0, 0.72, { t: u, mood: 'happy', talk: u > a + 0.5 && u < a + 1.8 }), 0.5);
      iv += op(fade(u, a + 0.3), txt(x, 342, lab, 17, { weight: 600 }));
    });
    iv += pop(u, L[1] + 4.3, 930, 190, chip(0, 0, 'Top Secret: a deeper look', { size: 20, fill: C.yellow }), 0.4);
    s += op(1 - fade(u, L[2], 0.4), iv);
  }
  // answer promptly + honestly
  if (u > L[2]) {
    s += slideIn(u, L[2] + 0.1, 900, 760, 690, 555, actor('alex', 0, 0, 0.9, { t: u, mood: 'happy', talk: u > L[2] + 0.6 && u < L[3], look: -5 }), 0.5);
    s += op(1 - fade(u, L[3] + 3.8, 0.4), pop(u, L[2] + 0.8, 520, 250, P.bubble(250, 66, txt(0, 0, 'Prompt + honest', 22, { weight: 700, fill: C.teal }), 'right'), 0.4));
  }
  // verify an investigator
  if (u > L[3]) {
    s += pop(u, L[3] + 1.0, 250, 225, `<circle r="26" fill="${C.yellow}" ${S2}/>` + txt(0, 2, '?', 32, { weight: 700 }), 0.35);
    s += pop(u, L[3] + 4.2, 1010, 250, card(380, 170,
      g(at(-140, 10, 0.75), P.phone(56)) + txt(40, -40, 'Verify an investigator', 21, { weight: 600 }) +
      txt(40, 6, '878-274-1186', 34, { weight: 700, fill: C.navy }) + txt(40, 46, 'DCSA', 18, { weight: 600, fill: C.gray }), { fill: C.cream }), 0.5);
  }
  return s;
};

// ---------- Step 7: adjudication ----------
const GUIDES = ['Allegiance', 'Foreign influence', 'Foreign preference', 'Sexual behavior', 'Personal conduct', 'Finances', 'Alcohol',
  'Drug involvement', 'Psychological', 'Criminal conduct', 'Protected info', 'Outside activities', 'IT use'];
SCENES.s7 = ({ local: u, L }) => {
  let s = bgRoom(u, { window: false });
  s += actor('adjudicator', 160, 555, 0.9, { t: u, mood: 'happy', look: 5, armR: u > L[0] + 1 && u < L[0] + 3 ? -100 : -14 });
  s += nameTag(160, 305, 'Adjudicator');
  // guideline cards
  const hl = { 0: L[1] + 2.0, 1: L[1] + 2.7, 5: L[1] + 3.5, 7: L[1] + 4.2, 4: L[1] + 5.0 };
  const gridDim = u > L[2] ? lerp(1, 0.45, fade(u, L[2], 0.5)) : 1;
  let grid = op(fade(u, L[0] + 3.5), txt(1060, 108, 'SEAD 4: 13 guidelines', 22, { weight: 700 }));
  GUIDES.forEach((name, k) => {
    const col = k < 7 ? 0 : 1, row = k < 7 ? k : k - 7;
    const x = 960 + col * 200, y = 150 + row * 46;
    const lit = hl[k] !== undefined && u > hl[k] && u < L[2];
    const c = `<rect x="-94" y="-18" width="188" height="36" rx="10" fill="${lit ? C.yellow : C.white}" ${S2}/><circle cx="-74" r="12" fill="${C.purple}"/>` +
      txt(-74, 1, String.fromCharCode(65 + k), 13, { fill: '#fff', weight: 700 }) + txt(-54, 1, name, 15, { anchor: 'start', weight: 600 });
    grid += pop(u, L[0] + 4.0 + k * 0.28, x, y, c, 0.3);
  });
  s += op(gridDim, grid);
  // balance: whole person + mitigation
  const good = [['Work', L[2] + 0.8], ['Family', L[2] + 1.3], ['Community', L[2] + 1.8], ['Time', L[3] + 0.3], ['Honesty', L[3] + 1.0], ['Change', L[3] + 1.9]];
  const bad = [['1 bad moment', L[2] + 3.0]];
  let tilt = 0;
  good.forEach(([, a]) => { tilt -= 3.2 * easeOut(prog(u, a, 0.5)); });
  bad.forEach(([, a]) => { tilt += 5 * easeOut(prog(u, a, 0.5)); });
  const stack = (items, col) => items.map(([lab, a], i) => {
    if (u < a) return '';
    const drop = (1 - easeOut(prog(u, a, 0.45))) * -220;
    return g(`translate(0 ${(-14 - i * 24 + drop).toFixed(1)})`, `<rect x="-58" y="-11" width="116" height="22" rx="11" fill="${col}" ${S2}/>` + txt(0, 1, lab, 13, { fill: '#fff', weight: 700 }));
  }).join('');
  s += op(fade(u, L[0] + 1.0, 0.5), g(at(560, 250), P.balance(tilt, stack(good, C.green), stack(bad, C.red))));
  s += op(fade(u, L[2] + 0.3) * (1 - fade(u, L[4] + 0.3, 0.3)), tag(560, 115, 'The whole person'));
  s += pop(u, L[4] + 0.5, 560, 118, P.stamp('FAVORABLE', C.green, 40), 0.45, -6);
  s += pop(u, L[4] + 3.4, 560, 490, chip(0, 0, 'Some: conditions + extra monitoring', { size: 18, fill: C.yellow }), 0.4);
  return s;
};

// ---------- Step 8: DOHA ----------
SCENES.s8 = ({ local: u, L }) => {
  let s = bgSky(u);
  s += g(at(160, 480, 0.7), govBuilding(230, 'DCSA'));
  s += g(at(1090, 480, 0.85), govBuilding(250, 'DOHA', '#f3e3c3'));
  s += op(fade(u, L[0] + 3.4), txt(1090, 505, 'Defense Office of', 17, { weight: 600 }) + txt(1090, 526, 'Hearings and Appeals', 17, { weight: 600 }));
  s += flyer(u, L[0] + 2.4, 1.4, [180, 380], [620, 90], [1000, 380], P.folder(84, 'Case', C.yellow), 0);
  const reading = u > L[0] + 4.0;
  s += slideIn(u, L[0] + 3.8, 1300, 555, 840, 555, actor('attorney', 0, 0, 0.9, {
    t: u, mood: 'neutral', look: -3, armR: reading ? -60 : -12, propR: reading && u < L[1] + 2.3 ? inHand(-60, P.folder(70, '', C.yellow), 0, -6) : '',
  }), 0.6);
  if (reading) s += op(fade(u, L[0] + 4.2), nameTag(840, 300, 'DOHA attorney'));
  // SOR
  const got = L[1] + 3.9;
  s += slideIn(u, L[1] + 0.1, -150, 555, 420, 555, actor('alex', 0, 0, 0.9, {
    t: u, mood: u > got ? 'worried' : 'neutral', look: 5, armR: u > got ? -40 : -12,
    propR: u > got ? inHand(-40, P.doc(56, 70, 'SOR', { head: C.red, lines: 3, size: 13 }), 0, -8) : '',
  }), 0.6);
  const sor = P.doc(170, 200, 'Statement of Reasons', { head: C.red, lines: 0, size: 14 }) +
    [0, 1, 2].map(i => `<circle cx="-60" cy="${-40 + i * 42}" r="7" fill="${C.red}"/><path d="M-44 ${-40 + i * 42} h${100 - i * 16}" stroke="${C.gray}" stroke-width="5" stroke-linecap="round"/>`).join('');
  if (u > L[1] + 1.9 && u < L[1] + 3.0) s += pop(u, L[1] + 1.9, 640, 240, sor, 0.4);
  s += flyer(u, L[1] + 3.0, 0.9, [640, 240], [560, 180], [470, 380], sor, -10, 1, 0.3);
  // or: granted
  if (u > L[2]) {
    s += pop(u, L[2] + 0.4, 640, 170, card(360, 90, g(at(-140, 0), P.check(24)) + txt(20, 0, 'Or: eligibility granted', 24, { weight: 700, fill: C.green }), { fill: '#e6f5eb' }), 0.45);
  }
  return s;
};

// ---------- Step 9: you respond ----------
SCENES.s9 = ({ local: u, L }) => {
  let s = bgRoom(u);
  s += g(at(420, 440), P.desk(260));
  s += g(at(400, 425, 1, -4), P.doc(90, 30, '', { lines: 0 }));
  const writing = u < L[2];
  s += actor('alex', 225, 552, 0.95, { t: u, mood: 'neutral', look: 4, armR: writing ? -72 + wob(u, 3, 6) : -14, propR: writing ? inHand(-72, P.pen(46)) : '' });
  s += nameTag(225, 285, 'Alex');
  s += op(1 - fade(u, L[1], 0.4), pop(u, L[0] + 2.2, 520, 250, chip(0, 0, 'Want the clearance? Respond.', { size: 20, fill: C.yellow }), 0.4));
  // 20 days, under oath, admit/deny
  if (u > L[1] && u < L[2] + 0.4) {
    let a = pop(u, L[1] + 0.8, 720, 240, P.calendar('20', 'days', 110), 0.45);
    let ans = P.doc(300, 250, 'Your answer', { head: C.navy, lines: 0, size: 16 });
    [0, 1, 2].forEach(i => {
      const y = -60 + i * 50;
      ans += txt(-135, y, `Allegation ${i + 1}`, 15, { anchor: 'start', weight: 600 }) +
        `<rect x="5" y="${y - 10}" width="20" height="20" rx="4" fill="#fff" ${S2}/>` + txt(31, y, 'Admit', 13, { anchor: 'start', weight: 500 }) +
        `<rect x="78" y="${y - 10}" width="20" height="20" rx="4" fill="#fff" ${S2}/>` + txt(104, y, 'Deny', 13, { anchor: 'start', weight: 500 });
      if (u > L[1] + 3.0 + i * 0.4) ans += `<path d="M${i === 1 ? 81 : 8} ${y} l5 6 l10 -12" fill="none" stroke="${C.green}" stroke-width="4" stroke-linecap="round"/>`;
    });
    ans += pop(u, L[1] + 2.0, 110, 90, `<circle r="30" fill="${C.red}" ${S2}/>` + txt(0, 1, 'OATH', 14, { fill: '#fff', weight: 700 }), 0.35, -12);
    a += pop(u, L[1] + 1.5, 990, 280, ans, 0.45);
    s += op(1 - fade(u, L[2], 0.4), a);
  }
  // hearing or written record
  if (u > L[2] && u < L[3] + 3.4) {
    const sp = P.signpost(u > L[2] + 1.6 && u < L[2] + 3.6, u > L[2] + 3.6);
    s += op(1 - fade(u, L[3] + 3.0, 0.4), pop(u, L[2] + 0.6, 870, 470, sp, 0.5));
  }
  // lawyer / representative, and no response = denied
  if (u > L[3]) {
    s += slideIn(u, L[3] + 0.2, 1400, 555, 640, 555, actor('rep', 0, 0, 0.9, { t: u, mood: 'happy', look: -4, armL: 20, propL: inHand(20, P.briefcase(46), 0, 10) }), 0.7);
    s += op(fade(u, L[3] + 0.9), nameTag(640, 300, 'Lawyer or representative'));
    s += pop(u, L[3] + 3.3, 1010, 330, P.stamp('NO RESPONSE = DENIED', C.red, 28), 0.45, -6);
  }
  return s;
};

// ---------- Step 10: decision and appeal ----------
SCENES.s10 = ({ local: u, L }) => {
  let s = bgRoom(u, { wall: '#efe6f5', window: false });
  s += actor('judge', 380, 470, 0.95, { t: u, mood: 'neutral' });
  s += g(at(380, 480), P.bench(300, 120));
  const bang = t0 => { const p = prog(u, t0, 0.35); return p > 0 && p < 1 ? -35 * Math.sin(p * Math.PI) : 0; };
  s += g(at(500, 318), P.gavel(bang(L[0] + 1.2) + bang(L[0] + 1.7) - 10));
  s += burst(u, L[0] + 1.4, 470, 350, C.orange, 8, 50);
  s += nameTag(380, 180, 'Administrative judge');
  // appeal board
  if (u > L[0] + 2.8) {
    let b = '';
    [890, 1010, 1130].forEach(x => { b += actor('judge', x, 425, 0.5, { t: u + x, mood: 'neutral' }); });
    b += g(at(1010, 480), P.bench(380, 90));
    s += op(fade(u, L[0] + 2.8, 0.4), b);
    s += op(fade(u, L[0] + 3.2), nameTag(1010, 262, 'DOHA Appeal Board'));
  }
  s += op(1 - fade(u, L[1], 0.3), pop(u, L[0] + 4.2, 1010, 158, P.calendar('15', 'days', 110), 0.45));
  if (u > L[1]) {
    s += pop(u, L[1] + 1.4, 1010, 158, P.calendar('1', 'year', 110, C.purple), 0.45);
    s += pop(u, L[1] + 2.6, 700, 262, chip(0, 0, 'Then your employer can reapply', { size: 19, fill: C.yellow }), 0.4);
  }
  return s;
};

// ---------- Access ----------
SCENES.access = ({ local: u, L }) => {
  let s = bgRoom(u);
  s += actor('alex', 220, 560, 0.95, { t: u, mood: 'happy', look: 5, armR: u > L[1] + 5.0 && u < L[1] + 6.8 ? -70 + wob(u, 3, 6) : -14 });
  s += nameTag(220, 292, 'Alex');
  s += op(1 - fade(u, L[1], 0.4), pop(u, L[0] + 0.9, 220, 225, chip(0, 0, 'ELIGIBLE', { size: 22, fill: '#bfe8cc' }), 0.4));
  if (u < L[1] + 0.4) {
    let e = pop(u, L[0] + 2.2, 820, 520, P.door() + g(at(0, -140), P.lock(44, C.yellow)), 0.5);
    e += pop(u, L[0] + 2.8, 520, 330, `<circle r="40" fill="${C.white}" ${S}/>` + txt(0, 3, '≠', 60, { weight: 700, fill: C.red, font: 'DejaVu Sans' }), 0.4);
    e += op(fade(u, L[0] + 2.6), txt(820, 540, 'Access', 24, { weight: 700 }));
    s += op(1 - fade(u, L[1], 0.4), e);
  }
  // briefing + SF 312
  if (u > L[1] && u < L[2] + 0.4) {
    let b = slideIn(u, L[1] + 0.2, 1400, 560, 1110, 560, actor('fso', 0, 0, 0.95, { t: u, mood: 'happy', look: -5, armL: u > L[1] + 2.0 && u < L[1] + 4.5 ? 120 : 12 }), 0.6);
    b += op(fade(u, L[1] + 0.6), nameTag(1110, 292, 'FSO'));
    b += pop(u, L[1] + 2.0, 820, 210, P.board('Initial security briefing', ['Threat awareness', 'Protecting classified info', 'Reporting duties']), 0.45);
    let doc = P.doc(170, 200, 'SF 312', { head: C.purple, lines: 3 });
    const sig = prog(u, L[1] + 5.0, 1.4);
    doc += `<path d="M-50 70 c10 -20 18 -20 22 -5 s10 14 18 -8 s12 -14 16 3 s12 8 20 -6" fill="none" stroke="${C.navy}" stroke-width="3.5" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="${(1 - sig).toFixed(3)}"/>`;
    b += pop(u, L[1] + 4.3, 470, 330, doc, 0.45);
    b += pop(u, L[1] + 6.6, 1110, 230, chip(0, 0, 'Witness', { size: 18, fill: C.cream }), 0.35);
    b += pop(u, L[1] + 7.8, 470, 470, chip(0, 0, 'Lasts for life', { size: 20, fill: C.yellow }), 0.4);
    s += op(1 - fade(u, L[2], 0.4), b);
  }
  // need-to-know
  if (u > L[2]) {
    const open = [0, 0, easeOut(prog(u, L[2] + 2.4, 0.6))];
    s += pop(u, L[2] + 0.3, 820, 520, P.cabinet(open, ['Program A', 'Program B', 'Your project']), 0.45);
    s += op(fade(u, L[2] + 0.6), g(at(968, 284), P.lock(34, C.yellow)) + g(at(968, 372), P.lock(34, C.yellow)));
    s += flyer(u, L[2] + 1.2, 1.1, [300, 380], [560, 200], [900, 430], P.key(1.2), 360);
    s += pop(u, L[2] + 2.4, 820, 180, chip(0, 0, 'Need-to-know', { size: 20, fill: C.yellow }), 0.4);
  }
  return s;
};

// ---------- Continuous vetting ----------
SCENES.cv = ({ local: u, L }) => {
  let s = bgRoom(u, { window: false });
  if (u < L[1] + 0.4) {
    let r = pop(u, L[0] + 2.4, 760, 270, P.radar(u, 125), 0.5);
    r += op(fade(u, L[0] + 2.8), tag(760, 425, 'Continuous vetting'));
    r += pop(u, L[0] + 4.8, 540, 170, chip(0, 0, 'Automated record checks', { size: 18, fill: C.cream }), 0.4);
    r += pop(u, L[0] + 7.0, 1090, 240, P.calendar('5', 'years', 120), 0.45) + pop(u, L[0] + 7.3, 1090, 352, chip(0, 0, 'Update your form', { size: 18, fill: C.yellow }), 0.4);
    s += op(1 - fade(u, L[1], 0.4), r);
    s += op(1 - fade(u, L[1], 0.4), actor('alex', 260, 560, 0.95, { t: u, mood: 'happy', look: 5 }) + nameTag(260, 292, 'Alex'));
  }
  if (u > L[1]) {
    s += op(fade(u, L[1], 0.4), actor('alex', 220, 560, 0.95, { t: u, mood: 'happy', look: 5, talk: u > L[1] + 1 && u < L[1] + 6.5 }) + nameTag(220, 292, 'Alex'));
    s += slideIn(u, L[1] + 0.1, 1400, 560, 1090, 560, actor('fso', 0, 0, 0.95, { t: u, mood: 'happy', look: -5 }), 0.6);
    s += op(fade(u, L[1] + 0.5), nameTag(1090, 292, 'FSO'));
    if (u > L[1] + 1.0) {
      const p = easeOut(prog(u, L[1] + 1.0, 0.6));
      s += `<path d="M330 420 H${lerp(330, 990, p).toFixed(1)}" stroke="${C.ink}" stroke-width="5" stroke-linecap="round" stroke-dasharray="12 10"/>`;
      if (p >= 1) s += `<path d="M975 408 L995 420 L975 432" fill="none" stroke="${C.ink}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>`;
      s += pop(u, L[1] + 1.4, 660, 450, chip(0, 0, 'Report', { size: 20, fill: C.yellow }), 0.35);
    }
    [[P.plane(56), 'Foreign travel', 3.1], [P.globe(28), 'Foreign contacts', 3.9], [P.dollar(28), 'Money trouble', 4.8], [P.handcuffs(1.3), 'An arrest', 5.5]].forEach(([icon, lab, dt], k) => {
      const x = 440 + k * 150;
      s += pop(u, L[1] + dt, x, 290, `<circle r="44" fill="${C.white}" ${S}/>` + icon, 0.4);
      s += op(fade(u, L[1] + dt + 0.1), txt(x, 356, lab, 17, { weight: 600 }));
    });
  }
  return s;
};

// ---------- Recap ----------
const RECAP_NODES = [...STEPS, 'Briefed + sign', 'Keep reporting'];
SCENES.recap = ({ local: u, L }) => {
  let s = bgSky(u, { ground: '#bfe3c0' });
  const n = RECAP_NODES.length, x0 = 90, x1 = 1190, dx = (x1 - x0) / (n - 1), y = 330;
  const lit = [L[0] + 0.9, L[0] + 2.0, L[0] + 3.3, L[0] + 3.8, L[0] + 4.4, L[0] + 5.0, L[0] + 5.6, L[0] + 6.8, L[0] + 7.2, L[0] + 7.6, L[1] + 0.8, L[1] + 2.4];
  s += `<path d="M${x0} ${y} H${x1}" stroke="${C.gray}" stroke-width="8" stroke-linecap="round"/>`;
  const bx0 = x0 + dx * 7 - 38, bx1 = x0 + dx * 9 + 38;
  s += `<path d="M${bx0} ${y + 72} V${y + 86} H${bx1} V${y + 72}" fill="none" stroke="${C.red}" stroke-width="3" stroke-dasharray="7 6"/>` + txt((bx0 + bx1) / 2, y + 104, 'only if issues', 17, { fill: C.red, weight: 600 });
  let reached = -1;
  RECAP_NODES.forEach((lab, i) => {
    const x = x0 + dx * i, on = u > lit[i], issue = i >= 7 && i <= 9;
    if (on) reached = i;
    const col = !on ? C.white : issue ? '#f6c7bb' : i >= 10 ? C.yellow : C.teal;
    const sc = on ? 1 + 0.25 * Math.max(0, 1 - (u - lit[i]) / 0.4) : 1;
    const label = i < 10 ? String(i + 1) : i === 10 ? 'SF' : 'CV';
    s += g(at(x, y, sc), `<circle r="20" fill="${col}" ${issue ? `stroke="${C.red}" stroke-width="3.5" stroke-dasharray="6 4"` : S2}/>` + txt(0, 1, label, i < 10 ? 16 : 13, { fill: on && !issue ? '#fff' : C.ink, weight: 700 }));
    s += txt(x, y + 42 + (i % 2) * 20, lab, 15, { weight: 600, fill: on ? C.ink : C.gray });
  });
  // Alex walks to the last reached node (skipping the dashed issue nodes on the happy path)
  const mapN = i => (i < 0 ? -0.8 : i >= 7 && i <= 9 ? 6 : i);
  const target = mapN(reached), from = mapN(reached - 1);
  const prevT = reached >= 0 ? lit[reached] : 0;
  const moveP = easeInOut(prog(u, prevT, 0.3 * Math.max(1, Math.abs(target - from))));
  const ax = x0 + dx * lerp(from, target, moveP);
  s += actor('alex', ax, y - 26, 0.5, { t: u, walk: moveP > 0 && moveP < 1, mood: 'happy', armR: reached === 11 && u > lit[11] + 0.5 ? -150 + wob(u, 1.5, 15) : -12 });
  // tips
  [['Tell the truth', 3.6], ['Meet deadlines', 4.6], ['Talk to your FSO', 5.6]].forEach(([tip, dt], k) => {
    s += pop(u, L[1] + dt, 360 + k * 280, 520, chip(0, 0, tip, { size: 24, fill: C.yellow }), 0.4);
  });
  return s;
};

// ---------- End card ----------
SCENES.end = ({ local: u }) => {
  let s = bgNight(u + 40, [120, 1160, 50, 395]);
  s += pop(u, 0.2, 640, 120, txt(0, 0, 'Questions? Ask your FSO.', 54, { fill: C.cream, weight: 700 }), 0.5);
  s += op(fade(u, 0.6), txt(640, 195, 'Verify a DCSA investigator: 878-274-1186', 26, { fill: C.yellow, weight: 600 }));
  s += op(fade(u, 1.0), txt(640, 270, 'Sources: 32 CFR Part 117 (NISPOM) · 32 CFR Part 155 · SEAD 4 ·', 20, { fill: '#cfe3f7', weight: 500 }) +
    txt(640, 300, 'DCSA Voice of Industry (Jan 2025, Jun 2026) · adapted from the “High Level PCL Process” map', 20, { fill: '#cfe3f7', weight: 500 }));
  s += op(fade(u, 1.4), txt(640, 360, 'Unofficial training aid · Not legal advice · Current as of September 2026', 19, { fill: '#9fb8d6', weight: 500 }));
  s += `<ellipse cx="640" cy="652" rx="130" ry="20" fill="rgba(255,255,255,0.12)"/>`;
  s += slideIn(u, 0.5, 640, 860, 640, 650, actor('alex', 0, 0, 0.8, { t: u, armR: -150 + wob(u, 1.6, 22), mood: 'happy' }), 0.6);
  return s;
};
