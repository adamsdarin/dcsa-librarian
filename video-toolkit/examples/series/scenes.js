// Four-part clearance series: scene definitions. Each receives ctx {t, local, L (line starts), Le (line ends), D} and returns SVG.
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
  // two kinds of sponsor: a cleared company or a federal agency
  s += slideIn(u, L[0] + 0.2, 150, 780, 150, 482, g('scale(0.82)', officeBuilding(240, 250, 'Your Employer')), 0.7);
  s += pop(u, L[0] + 2.8, 240, 285, g('scale(0.8)', P.rosette('FCL')), 0.5, -8);
  s += op(fade(u, L[0] + 3.2), tag(150, 530, 'Facility clearance'));
  s += slideIn(u, L[0] + 4.6, 410, 780, 410, 482, g('scale(0.72)', govBuilding(230, 'AGENCY', '#dfe7f1')), 0.6);
  s += op(fade(u, L[0] + 5.0), tag(410, 530, 'Federal agency'));
  s += actor('alex', 640, 560, 0.95, { t: u, mood: 'happy', look: u > L[1] ? 5 : -4 });
  if (u > L[0] + 6.2) {
    const p = easeOut(prog(u, L[0] + 6.2, 0.6));
    s += op(1 - fade(u, L[4], 0.4), `<path d="M255 300 Q420 205 ${lerp(255, 585, p).toFixed(1)} ${lerp(300, 330, p).toFixed(1)}" fill="none" stroke="${C.ink}" stroke-width="5" stroke-linecap="round"/>` +
      `<path d="M500 372 Q545 345 ${lerp(500, 585, p).toFixed(1)} ${lerp(372, 362, p).toFixed(1)}" fill="none" stroke="${C.ink}" stroke-width="5" stroke-linecap="round"/>`);
    s += op(1 - fade(u, L[4], 0.4), pop(u, L[0] + 6.8, 420, 200, chip(0, 0, 'either can sponsor you', { size: 18, fill: C.yellow }), 0.35));
  }
  // need-to-know, no "just in case"
  if (u > L[1] && u < L[2] + 0.4) {
    let n = pop(u, L[1] + 0.6, 870, 230, P.key(1.6), 0.45, -15) + op(fade(u, L[1] + 0.9), tag(870, 300, 'Need-to-know'));
    n += pop(u, L[1] + 3.6, 1100, 230, P.bubble(250, 80, txt(0, 0, 'Just in case?', 26, { weight: 600 }), 'left'), 0.45);
    n += pop(u, L[1] + 4.6, 1180, 305, P.stamp('NO', C.red, 34), 0.35, -10);
    s += op(1 - fade(u, L[2] - 0.1, 0.4), n);
  }
  // pre-employment start, and the private-company 45-day rule
  if (u > L[2] && u < L[4] + 0.4) {
    const xs = [800, 1000, 1200], y = 330;
    let tl = `<path d="M${xs[0]} ${y} H${lerp(xs[0], xs[2], easeOut(prog(u, L[3] + 0.6, 1.0)))}" stroke="${C.ink}" stroke-width="5" stroke-linecap="round"/>`;
    tl += pop(u, L[2] + 0.3, xs[0], 215, P.doc(80, 96, 'Offer', { head: C.green, lines: 2, size: 14 }), 0.4);
    tl += pop(u, L[2] + 0.3, xs[0], y, `<circle r="14" fill="${C.teal}" ${S2}/>`, 0.35) + op(fade(u, L[2] + 0.5), txt(xs[0], y + 36, 'Offer accepted', 18, { weight: 600 }));
    tl += op(fade(u, L[2] + 1.6), txt(xs[0], y + 60, 'process can start', 16, { weight: 500, fill: C.gray }));
    tl += pop(u, L[3] + 1.4, xs[1], y, `<circle r="14" fill="${C.yellow}" ${S2}/>`, 0.35) + op(fade(u, L[3] + 1.5), txt(xs[1], y + 36, 'Eligibility granted', 18, { weight: 600 }));
    tl += pop(u, L[3] + 2.2, xs[2], y, `<circle r="14" fill="${C.green}" ${S2}/>`, 0.35) + op(fade(u, L[3] + 2.3), txt(xs[2] - 10, y + 36, 'In the cleared job', 18, { weight: 600 }));
    tl += op(fade(u, L[3] + 2.6), `<path d="M${xs[1]} ${y - 30} V${y - 46} H${xs[2]} V${y - 30}" fill="none" stroke="${C.red}" stroke-width="3"/>`);
    tl += pop(u, L[3] + 2.8, (xs[1] + xs[2]) / 2, 205, P.calendar('45', 'days', 96), 0.45);
    tl += pop(u, L[3] + 0.4, 1000, 100, chip(0, 0, 'Private company rule', { size: 18, fill: C.cream }), 0.35);
    s += op(1 - fade(u, L[4], 0.4), tl);
  }
  // scope: this video follows the contractor path
  if (u > L[4]) {
    s += pop(u, L[4] + 0.4, 662, 285, chip(0, 0, 'This video: contractor path', { size: 20, fill: C.yellow }), 0.4);
    s += pop(u, L[4] + 3.4, 1030, 235, card(420, 150,
      txt(0, -42, 'Working for a federal agency?', 22, { weight: 700 }) +
      txt(0, -4, "Your agency's security office", 20, { weight: 500 }) + txt(0, 26, 'guides you; later steps differ.', 20, { weight: 500 }), { fill: C.cream }), 0.45);
    if (u > L[4] + 3.6) {
      const p = easeOut(prog(u, L[4] + 3.6, 0.6));
      s += `<path d="M815 245 Q620 90 ${lerp(815, 425, p).toFixed(1)} ${lerp(245, 338, p).toFixed(1)}" fill="none" stroke="${C.ink}" stroke-width="4" stroke-dasharray="10 8"/>`;
    }
  }
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


// ---------- Recap ----------
const RECAP_NODES = ['FSO starts', 'You apply', 'FSO review', 'DCSA check', 'Temporary', 'Investigate', 'Adjudicate', 'DOHA review', 'You respond', 'Decision', 'Briefed + sign', 'Keep reporting'];
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


// =====================================================================
// Four-part series (Submission / Investigation / Adjudication / Maintenance)
// =====================================================================
const SERIES = ['Submission', 'Investigation', 'Adjudication', 'Maintenance'];
function onTimeline(tl) {
  if (tl.bar) { STEPS = tl.bar.steps; BAR_BRACKET = tl.bar.bracket; BAR_SCENES = new Set(tl.bar.scenes); }
  else BAR_SCENES = new Set(['s1', 's2', 's3', 's4', 's5', 's6', 's6b', 's7', 's7b', 's8', 's9', 's9b', 's10']);
}
const partNo = () => (TL.series ? TL.series.part : 1);
const seriesIcon = (k, u) => [
  g('translate(-14 4)', P.doc(70, 86, 'SF 86', { head: C.navy, lines: 2, size: 13 })) + g('translate(30 26) rotate(-12)', P.envelope(46)),
  g('translate(-8 -6)', P.magnifier(30)),
  g('translate(0 -36) scale(0.34)', P.balance(-6)),
  g('scale(0.5)', P.radar(u, 70)),
][k];

// ---------- Title (part-aware) ----------
SCENES.title = ({ local: u }) => {
  const n = partNo();
  let s = bgNight(u);
  s += `<ellipse cx="640" cy="598" rx="190" ry="26" fill="rgba(255,255,255,0.12)"/>`;
  s += pop(u, 0.15, 640, 170, txt(0, 0, 'Your Security Clearance', 70, { fill: C.cream, weight: 700 }), 0.6);
  s += pop(u, 0.55, 640, 256, txt(0, 0, `Part ${n}: ${SERIES[n - 1]}`, 52, { fill: C.yellow, weight: 700 }), 0.6);
  s += pop(u, 0.9, 640, 318, txt(0, 0, 'A four-part cartoon guide for new applicants', 24, { fill: '#cfe3f7', weight: 500 }), 0.5);
  s += slideIn(u, 0.4, 640, 800, 640, 596, actor('alex', 0, 0, 0.95, { t: u, armR: -150 + wob(u, 1.6, 22), mood: 'happy' }), 0.7);
  s += pop(u, 1.2, 830, 540, P.folder(120, '', C.yellow) + g(at(0, 8, 0.9), P.lock(36, C.red)), 0.5, 8);
  s += pop(u, 1.4, 450, 530, shield(), 0.5, -8);
  s += op(fade(u, 1.0, 0.6), txt(1250, 30, 'Unofficial training aid', 17, { fill: '#9fb8d6', anchor: 'end', weight: 500 }));
  return s;
};


// ---------- series helpers ----------
// Time a word is spoken, estimated from its position in the line's caption (good to a few tenths of a second).
function sayAt(c, i, word, lag = 0.1) {
  const cap = c.sc.lines[i].cap, k = cap.indexOf(word);
  return c.L[i] + (c.Le[i] - c.L[i]) * (k < 0 ? 0 : k / cap.length) + lag;
}
// Opacity that fades in at a and out at b.
const span = (u, a, b, d = 0.4) => (u < a || u > b + d ? 0 : fade(u, a, d) * (1 - fade(u, b, d)));
const iconTile = (u, a, x, y, icon, labels, r = 44) =>
  pop(u, a, x, y, `<circle r="${r}" fill="${C.white}" ${S}/>` + icon, 0.4) +
  op(fade(u, a + 0.1), labels.map((l, j) => txt(x, y + r + 22 + j * 21, l, 17, { weight: 600 })).join(''));
const reportArrow = (u, a, y = 420) => {
  const p = easeOut(prog(u, a, 0.6));
  if (p <= 0) return '';
  let s = `<path d="M330 ${y} H${lerp(330, 990, p).toFixed(1)}" stroke="${C.ink}" stroke-width="5" stroke-linecap="round" stroke-dasharray="12 10"/>`;
  if (p >= 1) s += `<path d="M975 ${y - 12} L995 ${y} L975 ${y + 12}" fill="none" stroke="${C.ink}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>`;
  return s + pop(u, a + 0.4, 660, y + 30, chip(0, 0, 'Report', { size: 20, fill: C.yellow }), 0.35);
};

// ---------- series props ----------
P.db = (w = 40, col = C.tealL) => {
  const h = w * 1.1, ry = w * 0.18;
  return `<path d="M${-w / 2} ${-h / 2} v${h} a${w / 2} ${ry} 0 0 0 ${w} 0 v${-h}" fill="${col}" ${S2}/><ellipse cy="${-h / 2}" rx="${w / 2}" ry="${ry}" fill="${col}" ${S2}/>` +
    `<path d="M${-w / 2} 0 a${w / 2} ${ry} 0 0 0 ${w} 0" fill="none" ${S2}/>`;
};
P.medcross = (s = 1) => g(`scale(${s})`, `<path d="M-8 -24 h16 v16 h16 v16 h-16 v16 h-16 v-16 h-16 v-16 h16 z" fill="${C.red}" ${S2}/>`);
P.mic = () => `<rect x="-11" y="-32" width="22" height="36" rx="11" fill="${C.gray}" ${S2}/><path d="M-18 -6 q0 20 18 20 q18 0 18 -20" fill="none" ${S2}/><path d="M0 14 v12 M-11 26 h22" ${S2}/>`;
P.rings = () => [-9, 9].map(x => `<circle cx="${x}" r="14" fill="none" stroke="${C.ink}" stroke-width="8"/><circle cx="${x}" r="14" fill="none" stroke="${C.yellow}" stroke-width="4"/>`).join('');
P.ballot = () => `<rect x="-10" y="-32" width="20" height="26" fill="#fff" ${S2}/><path d="M-5 -21 l4 4 l7 -9" stroke="${C.green}" stroke-width="3" fill="none" stroke-linecap="round"/>` +
  `<rect x="-26" y="-8" width="52" height="36" rx="4" fill="${C.navy}" ${S2}/><rect x="-14" y="-4" width="28" height="5" rx="2" fill="${C.ink}"/>`;
P.bank = () => {
  let s = `<path d="M-28 -12 L0 -30 L28 -12 Z" fill="#e9eef3" ${S2}/>`;
  for (const x of [-20, -7, 6, 19]) s += `<rect x="${x - 3}" y="-10" width="7" height="26" fill="#e9eef3" ${S2}/>`;
  return s + `<rect x="-30" y="16" width="60" height="8" fill="#e9eef3" ${S2}/>` + g('translate(22 -22)', P.globe(10));
};
P.bell = (a = 0) => g(`rotate(${a.toFixed(2)} 0 -26)`, `<path d="M-22 12 q2 -36 22 -36 q20 0 22 36 z" fill="${C.yellow}" ${S2}/><rect x="-27" y="10" width="54" height="9" rx="4" fill="${C.yellow}" ${S2}/><circle cy="24" r="6" fill="${C.ink}"/><circle cy="-28" r="5" fill="${C.yellow}" ${S2}/>`);
P.idcard = (w = 220) => {
  const h = w * 0.63, x0 = -w / 2, y0 = -h / 2;
  let s = `<rect x="${x0}" y="${y0}" width="${w}" height="${h}" rx="${w * 0.055}" fill="${C.white}" ${S}/>` +
    `<path d="M${x0} ${y0 + h * 0.26} V${y0 + w * 0.055} Q${x0} ${y0} ${x0 + w * 0.055} ${y0} H${-x0 - w * 0.055} Q${-x0} ${y0} ${-x0} ${y0 + w * 0.055} V${y0 + h * 0.26} Z" fill="${C.navy}" ${S}/>` +
    txt(0, y0 + h * 0.14, 'CREDENTIAL', w * 0.09, { fill: '#fff', weight: 700, extra: 'letter-spacing="2"' });
  const px = x0 + w * 0.07, pw = w * 0.28, py = y0 + h * 0.36, ph = h * 0.54;
  s += `<rect x="${px}" y="${py}" width="${pw}" height="${ph}" rx="${w * 0.03}" fill="${C.sky}" ${S2}/>` +
    `<circle cx="${px + pw / 2}" cy="${py + ph * 0.38}" r="${pw * 0.2}" fill="#8d5524"/><path d="M${px + pw * 0.14} ${py + ph} q${pw * 0.36} ${-ph * 0.6} ${pw * 0.72} 0 z" fill="#c8a165"/>`;
  [0.46, 0.62, 0.78].forEach((f, i) => { s += `<path d="M${x0 + w * 0.42} ${y0 + h * f} h${w * (i === 2 ? 0.3 : 0.48)}" stroke="${C.gray}" stroke-width="${w * 0.022}" stroke-linecap="round"/>`; });
  return s;
};
const FEDORA = `<path d="M-36 -238 q0 -40 36 -40 q36 0 36 40 z" fill="#3d405b" ${S2}/><rect x="-36" y="-252" width="72" height="9" fill="${C.ink}"/><ellipse cy="-236" rx="62" ry="9" fill="#3d405b" ${S2}/>`;
CAST.stranger = o => person({ skin: '#e0b48a', hair: '#333', hairStyle: 'short', top: '#b08d57', blazer: '#b08d57', pants: '#4a4e69', hat: FEDORA, seed: 10.2, ...o });
const refreshArrow = (u, r = 100) => {
  const a1 = (200 * Math.PI) / 180, ex = Math.cos(a1) * r, ey = Math.sin(a1) * r;
  const dx = -Math.sin(a1), dy = Math.cos(a1), nx = Math.cos(a1), ny = Math.sin(a1);
  const head = `${(ex + dx * 18).toFixed(1)},${(ey + dy * 18).toFixed(1)} ${(ex + nx * 11).toFixed(1)},${(ey + ny * 11).toFixed(1)} ${(ex - nx * 11).toFixed(1)},${(ey - ny * 11).toFixed(1)}`;
  return g(`rotate(${(u * 70).toFixed(2)})`, `<path d="M0 ${-r} A${r} ${r} 0 1 1 ${ex.toFixed(1)} ${ey.toFixed(1)}" fill="none" stroke="${C.teal}" stroke-width="8" stroke-linecap="round"/><polygon points="${head}" fill="${C.teal}"/>`);
};

// ---------- Series map tiles (used by the map and wrap-up scenes) ----------
function tilesView(u, cur, hl, label, start, popAt) {
  const xs = [205, 495, 785, 1075], y = 255;
  let s = op(fade(u, popAt(0)), `<path d="M${xs[0]} 398 H${xs[3]}" stroke="${C.ink}" stroke-width="5" stroke-dasharray="14 10" stroke-linecap="round"/>`);
  xs.forEach((x, k) => {
    const isCur = k === cur - 1 && u > hl, past = k < cur - 1;
    const fill = isCur ? C.yellow : past ? C.tealL : C.white;
    let tile = `<rect x="-118" y="-105" width="236" height="210" rx="22" fill="${fill}" stroke="${C.ink}" stroke-width="${isCur ? 5 : 3.5}"/>`;
    tile += `<circle cx="-92" cy="-80" r="20" fill="${past ? C.teal : C.navy}" ${S2}/>` + txt(-92, -79, String(k + 1), 20, { fill: '#fff', weight: 700 });
    tile += g('translate(0 -10)', seriesIcon(k, u));
    tile += txt(0, 80, SERIES[k], 26, { weight: 700 });
    if (past) tile += g('translate(92 -80)', P.check(18));
    const sc = isCur ? 1 + 0.06 * easeOut(prog(u, hl, 0.4)) : 1;
    s += pop(u, popAt(k), x, y, g(`scale(${sc.toFixed(4)})`, tile), 0.45);
  });
  if (u > hl) s += pop(u, hl + 0.2, xs[cur - 1], 120, chip(0, 0, label, { size: 20, fill: C.yellow }), 0.4);
  const p = easeInOut(prog(u, hl, 1.1)), pos = lerp(start, cur - 1, p), ax = xs[0] + (xs[1] - xs[0]) * pos;
  s += actor('alex', ax, 602, 0.62, { t: u, walk: p > 0 && p < 1, mood: 'happy', armR: p >= 1 ? -150 + wob(u, 1.5, 15) : -12 });
  return s;
}
SCENES.map = ({ local: u, L }) => {
  const n = partNo(), listing = n === 1 && L.length > 1;   // part one names the chunks aloud
  const popAt = k => (listing ? L[0] + 2.7 + k * 0.85 : 0.35 + k * 0.22);
  const hl = listing ? L[1] - 0.1 : L[0] + 0.9;
  return bgSky(u) + tilesView(u, n, hl, 'You are here', n === 1 ? -0.9 : n - 2, popAt);
};

// ---------- Wrap-up (parts 1–3): what this part covered, then what's next ----------
const WRAP = {
  1: [['A sponsor with a real need', 'sponsor'], ['Proof of citizenship', 'citizenship'], ['A complete, honest SF 86', 'complete and honest'], ['Releases + fingerprints', 'releases'], ['An FSO review', 'FSO review']],
  2: [['Temporary eligibility, if you qualify', 'temporary'], ['Record checks', 'record checks'], ['Interviews', 'interviews']],
  3: [['The 13 guidelines', 'guidelines'], ['The whole person', 'whole person'], ['Due process, if there are concerns', 'due process']],
};
SCENES.next = c => {
  const { local: u, L } = c, n = partNo(), items = WRAP[n] || [];
  let s = bgSky(u);
  const o0 = 1 - fade(u, L[1] - 0.1, 0.4);
  if (o0 > 0) {
    const w = 600, h = 96 + items.length * 54;
    let inner = `<path d="M${-w / 2} ${-h / 2 + 50} V${-h / 2 + 18} Q${-w / 2} ${-h / 2} ${-w / 2 + 18} ${-h / 2} H${w / 2 - 18} Q${w / 2} ${-h / 2} ${w / 2} ${-h / 2 + 18} V${-h / 2 + 50} Z" fill="${C.navy}" ${S}/>` +
      txt(0, -h / 2 + 26, `Part ${n}: ${SERIES[n - 1]}`, 24, { fill: '#fff', weight: 700 });
    items.forEach(([lab, key], i) => {
      const y = -h / 2 + 88 + i * 54, tk = sayAt(c, 0, key);
      inner += `<rect x="${-w / 2 + 32}" y="${y - 16}" width="32" height="32" rx="8" fill="${C.white}" ${S2}/>` + txt(-w / 2 + 84, y + 1, lab, 23, { anchor: 'start', weight: 600, fill: u > tk ? C.ink : C.gray });
      if (u > tk) inner += g(at(-w / 2 + 48, y, popS(u, tk, 0.3)), `<path d="M-9 0 L-2 8 L11 -9" fill="none" stroke="${C.green}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>`);
    });
    s += op(o0, pop(u, 0.3, 780, 300, card(w, h, inner), 0.5));
    s += op(o0, actor('alex', 230, 572, 0.95, { t: u, mood: 'happy', look: 5, armR: u > Math.max(...items.map(([, k]) => sayAt(c, 0, k))) + 0.6 ? -150 + wob(u, 1.5, 15) : -14 }));
  }
  if (u > L[1] - 0.2) s += op(fade(u, L[1] - 0.1, 0.4), tilesView(u, n + 1, L[1] + 0.6, 'Up next', n - 1, k => L[1] - 0.1 + k * 0.1));
  return s;
};

// ---------- End card (per part) ----------
const END_SOURCES = {
  1: ['32 CFR Part 117 (NISPOM) · DCSA Voice of Industry (Jan 2025; Jun and Jul 2026)', 'Adapted from the “High Level PCL Process” map'],
  2: ['32 CFR Part 117 (NISPOM) · Federal Personnel Vetting Investigative Standards (2022)', 'ISL 2021-02 · DCSA Voice of Industry (Jun and Oct 2026)'],
  3: ['SEAD 4 · 32 CFR Parts 117, 147 and 155', 'DCSA Voice of Industry (Jan 2025)'],
  4: ['32 CFR Part 117 (NISPOM) · ISL 2021-02 · SEAD 3 · SEAD 7 · SF 312', 'DCSA Voice of Industry (Aug 2026)'],
};
SCENES.end = ({ local: u }) => {
  const n = partNo();
  let s = bgNight(u + 40, [120, 1160, 50, 430]);
  s += pop(u, 0.2, 640, 105, txt(0, 0, n < 4 ? `Next: Part ${n + 1}, ${SERIES[n]}` : 'That’s the whole series!', 50, { fill: C.yellow, weight: 700 }), 0.5);
  s += op(fade(u, 0.6), txt(640, 178, 'Questions? Ask your FSO.', 36, { fill: C.cream, weight: 700 }));
  let y = 240;
  if (n === 2 || n === 4) { s += op(fade(u, 0.8), txt(640, y, 'Verify a DCSA investigator: 878-274-1186', 24, { fill: C.yellow, weight: 600 })); y += 52; }
  s += op(fade(u, 1.0), END_SOURCES[n].map((l, i) => txt(640, y + i * 30, (i ? '' : 'Sources: ') + l, 20, { fill: '#cfe3f7', weight: 500 })).join(''));
  s += op(fade(u, 1.4), txt(640, y + 92, 'Unofficial training aid · Not legal advice · Current as of October 2026', 19, { fill: '#9fb8d6', weight: 500 }));
  s += `<ellipse cx="640" cy="652" rx="130" ry="20" fill="rgba(255,255,255,0.12)"/>`;
  s += slideIn(u, 0.5, 640, 860, 640, 650, actor('alex', 0, 0, 0.8, { t: u, armR: -150 + wob(u, 1.6, 22), mood: 'happy' }), 0.6);
  return s;
};

// ---------- Step 1: citizenship + FSO starts the request ----------
SCENES.s1 = c => {
  const { local: u, L } = c;
  const hand = L[0] + 2.2, handEnd = hand + 1.3;
  const click = L[2] + 2.4, launch = click + 0.35, land = launch + 1.5;
  let s = bgRoom(u, { window: false });
  s += g(at(470, 440), P.desk(270));
  const pressed = u > click && u < click + 0.35;
  const screen1 = txt(0, -24, 'Investigation', 16, { weight: 600 }) + txt(0, -4, 'request', 16, { weight: 600 }) +
    `<rect x="-46" y="14" width="92" height="28" rx="14" fill="${pressed ? C.yellow : u > click ? C.green : C.teal}" ${S2}/>` +
    txt(0, 29, u > click ? 'Sent!' : 'Send', 15, { fill: '#fff', weight: 700 });
  s += g(at(470, 404), P.monitor(170, screen1));
  const tap = u > click - 0.6 && u < click + 0.3 ? wob(u, 3, 6) : 0;
  const fsoHold = u > handEnd && u < L[2] + 0.2;
  s += actor('fso', 265, 552, 0.95, { t: u, armR: -62 + tap, mood: 'happy', look: 4, armL: fsoHold ? 70 : 12, propL: fsoHold ? inHand(70, P.passport(40), 0, -8) : '' });
  s += nameTag(265, 285, 'FSO');
  s += op(fade(u, handEnd + 0.3) * (1 - fade(u, L[2] + 0.3, 0.4)),
    `<g transform="translate(470 250)">${chip(0, 0, 'U.S. citizenship verified', { size: 18, fill: C.yellow })}</g>` + pop(u, handEnd + 0.4, 596, 250, P.check(16), 0.3));
  // documents can be checked in person or digitally
  const ways = span(u, L[1], L[2] + 0.1);
  if (ways > 0) {
    const tA = sayAt(c, 1, 'in person'), tB = sayAt(c, 1, 'digitally');
    let w = pop(u, tA, 600, 145, card(220, 96, g(at(-62, 0), P.passport(32)) + txt(26, 1, 'In person', 22, { weight: 700 })), 0.4);
    w += op(fade(u, tB - 0.2), txt(730, 147, 'or', 22, { weight: 600, fill: C.gray }));
    w += pop(u, tB, 860, 145, card(220, 96, g(at(-62, 0, 0.5), P.phone(56) + g(at(0, -4, 0.7), P.doc(50, 64, '', { lines: 3 }))) + txt(26, 1, 'Digitally', 22, { weight: 700 })), 0.4);
    s += op(ways, w);
  }
  // Alex, table, laptop
  s += `<rect x="860" y="452" width="180" height="16" rx="5" fill="#b5835a" ${S}/><rect x="940" y="468" width="20" height="74" fill="#9c6b45" ${S2}/>`;
  const got = u > land;
  const lscreen = got
    ? `<rect x="-92" y="-54" width="184" height="24" fill="${C.teal}"/>` + txt(0, -41, 'eApp  ·  NBIS', 15, { fill: '#fff', weight: 700 }) +
      g(at(-50, 4, 0.7), P.envelope(60)) + txt(26, -4, "You're", 17, { weight: 600 }) + txt(26, 18, 'invited!', 17, { weight: 600 })
    : txt(0, 0, 'Inbox', 18, { fill: C.gray });
  s += g(at(950, 452), P.laptop(210, lscreen));
  const offering = u > L[0] + 1.2 && u < hand;
  const mood = !got ? (u > L[2] ? 'neutral' : 'happy') : u < land + 0.6 ? 'surprised' : 'happy';
  s += actor('alex', 1135, 552, 0.95, { t: u, mood, look: -5, armL: offering ? 80 : got ? 40 + wob(u, 1.2, 4) : 14, propL: offering ? inHand(80, P.passport(40), 0, -8) : '' });
  s += nameTag(1135, 285, 'Alex');
  s += flyer(u, hand, handEnd - hand, [1060, 390], [720, 170], [345, 400], P.passport(44), 360);
  if (u > launch && u < land) {
    const p = easeInOut(prog(u, launch, land - launch)), [x, y] = qb([470, 330], [720, 60], [950, 380], p);
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
// lines: 0 intro, 1 sections, 2 look-back, 3 gather records, 4 honesty, 5 gaps, 6 releases + prints, 7 120 days, 8 PVQ, 9 five years
SCENES.s2 = c => {
  const { local: u, L } = c;
  let s = bgRoom(u, { window: false });
  const W = { x: 400, y: 104, w: 830, h: 470 }, cx = W.w / 2;
  const wp = popS(u, 0.25, 0.5);
  let win = `<rect x="0" y="0" width="${W.w}" height="${W.h}" rx="18" fill="${C.white}" ${S}/>` +
    `<path d="M0 18 Q0 0 18 0 H${W.w - 18} Q${W.w} 0 ${W.w} 18 V48 H0 Z" fill="${C.navy}" ${S}/>` +
    `<circle cx="26" cy="24" r="7" fill="${C.red}"/><circle cx="48" cy="24" r="7" fill="${C.yellow}"/><circle cx="70" cy="24" r="7" fill="${C.green}"/>` +
    txt(cx, 25, 'eApp', 22, { fill: '#fff', weight: 700 });
  win += op(fade(u, L[0] + 1.2), txt(cx, 86, 'SF 86 · Questionnaire for National Security Positions', 25, { weight: 600 }) + `<path d="M40 110 H${W.w - 40}" stroke="${C.light}" stroke-width="4"/>`);
  // the sections: listed (1), dimmed for the look-back (2), back while gathering records (3), dimmed for honesty (4), gone from (5)
  const rowsOp = u < L[2] ? 1 : u < L[3] ? lerp(1, 0.07, fade(u, L[2])) : u < L[4] ? lerp(0.07, 1, fade(u, L[3])) : u < L[5] ? lerp(1, 0.07, fade(u, L[4])) : lerp(0.07, 0, fade(u, L[5]));
  if (rowsOp > 0) {
    let rows = '';
    SF86_ROWS.forEach(([icon, label], k) => {
      const col = k % 2, row = Math.floor(k / 2), x = 70 + col * 390, y = 160 + row * 78;
      const a = L[1] + 0.2 + k * 0.55, done = L[3] + 0.6 + k * 0.3;
      rows += pop(u, a, x, y, P[icon](icon === 'globe' || icon === 'dollar' ? 20 : 40)) + op(fade(u, a + 0.1), txt(x + 40, y + 2, label, 23, { anchor: 'start', weight: 500 }));
      rows += op(fade(u, a), `<rect x="${x + 290}" y="${y - 15}" width="30" height="30" rx="7" fill="${C.white}" ${S2}/>`);
      if (u > done) rows += g(at(x + 305, y, popS(u, done, 0.3)), `<path d="M-9 0 L-2 8 L11 -9" fill="none" stroke="${C.green}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>`);
    });
    rows += op(fade(u, L[1] + 3.6), txt(cx, 400, '…and more', 22, { fill: C.gray, weight: 500 }));
    win += op(rowsOp, rows);
  }
  // look-back
  const lbO = span(u, L[2] + 0.1, L[3] - 0.2);
  if (lbO > 0) {
    const p = easeOut(prog(u, L[2] + 0.4, 1.2));
    let k = `<path d="M700 220 H${lerp(700, 140, p).toFixed(1)}" stroke="${C.ink}" stroke-width="6" stroke-linecap="round"/>`;
    if (p >= 1) k += `<path d="M160 205 L138 220 L160 235" fill="none" stroke="${C.ink}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>`;
    k += `<circle cx="700" cy="220" r="12" fill="${C.teal}" ${S2}/>` + txt(700, 254, 'Today', 20, { weight: 600 });
    k += op(fade(u, L[2] + 1.0), txt(420, 180, 'Most questions: 7–10 years back', 26, { weight: 700, fill: C.navy }));
    [[P.calendar('31', '', 54), ['Dates'], 'dates'], [P.house(48), ['Addresses'], 'addresses'], [actor('neighbor', 0, 32, 0.24, { t: u }), ['People who', 'can vouch for you'], 'people']].forEach(([icon, labs, key], j) => {
      const x = 230 + j * 190, a = sayAt(c, 2, key);
      k += pop(u, a, x, 335, icon, 0.4) + op(fade(u, a + 0.1), labs.map((l, i) => txt(x, 392 + i * 22, l, 19, { weight: 600 })).join(''));
    });
    win += op(lbO, k);
  }
  // honesty
  const hoO = span(u, L[4], L[5] - 0.1);
  if (hoO > 0) {
    let k = pop(u, L[4] + 0.25, cx, 215, P.stamp('COMPLETE + HONEST', C.teal, 40), 0.5, -8);
    k += pop(u, sayAt(c, 4, 'Leaving'), cx, 340, `<rect x="-250" y="-30" width="500" height="60" rx="30" fill="#fde2dc" ${S2}/>` + g(at(-212, 0, 0.8), P.cross(24)) + txt(18, 2, 'Omissions can hurt more than the issue', 22, { fill: C.red, weight: 600 }), 0.45);
    win += op(hoO, k);
  }
  // gaps in the timeline
  const gpO = span(u, L[5] + 0.1, L[6] - 0.3);
  if (gpO > 0) {
    const y = 250, found = sayAt(c, 5, 'gaps') + 0.3, filled = sayAt(c, 5, 'every');
    let k = txt(cx, 160, 'Your timeline', 24, { weight: 700, fill: C.navy });
    [[120, 330, 'Home 1'], [410, 710, 'Home 2']].forEach(([a, b, lab]) => { k += `<rect x="${a}" y="${y - 24}" width="${b - a}" height="48" rx="12" fill="${C.tealL}" ${S2}/>` + txt((a + b) / 2, y + 1, lab, 20, { weight: 600 }); });
    if (u > found) {
      const fp = easeOut(prog(u, filled, 0.6));
      k += `<rect x="334" y="${y - 24}" width="72" height="48" rx="10" fill="${fp > 0 ? `rgba(87,167,115,${(0.85 * fp).toFixed(3)})` : 'none'}" stroke="${fp >= 1 ? C.ink : C.red}" stroke-width="3" ${fp >= 1 ? '' : 'stroke-dasharray="8 6"'}/>`;
      k += op(1 - fade(u, filled, 0.3), pop(u, found, 370, 186, chip(0, 0, 'Gap?', { size: 20, fill: '#fde2dc', color: C.red }), 0.35));
      k += pop(u, filled + 0.5, 370, y, P.check(16), 0.3);
      k += pop(u, filled + 0.8, cx, 350, chip(0, 0, 'Every date and address filled in', { size: 21, fill: '#bfe8cc' }), 0.4);
    }
    if (u > L[5] + 0.3 && u < filled) {
      const mp = easeInOut(prog(u, L[5] + 0.3, found - L[5] - 0.3));
      k += g(at(lerp(130, 372, mp), y - 6), P.magnifier(26));
    }
    win += op(gpO, k);
  }
  // releases + fingerprints, then the 120-day clock
  const fb = u < L[6] - 0.2 ? 0 : fade(u, L[6] - 0.1, 0.4) * (1 - fade(u, L[9], 0.4));
  if (fb > 0) {
    let b = g(at(210, 270), P.doc(190, 230, 'Release forms', { head: C.purple, lines: 4 }));
    const sig = prog(u, L[6] + 0.5, 1.6);
    b += `<path d="M150 348 c12 -26 22 -26 26 -6 s12 18 22 -10 s14 -18 20 4 s16 10 26 -8" fill="none" stroke="${C.navy}" stroke-width="4" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="${(1 - sig).toFixed(3)}"/>`;
    if (sig > 0 && sig < 1) b += g(at(150 + sig * 94, 336 - Math.sin(sig * 18) * 10), P.pen(62));
    b += txt(210, 410, 'Sign', 22, { weight: 600 });
    const scan = prog(u, L[6] + 1.4, 1.8);
    b += g(at(630, 290), P.scanner(220, scan));
    b += op(0.35 + 0.65 * fade(u, L[6] + 1.4, 0.3), g(at(630, 290, 0.95), P.fingerprint(32, scan > 0 ? C.navy : C.gray)));
    if (scan > 0 && scan < 1) b += `<rect x="552" y="${(256 + scan * 64).toFixed(1)}" width="156" height="5" rx="2.5" fill="${C.green}" opacity=".9"/>`;
    b += pop(u, L[6] + 3.3, 735, 232, P.check(22), 0.35);
    b += txt(630, 410, 'Electronic fingerprints', 22, { weight: 600 });
    b += pop(u, sayAt(c, 7, '120'), 405, 205, P.calendar('120', 'days', 100), 0.45);
    b += op(fade(u, sayAt(c, 7, '120') + 0.3), txt(405, 290, 'each', 20, { weight: 700, fill: C.navy }));
    b += pop(u, sayAt(c, 7, "don't let"), 410, 332, chip(0, 0, "Don't let it sit!", { size: 18, fill: C.yellow }), 0.4);
    win += op(fb, b);
  }
  // PVQ: most look-backs drop to five years
  if (u > L[9]) {
    const bp = easeOut(prog(u, sayAt(c, 9, 'five'), 0.7));
    let k = txt(cx, 165, 'Most look-back periods', 26, { weight: 700, fill: C.navy });
    k += txt(150, 240, 'SF 86', 24, { weight: 700, anchor: 'end' }) + `<rect x="180" y="216" width="460" height="48" rx="12" fill="${C.tealL}" ${S2}/>` + txt(410, 241, '7–10 years', 22, { weight: 600 });
    k += txt(150, 330, 'PVQ', 24, { weight: 700, anchor: 'end' }) + `<rect x="180" y="306" width="${(230 * bp).toFixed(1)}" height="48" rx="12" fill="${C.yellow}" ${S2}/>`;
    k += op(fade(u, sayAt(c, 9, 'five') + 0.5), txt(295, 331, '5 years', 22, { weight: 700 }));
    win += op(fade(u, L[9] + 0.1, 0.4), k);
  }
  s += g(`translate(${W.x + cx} ${W.y + W.h / 2}) scale(${wp.toFixed(4)}) translate(${-cx} ${-W.h / 2})`, win);
  if (u > L[8]) s += pop(u, L[8] + 0.2, 205, 178, g(`rotate(${(-5 + wob(u, 0.9, 2.5)).toFixed(2)})`, P.sticky(220, 118, ['Phasing in:', 'the PVQ', 'replaces SF 86'])), 0.45);
  const point = [L[1], L[2], L[4], L[5]].some(a => u > a && u < a + 1.6);
  const holding = u > L[3] + 0.2 && u < L[4];
  s += actor('alex', 205, 560, 0.95, {
    t: u, look: 5, mood: 'happy', armR: point ? -118 + wob(u, 2, 5) : -20,
    armL: holding ? 30 : u > L[8] + 0.3 && u < L[8] + 2.2 ? 160 + wob(u, 2, 5) : 12,
    propL: holding ? g(at(-18, 4, 0.55, 12), P.folder(90, '', C.yellow)) : '',
  });
  s += nameTag(205, 290, 'Alex');
  if (holding) s += op(fade(u, L[3] + 0.2), chip(105, 500, 'My records', { size: 17 }));
  return s;
};

// ---------- Step 4: DCSA checks the package ----------
SCENES.s4 = ({ local: u, L }) => {
  const a = L[0], miss = a + 3.4, back0 = a + 4.3, fix = a + 5.4, fwd0 = a + 6.4, ok = a + 7.5;
  let s = bgRoom(u, { window: false });
  s += actor('fso', 130, 552, 0.85, { t: u, mood: u > miss && u < ok ? 'neutral' : 'happy', look: 4 });
  s += nameTag(130, 310, 'FSO');
  const fixing = u > fix - 0.2 && u < fwd0;
  s += actor('alex', 290, 552, 0.85, { t: u, mood: 'happy', look: 4, armR: fixing ? -70 + wob(u, 3, 8) : -12, propR: fixing ? inHand(-70, P.pen(50), 0, 0) : '' });
  s += nameTag(290, 310, 'Alex');
  s += g(at(1100, 480, 0.85), govBuilding(230, 'DCSA'));
  const rows = ['SF 86', 'Signed releases', 'Fingerprints'], MISS = 2;
  let pnl = card(400, 240, `<path d="M-200 -102 Q-200 -120 -182 -120 H182 Q200 -120 200 -102 V-78 H-200 Z" fill="${C.navy}" ${S}/>` + txt(0, -99, 'DCSA package check', 21, { fill: '#fff', weight: 600 }));
  rows.forEach((r, i) => {
    const y = -40 + i * 56;
    if (i === MISS && u > L[1]) pnl += op(fade(u, L[1] + 0.2), `<rect x="-186" y="${y - 23}" width="372" height="46" rx="12" fill="${C.yellow}" opacity=".55"/>`);
    pnl += txt(-160, y, r, 22, { anchor: 'start', weight: 500 });
    const tOk = i === MISS ? ok : a + 1.3 + i * 0.5;
    if (i === MISS && u > miss && u < ok) pnl += g(at(140, y, popS(u, miss, 0.3)), P.cross(18)) + op(fade(u, miss + 0.2), txt(60, y, 'Missing!', 18, { fill: C.red, weight: 700 }));
    else if (u > tOk) pnl += g(at(140, y, popS(u, tOk, 0.3)), P.check(18));
    else pnl += `<rect x="124" y="${y - 16}" width="32" height="32" rx="8" fill="${C.white}" ${S2}/>`;
  });
  s += pop(u, 0.2, 690, 270, pnl, 0.5);
  s += flyer(u, back0, 1.0, [690, 300], [470, 120], [250, 360], P.folder(80, '', C.yellow), -20);
  if (u > back0 + 1.0 && u < fwd0) s += g(at(210, 360), P.folder(80, '', C.yellow));
  s += flyer(u, fwd0, 1.0, [250, 360], [470, 120], [690, 300], P.folder(80, '', C.yellow), 20);
  s += op(1 - fade(u, L[1], 0.3), pop(u, ok + 0.2, 690, 440, chip(0, 0, 'Complete', { size: 22, fill: '#bfe8cc' }), 0.4));
  // why fingerprint timing matters
  if (u > L[1]) {
    s += pop(u, L[1] + 0.9, 690, 118, chip(0, 0, 'A common reason for rejection', { size: 19, fill: C.yellow }), 0.4);
    const t2 = L[1] + 3.6;
    let k = pop(u, t2, 600, 450, `<circle r="34" fill="${C.white}" ${S2}/>` + P.fingerprint(22), 0.4) + pop(u, t2 + 0.4, 790, 450, `<circle r="34" fill="${C.white}" ${S2}/>` + P.folder(40, '', C.yellow), 0.4);
    k += op(fade(u, t2 + 0.6), `<path d="M642 450 H748" stroke="${C.ink}" stroke-width="4" stroke-dasharray="7 6"/>` + txt(600, 503, 'Fingerprints', 18, { weight: 600 }) + txt(790, 503, 'Form released', 18, { weight: 600 }));
    k += pop(u, t2 + 1.0, 695, 418, chip(0, 0, 'close together', { size: 16, fill: C.cream }), 0.35);
    s += k;
  }
  return s;
};

// ---------- Step 5: temporary eligibility ----------
SCENES.s5 = c => {
  const { local: u, L, D } = c;
  let s = bgRoom(u, { window: false });
  s += g(at(190, 300), P.hourglass(prog(u, 0, D), 170));
  s += op(fade(u, 0.8), tag(190, 425, 'Investigation running…'));
  const handoff = L[1] + 3.0, held = u > handoff + 0.8;
  s += actor('alex', 1060, 555, 0.95, { t: u, mood: held ? 'happy' : 'neutral', look: -5, armR: held ? -120 : -14 });
  s += nameTag(1060, 290, 'Alex');
  const tcard = card(330, 190,
    txt(0, -42, 'TEMPORARY', 38, { weight: 700, fill: C.teal, extra: 'letter-spacing="2"' }) + txt(0, 2, 'eligibility', 26, { weight: 600 }) +
    op(fade(u, L[0] + 5.8), txt(0, 48, '(you may hear "interim")', 19, { weight: 500, fill: C.gray })), { dashed: true, stroke: C.teal });
  if (u < handoff) s += pop(u, L[0] + 2.8, 620, 260, tcard, 0.5);
  else { const p = easeInOut(prog(u, handoff, 0.9)); s += g(at(lerp(620, 1192, p), lerp(260, 402, p), lerp(1, 0.42, p), lerp(0, 8, p)), tcard); }
  // early checks
  if (u > L[1] && u < L[2] + 0.4) {
    let e = pop(u, L[1] + 0.3, 520, 450, P.doc(50, 62, '', { lines: 3 }), 0.35) + pop(u, L[1] + 0.6, 600, 450, P.fingerprint(24), 0.35) + pop(u, L[1] + 0.9, 680, 446, P.magnifier(18), 0.35);
    e += op(fade(u, L[1] + 1.0), txt(600, 510, 'your form + early checks', 18, { weight: 600 }));
    e += op(fade(u, handoff + 1.0), tag(890, 250, 'Start sooner', { fill: C.yellow }));
    s += op(1 - fade(u, L[2], 0.4), e);
  }
  // not getting it is not a denial
  const nd = span(u, L[2] + 0.1, L[3] - 0.1);
  if (nd > 0) {
    s += op(nd, pop(u, sayAt(c, 2, 'not getting'), 620, 250, g('rotate(-3)', P.sticky(320, 96, ['No temporary?', 'That is NOT a denial.'])), 0.45));
    s += op(nd, pop(u, sayAt(c, 2, 'wait'), 190, 488, tag(0, 0, 'Wait for the final decision', { fill: C.yellow }), 0.4));
  }
  // what temporary Secret doesn't cover
  const lm = span(u, L[3] + 0.1, L[4] - 0.1);
  if (lm > 0) {
    let inner = txt(0, -78, 'Temporary Secret does not cover', 22, { weight: 700 });
    [['Restricted Data', 'Restricted'], ['COMSEC', 'COMSEC'], ['NATO information', 'NATO']].forEach(([lab, key], i) => {
      const y = -30 + i * 44, a = sayAt(c, 3, key);
      inner += op(fade(u, a, 0.3), g(at(-130, y), P.cross(14)) + txt(-104, y + 1, lab, 21, { anchor: 'start', weight: 600 }));
    });
    inner += op(fade(u, sayAt(c, 3, 'Those need')), txt(0, 96, 'These need a final decision', 18, { weight: 600, fill: C.gray }));
    s += op(lm, pop(u, L[3] + 0.2, 620, 260, card(420, 236, inner), 0.45));
  }
  // one-year cap
  if (u > L[4]) {
    s += pop(u, sayAt(c, 4, 'a year'), 620, 235, P.calendar('1', 'year max', 120, C.purple), 0.45);
    s += pop(u, sayAt(c, 4, 'unless'), 620, 365, chip(0, 0, 'unless DCSA approves', { size: 20, fill: C.cream }), 0.4);
  }
  return s;
};

// ---------- Step 6: background investigation ----------
SCENES.s6 = c => {
  const { local: u, L } = c;
  let s = bgRoom(u, { window: false });
  const armR = -58 + wob(u, 0.5, 4);
  s += actor('investigator', 250, 555, 0.95, { t: u, mood: 'happy', look: 5, armR, propR: inHand(armR, P.magnifier(24), 0, -10) });
  s += nameTag(250, 290, 'DCSA investigator', C.cream);
  // records
  if (u < L[1] + 0.4) {
    const rc = (x, icon, label, a) => pop(u, a, x, 250, card(230, 150, g(at(0, -22), icon) + txt(0, 44, label, 22, { weight: 600 })), 0.45);
    s += op(1 - fade(u, L[1], 0.4), rc(720, P.handcuffs(1.3), 'Criminal history', sayAt(c, 0, 'criminal')) + rc(990, P.dollar(28), 'Credit', sayAt(c, 0, 'credit')));
  }
  // depth by level
  const ti = span(u, L[1] + 0.1, L[2] - 0.1);
  if (ti > 0) {
    let k = op(fade(u, L[1] + 0.4), txt(860, 110, 'How deep it goes', 26, { weight: 700 }));
    [[740, 120, 'Secret', 'Moderate tier', 'moderate', C.tealL], [980, 230, 'Top Secret', 'High tier', 'high-tier', C.teal]].forEach(([x, H, lvl, tier, key, col]) => {
      const a = sayAt(c, 1, key), h = H * easeOut(prog(u, a, 0.6));
      if (h > 0) k += `<rect x="${x - 80}" y="${(450 - h).toFixed(1)}" width="160" height="${h.toFixed(1)}" rx="10" fill="${col}" ${S}/>`;
      k += op(fade(u, a + 0.4), txt(x, 450 - H / 2, lvl, 22, { weight: 700, fill: col === C.teal ? '#fff' : C.ink }) + chip(x, 450 - H - 28, tier, { size: 19, fill: C.yellow }));
    });
    s += op(ti, k);
  }
  // what the checks can include
  const ck = span(u, L[2] + 0.1, L[3] - 0.1);
  if (ck > 0) {
    let k = pop(u, L[2] + 0.4, 850, 140, chip(0, 0, 'Checks can include', { size: 21, fill: C.cream }), 0.4);
    [[P.db(40), ['National', 'databases'], 'national'], [P.fingerprint(26), ['Fingerprints'], 'fingerprints'], [P.dollar(26), ['Credit'], 'credit'],
      [P.cap(52), ['Education'], 'education'], [P.briefcase(48), ['Employment'], 'employment']].forEach(([icon, labs, key], i) => {
      k += iconTile(u, sayAt(c, 2, key), 520 + i * 165, 255, icon, labs);
    });
    s += op(ck, k);
  }
  // interviews
  const ivO = span(u, L[3], L[4] - 0.1);
  if (ivO > 0) {
    let iv = '';
    [['alex', 760, 'You', 'you'], ['neighbor', 930, 'References', 'references'], ['cow1', 1100, 'People who know you', 'people']].forEach(([who, x, lab, key]) => {
      const a = sayAt(c, 3, key) - 0.2;
      iv += slideIn(u, a, x, 760, x, 555, actor(who, 0, 0, 0.72, { t: u, mood: 'happy', talk: u > a + 0.5 && u < a + 1.8 }), 0.5);
      iv += op(fade(u, a + 0.3), txt(x, 342, lab, 17, { weight: 600 }));
    });
    iv += pop(u, sayAt(c, 3, 'Top Secret'), 930, 190, chip(0, 0, 'Top Secret: a deeper look', { size: 20, fill: C.yellow }), 0.4);
    s += op(ivO, iv);
  }
  // the interview: explain, keep your SF 86 handy, say "I don't know"
  if (u > L[4]) {
    const holdArm = 52;
    s += slideIn(u, L[4] + 0.1, 900, 760, 650, 555, actor('alex', 0, 0, 0.9, {
      t: u, mood: 'happy', look: -5, talk: (u > L[4] + 0.6 && u < L[4] + 2.4) || (u > L[5] + 0.3 && u < L[5] + 3),
      armL: holdArm, propL: inHand(holdArm, P.doc(54, 68, 'SF 86', { head: C.navy, lines: 2, size: 12 }), 0, -6),
    }), 0.5);
    const tips = [['Your chance to explain', L[4] + 0.6], ['Keep a copy of your SF 86', sayAt(c, 4, 'Keep a copy')], ["Don't know? Say so.", sayAt(c, 4, "if you don't")]];
    let k = '';
    tips.forEach(([tip, a], i) => { k += pop(u, a, 1010, 170 + i * 80, card(340, 60, txt(0, 1, tip, 21, { weight: 700 }), { fill: i === 2 ? C.yellow : C.cream }), 0.4); });
    s += op(1 - fade(u, L[5], 0.4), k);
    s += pop(u, L[5] + 0.4, 520, 250, P.bubble(250, 66, txt(0, 0, 'Prompt + honest', 22, { weight: 700, fill: C.teal }), 'right'), 0.4);
  }
  return s;
};

// ---------- Step 6, continued: who's who, and waiting ----------
SCENES.s6b = c => {
  const { local: u, L } = c;
  let s = bgRoom(u, { window: false });
  // investigator (lines 0-2)
  const invO = 1 - fade(u, L[3] - 0.3, 0.4);
  if (invO > 0) {
    const showing = u > L[0] + 0.6 && u < L[1] + 0.8, armR = showing ? -100 : -14;
    let k = actor('investigator', 230, 555, 0.95, { t: u, mood: 'happy', look: 5, armR, propR: showing ? inHand(armR, P.idcard(64), 0, -16) : '' });
    k += nameTag(230, 290, 'DCSA investigator', C.cream);
    if (u > L[2]) k += pop(u, sayAt(c, 2, 'gather'), 230, 228, chip(0, 0, 'Gathers facts', { size: 18, fill: C.yellow }), 0.4);
    s += op(invO, k);
  }
  // credential card
  const cr = span(u, L[0] + 0.9, L[1] - 0.1);
  if (cr > 0) s += op(cr, pop(u, L[0] + 0.9, 640, 240, P.idcard(250), 0.45) + pop(u, L[0] + 1.8, 640, 375, chip(0, 0, 'Official DCSA credential card', { size: 19, fill: C.cream }), 0.4));
  // Alex, unsure (lines 0-1)
  const alexO = 1 - fade(u, L[2] - 0.1, 0.4);
  if (alexO > 0) {
    let k = actor('alex', 1060, 555, 0.95, { t: u, mood: u > L[1] && u < L[1] + 3 ? 'worried' : 'neutral', look: -5 });
    k += nameTag(1060, 290, 'Alex');
    k += op(1 - fade(u, L[1] + 4, 0.3), pop(u, L[1] + 0.5, 1130, 232, `<circle r="26" fill="${C.yellow}" ${S2}/>` + txt(0, 2, '?', 32, { weight: 700 }), 0.35));
    s += op(alexO, k);
  }
  // verify by phone
  const ph = span(u, sayAt(c, 1, 'DCSA can verify'), L[2] - 0.2);
  if (ph > 0) s += op(ph, pop(u, sayAt(c, 1, 'DCSA can verify'), 640, 250, card(400, 180,
    g(at(-145, 10, 0.75), P.phone(56)) + txt(40, -44, 'Verify an investigator', 22, { weight: 600 }) +
    txt(40, 4, '878-274-1186', 36, { weight: 700, fill: C.navy }) + txt(40, 48, 'DCSA', 18, { weight: 600, fill: C.gray }), { fill: C.cream }), 0.5));
  // facts go to an adjudicator, who decides
  const adO = span(u, L[2] + 0.1, L[3] - 0.3);
  if (adO > 0) {
    let k = slideIn(u, L[2] + 0.1, 1400, 555, 1060, 555, actor('adjudicator', 0, 0, 0.95, { t: u, mood: 'happy', look: -5 }), 0.6);
    k += op(fade(u, L[2] + 0.5), nameTag(1060, 290, 'Adjudicator'));
    const tf = sayAt(c, 2, 'report');
    k += flyer(u, tf - 0.6, 1.3, [300, 380], [640, 150], [950, 430], P.folder(90, 'Facts', C.yellow), 0);
    if (u > tf + 0.7) k += g(at(950, 430), P.folder(90, 'Facts', C.yellow));
    k += pop(u, sayAt(c, 2, "don't decide"), 640, 200, card(330, 70, txt(0, 1, "Investigators don't decide", 21, { weight: 700, fill: C.red }), { fill: '#fde2dc' }), 0.4);
    k += pop(u, tf + 0.9, 1060, 228, chip(0, 0, 'Decides', { size: 18, fill: C.yellow }), 0.4);
    s += op(adO, k);
  }
  // waiting: case status online, keep your FSO posted
  if (u > L[3] - 0.2) {
    s += slideIn(u, L[3], -150, 555, 230, 555, actor('alex', 0, 0, 0.95, { t: u, mood: 'happy', look: 5, talk: u > L[4] + 0.8 && u < L[4] + 5 }), 0.6);
    s += op(fade(u, L[3] + 0.4), nameTag(230, 290, 'Alex'));
  }
  const st = span(u, L[3] + 0.2, L[4] - 0.1);
  if (st > 0) {
    let scr = `<rect x="-141" y="-84" width="282" height="32" fill="${C.teal}"/>` + txt(0, -67, 'Case status', 18, { fill: '#fff', weight: 700 });
    [['Submitted', 'done'], ['Investigation', 'now'], ['Adjudication', 'later']].forEach(([lab, state], i) => {
      const y = -28 + i * 40;
      scr += state === 'done' ? g(at(-112, y), P.check(13)) : `<circle cx="-112" cy="${y}" r="13" fill="${state === 'now' ? C.yellow : C.white}" ${S2}/>`;
      scr += txt(-88, y + 1, lab, 19, { anchor: 'start', weight: state === 'later' ? 500 : 700, fill: state === 'later' ? C.gray : C.ink });
    });
    let k = `<rect x="550" y="452" width="300" height="16" rx="5" fill="#b5835a" ${S}/><rect x="690" y="468" width="20" height="74" fill="#9c6b45" ${S2}/>`;
    k += pop(u, L[3] + 0.4, 700, 452, P.laptop(300, scr), 0.45);
    k += pop(u, sayAt(c, 3, 'Individual'), 700, 222, chip(0, 0, 'Individual Engagement Platform', { size: 19, fill: C.cream }), 0.4);
    s += op(st, k);
  }
  if (u > L[4]) {
    s += slideIn(u, L[4] + 0.1, 1400, 555, 1090, 555, actor('fso', 0, 0, 0.95, { t: u, mood: 'happy', look: -5 }), 0.6);
    s += op(fade(u, L[4] + 0.5), nameTag(1090, 290, 'FSO'));
    s += reportArrow(u, L[4] + 0.8);
    s += iconTile(u, sayAt(c, 4, 'foreign trip'), 560, 290, P.plane(56), ['A foreign trip']);
    s += iconTile(u, sayAt(c, 4, 'new arrest'), 760, 290, P.handcuffs(1.2), ['A new arrest']);
    s += pop(u, sayAt(c, 4, 'Reporting rules'), 660, 160, chip(0, 0, 'Reporting rules already apply', { size: 20, fill: C.yellow }), 0.4);
  }
  return s;
};

// ---------- Step 7: adjudication and the 13 guidelines ----------
const GUIDE_COLS = [
  [['Allegiance to the U.S.', 'allegiance'], ['Foreign influence', 'foreign influence'], ['Foreign preference', 'foreign preference'], ['Sexual behavior', 'sexual'], ['Personal conduct', 'personal']],
  [['Financial considerations', 'financial'], ['Alcohol consumption', 'alcohol'], ['Drug involvement', 'drug'], ['Psychological conditions', 'psychological']],
  [['Criminal conduct', 'criminal'], ['Handling protected info', 'handling'], ['Outside activities', 'outside'], ['Use of IT', 'use of information']],
];
const balanceStack = (u, items, col) => items.map(([lab, a], i) => {
  if (u < a) return '';
  const drop = a < 0 ? 0 : (1 - easeOut(prog(u, a, 0.45))) * -220;
  return g(`translate(0 ${(-14 - i * 24 + drop).toFixed(1)})`, `<rect x="-58" y="-11" width="116" height="22" rx="11" fill="${col}" ${S2}/>` + txt(0, 1, lab, 13, { fill: '#fff', weight: 700 }));
}).join('');
const balanceTilt = (u, good, bad) => good.reduce((t, [, a]) => t - 3.2 * (a < 0 ? 1 : easeOut(prog(u, a, 0.5))), 0) + bad.reduce((t, [, a]) => t + 5 * (a < 0 ? 1 : easeOut(prog(u, a, 0.5))), 0);
SCENES.s7 = c => {
  const { local: u, L } = c;
  let s = bgRoom(u, { window: false });
  s += actor('adjudicator', 160, 555, 0.9, { t: u, mood: 'happy', look: 5, armR: u > L[0] + 1 && u < L[0] + 3 ? -100 : -14 });
  s += nameTag(160, 305, 'Adjudicator');
  const t13 = sayAt(c, 0, '13');
  s += op(1 - fade(u, L[1], 0.4), pop(u, sayAt(c, 0, 'Security Executive'), 320, 330, P.book('SEAD 4', '', 92), 0.45, 6));
  // the grid: three groups, read aloud in lines 1-3
  const gridO = u < L[4] ? 1 : u < L[5] ? lerp(1, 0.18, fade(u, L[4])) : lerp(0.18, 0, fade(u, L[5]));
  if (gridO > 0) {
    let grid = op(fade(u, t13), txt(805, 112, 'SEAD 4: 13 adjudicative guidelines', 26, { weight: 700 }));
    let k = 0;
    GUIDE_COLS.forEach((col, ci) => {
      const x = 520 + ci * 285, line = ci + 1;
      if (u > L[line] - 0.2 && u < L[line + 1]) grid += op(span(u, L[line] - 0.2, L[line + 1] - 0.3, 0.3), `<rect x="${x - 146}" y="146" width="292" height="${col.length * 62 + 18}" rx="18" fill="none" stroke="${C.yellow}" stroke-width="5" stroke-dasharray="12 8"/>`);
      col.forEach(([name, key], r) => {
        const y = 186 + r * 62, named = sayAt(c, line, key, 0.05), lit = u > named, flash = lit && u < named + 1.2;
        const sc = lit ? 1 + 0.08 * Math.max(0, 1 - (u - named) / 0.35) : 1;
        const cardS = `<rect x="-135" y="-23" width="270" height="46" rx="12" fill="${flash ? C.yellow : lit ? '#d9f0ec' : C.white}" ${S2}/><circle cx="-110" r="14" fill="${C.purple}"/>` +
          txt(-110, 1, String.fromCharCode(65 + k), 15, { fill: '#fff', weight: 700 }) + txt(-88, 1, name, 17, { anchor: 'start', weight: 600 });
        grid += pop(u, t13 + 0.5 + k * 0.25, x, y, g(`scale(${sc.toFixed(4)})`, cardS), 0.3);
        k++;
      });
    });
    s += op(gridO, grid);
  }
  // each guideline: conditions that raise a concern, conditions that can ease it
  const zo = span(u, L[4] + 0.1, L[5] - 0.1);
  if (zo > 0) {
    let inner = txt(0, -98, 'Each guideline lists', 24, { weight: 700 });
    const half = (x, fill, head, icon, a) => op(fade(u, a, 0.3), `<rect x="${x - 125}" y="-72" width="250" height="172" rx="14" fill="${fill}" ${S2}/>` + g(at(x - 92, -40), icon) +
      txt(x + 14, -39, head, 20, { weight: 700 }) + [0, 1, 2].map(i => `<path d="M${x - 100} ${-2 + i * 32} h${170 - i * 30}" stroke="${C.gray}" stroke-width="5" stroke-linecap="round"/>`).join(''));
    inner += half(-140, '#fde2dc', 'Raise a concern', `<path d="M0 -14 L13 8 H-13 Z" fill="${C.red}" ${S2}/>`, sayAt(c, 4, 'raise'));
    inner += half(140, '#e6f5eb', 'Can ease it', P.check(13), sayAt(c, 4, 'and conditions'));
    s += op(zo, pop(u, L[4] + 0.2, 805, 300, card(580, 260, inner), 0.45));
  }
  // whole person
  if (u > L[5]) {
    const good = [['Work', L[5] + 0.6], ['Family', L[5] + 1.1], ['Community', L[5] + 1.6]], bad = [['1 bad moment', sayAt(c, 5, 'single')]];
    s += op(fade(u, L[5] + 0.1, 0.5), g(at(600, 250), P.balance(balanceTilt(u, good, bad), balanceStack(u, good, C.green), balanceStack(u, bad, C.red))));
    s += pop(u, L[5] + 0.3, 600, 112, tag(0, 0, 'The whole person'), 0.4);
    s += pop(u, sayAt(c, 5, "doesn't"), 1040, 250, card(300, 96, txt(0, -16, "Doesn't automatically", 21, { weight: 700 }) + txt(0, 16, 'mean a denial', 21, { weight: 700 }), { fill: C.cream }), 0.45);
  }
  return s;
};

// ---------- Step 7, continued: how the whole person is weighed ----------
SCENES.s7b = c => {
  const { local: u, L } = c;
  let s = bgRoom(u, { window: false });
  s += actor('adjudicator', 160, 555, 0.9, { t: u, mood: 'happy', look: 5 });
  s += nameTag(160, 305, 'Adjudicator');
  const good = [['Work', -1], ['Family', -1], ['Community', -1], ['Time', sayAt(c, 1, 'Time')], ['Honesty', sayAt(c, 1, 'honesty')], ['Change', sayAt(c, 1, 'changed')]];
  const bad = [['1 bad moment', -1]];
  s += g(at(600, 250), P.balance(balanceTilt(u, good, bad), balanceStack(u, good, C.green), balanceStack(u, bad, C.red)));
  s += op(1 - fade(u, L[3], 0.3), tag(600, 112, 'The whole person'));
  // the factors
  const fo = span(u, L[0] + 0.2, L[1] - 0.1);
  if (fo > 0) {
    let inner = txt(0, -112, 'Adjudicators weigh', 22, { weight: 700 });
    [['How serious', 'serious'], ['How recent, how often', 'recent'], ['Your age at the time', 'age'], ['Voluntary?', 'voluntary'], ["Have you changed?", "you've changed"]].forEach(([lab, key], i) => {
      const y = -66 + i * 44, a = sayAt(c, 0, key);
      inner += txt(-140, y + 1, lab, 20, { anchor: 'start', weight: 600, fill: u > a ? C.ink : C.gray });
      inner += u > a ? g(at(126, y, popS(u, a, 0.3)), P.check(13)) : `<circle cx="126" cy="${y}" r="13" fill="${C.white}" ${S2}/>`;
    });
    s += op(fo, pop(u, L[0] + 0.3, 1030, 280, card(340, 270, inner), 0.45));
  }
  // doubt goes to national security
  const dO = span(u, L[2] + 0.1, L[3] - 0.1);
  if (dO > 0) {
    let inner = txt(0, -78, 'Any real doubt?', 24, { weight: 700 }) + op(fade(u, sayAt(c, 2, 'national')), g(at(0, 4, 0.75), shield(C.navy)) + txt(0, 74, 'National security comes first', 18, { weight: 700, fill: C.navy }));
    s += op(dO, pop(u, L[2] + 0.2, 1030, 270, card(340, 220, inner), 0.45));
  }
  // favorable, sometimes with conditions
  s += pop(u, L[3] + 0.5, 600, 112, P.stamp('FAVORABLE', C.green, 40), 0.45, -6);
  s += op(1 - fade(u, L[4], 0.3), pop(u, sayAt(c, 3, 'Some are'), 1030, 260, card(320, 100, txt(0, -18, 'Some: approved with', 21, { weight: 700 }) + txt(0, 16, 'conditions + monitoring', 21, { weight: 700 }), { fill: C.cream }), 0.45));
  // conditional eligibility: monitored through continuous vetting
  if (u > L[4]) {
    s += pop(u, L[4] + 0.3, 1030, 136, chip(0, 0, 'Conditional eligibility', { size: 21, fill: C.yellow }), 0.4);
    s += pop(u, sayAt(c, 4, 'monitor'), 1030, 280, P.radar(u, 96), 0.45);
    s += pop(u, sayAt(c, 4, 'continuous vetting'), 1030, 410, chip(0, 0, 'Monitored through continuous vetting', { size: 17, fill: C.cream }), 0.4);
    s += op(fade(u, sayAt(c, 4, 'instead')), txt(1030, 450, 'instead of starting due process', 17, { weight: 600, fill: C.gray }));
  }
  return s;
};

// ---------- Step 9: you respond to the SOR ----------
SCENES.s9 = ({ local: u, L }) => {
  let s = bgRoom(u, { window: false });
  s += g(at(420, 440), P.desk(260));
  s += g(at(400, 425, 1, -4), P.doc(90, 30, '', { lines: 0 }));
  const writing = u < L[2];
  s += actor('alex', 225, 552, 0.95, { t: u, mood: 'neutral', look: 4, armR: writing ? -72 + wob(u, 3, 6) : -14, propR: writing ? inHand(-72, P.pen(46)) : '' });
  s += nameTag(225, 285, 'Alex');
  s += op(1 - fade(u, L[1], 0.4), pop(u, L[0] + 2.2, 520, 250, chip(0, 0, 'Want the clearance? Respond.', { size: 20, fill: C.yellow }), 0.4));
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
  if (u > L[2]) s += pop(u, L[2] + 0.6, 870, 470, P.signpost(u > L[2] + 1.4 && u < L[2] + 3.4, u > L[2] + 3.4), 0.5);
  return s;
};

// ---------- Step 9, continued: written record or hearing ----------
SCENES.s9b = c => {
  const { local: u, L } = c;
  let s = bgRoom(u, { window: false });
  const burden = u > L[2] && u < L[3];
  s += actor('alex', 200, 555, 0.95, {
    t: u, mood: 'neutral', look: 5, talk: u > sayAt(c, 1, 'testify') && u < sayAt(c, 1, 'testify') + 1.6,
    armR: burden ? -36 : -14, propR: burden ? inHand(-36, `<path d="M-12 10 q12 -20 24 0" fill="none" stroke="${C.ink}" stroke-width="7"/><path d="M-30 10 h60 l9 46 h-78 z" fill="${C.ink}"/>` + txt(0, 36, 'BURDEN', 12, { fill: '#fff', weight: 700 }), 0, 0) : '',
  });
  s += nameTag(200, 290, 'Alex');
  // written record
  const wr = span(u, L[0] + 0.1, L[1] - 0.2);
  if (wr > 0) {
    let k = pop(u, L[0] + 0.3, 640, 140, chip(0, 0, 'Written record', { size: 22, fill: C.cream }), 0.4);
    k += pop(u, sayAt(c, 0, 'copy'), 520, 300, P.doc(180, 210, "Government's evidence", { head: C.navy, lines: 4, size: 13 }), 0.45);
    k += pop(u, sayAt(c, 0, '30 days'), 760, 290, P.calendar('30', 'days', 110), 0.45);
    k += pop(u, sayAt(c, 0, 'your own'), 1010, 310, g('translate(14 12) rotate(6)', P.doc(150, 180, '', { lines: 3 })) + P.doc(150, 180, 'Your response', { head: C.teal, lines: 4, size: 14 }), 0.45);
    s += op(wr, k);
  }
  // hearing
  const hr = span(u, L[1] + 0.1, L[3] - 0.2);
  if (hr > 0) {
    let k = pop(u, L[1] + 0.3, 640, 140, chip(0, 0, 'Hearing', { size: 22, fill: C.cream }), 0.4);
    k += op(fade(u, L[1] + 0.2), actor('judge', 640, 420, 0.72, { t: u, mood: 'neutral' }) + g(at(640, 470), P.bench(280, 100)) + nameTag(640, 482 - 60, 'Administrative judge'));
    const dc = sayAt(c, 1, 'Department Counsel') - 0.8;
    k += slideIn(u, dc, 1400, 555, 1070, 555, actor('attorney', 0, 0, 0.9, { t: u, mood: 'neutral', look: -4, talk: u > dc + 0.8 && u < dc + 2.6 }), 0.6);
    k += op(fade(u, dc + 0.5), nameTag(1070, 300, 'Department Counsel'));
    const youO = 1 - fade(u, L[2], 0.3);
    [['Testify', 'testify'], ['Call witnesses', 'witnesses'], ['Present documents', 'documents']].forEach(([lab, key], i) => {
      k += op(youO, pop(u, sayAt(c, 1, key), 410, 200 + i * 52, chip(0, 0, lab, { size: 19, fill: C.yellow }), 0.35));
    });
    if (u > L[2]) {
      k += pop(u, L[2] + 0.3, 410, 190, chip(0, 0, 'Burden of persuasion: on you', { size: 19, fill: '#fde2dc', color: C.red }), 0.4);
      k += pop(u, sayAt(c, 2, 'explain'), 410, 244, chip(0, 0, 'Explain the circumstances', { size: 19, fill: C.yellow }), 0.35);
      k += pop(u, sayAt(c, 2, 'show'), 410, 298, chip(0, 0, 'Show what has changed', { size: 19, fill: C.yellow }), 0.35);
    }
    s += op(hr, k);
  }
  // lawyer or representative; no response means denial
  if (u > L[3]) {
    s += slideIn(u, L[3] + 0.2, 1400, 555, 640, 555, actor('rep', 0, 0, 0.9, { t: u, mood: 'happy', look: -4, armL: 20, propL: inHand(20, P.briefcase(46), 0, 10) }), 0.7);
    s += op(fade(u, L[3] + 0.9), nameTag(640, 300, 'Lawyer or representative'));
    s += pop(u, sayAt(c, 3, "If you don't"), 1010, 330, P.stamp('NO RESPONSE = DENIED', C.red, 28), 0.45, -6);
  }
  return s;
};

// ---------- Part 4, step 1: eligible is not access; the initial briefing ----------
SCENES.access = c => {
  const { local: u, L } = c;
  let s = bgRoom(u, { window: false });
  s += actor('alex', 220, 560, 0.95, { t: u, mood: 'happy', look: 5, armR: u > L[1] + 5.0 && u < L[1] + 6.8 ? -70 + wob(u, 3, 6) : -14 });
  s += nameTag(220, 292, 'Alex');
  s += op(1 - fade(u, L[1], 0.4), pop(u, L[0] + 0.9, 220, 225, chip(0, 0, 'ELIGIBLE', { size: 22, fill: '#bfe8cc' }), 0.4));
  if (u < L[1] + 0.4) {
    let e = pop(u, sayAt(c, 0, 'Being eligible'), 820, 520, P.door() + g(at(0, -140), P.lock(44, C.yellow)), 0.5);
    e += pop(u, sayAt(c, 0, "isn't"), 520, 330, `<circle r="40" fill="${C.white}" ${S}/>` + txt(0, 3, '≠', 60, { weight: 700, fill: C.red, font: 'DejaVu Sans' }), 0.4);
    e += op(fade(u, sayAt(c, 0, 'access')), txt(820, 540, 'Access', 24, { weight: 700 }));
    s += op(1 - fade(u, L[1], 0.4), e);
  }
  if (u > L[1]) {
    const pointing = (u > L[1] + 2.0 && u < L[1] + 4.5) || (u > L[2] && u < L[2] + 5);
    s += slideIn(u, L[1] + 0.2, 1400, 560, 1120, 560, actor('fso', 0, 0, 0.95, { t: u, mood: 'happy', look: -5, armL: pointing ? 120 : 12 }), 0.6);
    s += op(fade(u, L[1] + 0.6), nameTag(1120, 292, 'FSO'));
    const rows = [['Threats, including insider threats', 'threats'], ['Counterintelligence', 'counterintelligence'], ['How classification works', 'how classification'], ['Your reporting duties', 'reporting']];
    let board = P.board('Initial security briefing', [], 430, 236);
    rows.forEach(([r, key], i) => {
      const a = sayAt(c, 2, key), y = -118 + 68 + i * 38;
      board += u > a ? op(fade(u, a, 0.3), `<circle cx="${-215 + 28}" cy="${y}" r="7" fill="${C.teal}"/>` + txt(-215 + 46, y + 1, r, 19, { anchor: 'start', weight: 500 }))
        : `<circle cx="${-215 + 28}" cy="${y}" r="7" fill="${C.light}"/><path d="M${-215 + 46} ${y} h${220 - i * 30}" stroke="${C.light}" stroke-width="8" stroke-linecap="round"/>`;
    });
    s += pop(u, L[1] + 2.0, 810, 205, board, 0.45);
    let k = '', doc = P.doc(170, 200, 'SF 312', { head: C.purple, lines: 3 });
    const sig = prog(u, L[1] + 5.0, 1.4);
    doc += `<path d="M-50 70 c10 -20 18 -20 22 -5 s10 14 18 -8 s12 -14 16 3 s12 8 20 -6" fill="none" stroke="${C.navy}" stroke-width="3.5" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="${(1 - sig).toFixed(3)}"/>`;
    k += pop(u, L[1] + 4.3, 470, 330, doc, 0.45);
    k += pop(u, L[1] + 6.6, 1120, 230, chip(0, 0, 'Witness', { size: 18, fill: C.cream }), 0.35);
    k += pop(u, sayAt(c, 1, 'lasts for life'), 470, 468, chip(0, 0, 'Lasts for life', { size: 20, fill: C.yellow }), 0.4);
    s += op(1 - fade(u, L[2] - 0.1, 0.4), k);
  }
  return s;
};

// ---------- Part 4, step 2: need-to-know and refresher training ----------
SCENES.ntk = ({ local: u, L }) => {
  let s = bgRoom(u, { window: false });
  s += actor('alex', 220, 560, 0.95, { t: u, mood: 'happy', look: 5 });
  s += nameTag(220, 292, 'Alex');
  const open = [0, 0, easeOut(prog(u, L[0] + 2.4, 0.6))];
  s += pop(u, L[0] + 0.3, 840, 520, P.cabinet(open, ['Program A', 'Program B', 'Your project']), 0.45);
  s += op(fade(u, L[0] + 0.6), g(at(988, 284), P.lock(34, C.yellow)) + g(at(988, 372), P.lock(34, C.yellow)));
  s += flyer(u, L[0] + 1.2, 1.1, [300, 380], [560, 200], [920, 430], P.key(1.2), 360);
  s += pop(u, L[0] + 2.4, 840, 180, chip(0, 0, 'Need-to-know', { size: 20, fill: C.yellow }), 0.4);
  if (u > L[1]) {
    s += pop(u, L[1] + 0.2, 500, 230, refreshArrow(u) + P.calendar('12', 'months', 110), 0.45);
    s += pop(u, L[1] + 1.0, 500, 380, chip(0, 0, 'Refresher training', { size: 20, fill: C.yellow }), 0.4);
  }
  return s;
};

// ---------- Part 4, step 3: continuous vetting and FBI Rap Back ----------
SCENES.cv = c => {
  const { local: u, L } = c;
  let s = bgRoom(u, { window: false });
  s += actor('alex', 240, 560, 0.95, { t: u, mood: 'happy', look: 5 }) + nameTag(240, 292, 'Alex');
  if (u < L[1] + 0.4) {
    let r = pop(u, sayAt(c, 0, 'continuous'), 760, 270, P.radar(u, 125), 0.5);
    r += op(fade(u, sayAt(c, 0, 'continuous') + 0.4), tag(760, 425, 'Continuous vetting'));
    r += pop(u, sayAt(c, 0, 'automated'), 540, 160, chip(0, 0, 'Automated record checks', { size: 18, fill: C.cream }), 0.4);
    r += pop(u, sayAt(c, 0, 'updated form'), 1090, 240, P.calendar('5', 'years', 120), 0.45) + pop(u, sayAt(c, 0, 'updated form') + 0.3, 1090, 352, chip(0, 0, 'Update your form', { size: 18, fill: C.yellow }), 0.4);
    s += op(1 - fade(u, L[1], 0.4), r);
  }
  if (u > L[1]) {
    const t0 = L[1] + 0.3, tb = sayAt(c, 1, 'alerts'), td = sayAt(c, 1, 'DCSA');
    s += iconTile(u, t0, 480, 250, P.fingerprint(26), ['FBI Rap Back']);
    s += op(fade(u, tb - 0.5), `<path d="M535 250 H680" stroke="${C.ink}" stroke-width="5" stroke-linecap="round" stroke-dasharray="10 8"/><path d="M668 240 L682 250 L668 260" fill="none" stroke="${C.ink}" stroke-width="5" stroke-linecap="round"/>`);
    s += iconTile(u, tb, 740, 250, P.bell(u > tb ? wob(u, 2.2, 14) * Math.max(0, 1 - (u - tb) / 3) : 0), ['New criminal', 'record']);
    s += op(fade(u, td - 0.4), `<path d="M795 250 H900" stroke="${C.ink}" stroke-width="5" stroke-linecap="round" stroke-dasharray="10 8"/><path d="M888 240 L902 250 L888 260" fill="none" stroke="${C.ink}" stroke-width="5" stroke-linecap="round"/>`);
    s += slideIn(u, td, 1060, 760, 1060, 470, g('scale(0.72)', govBuilding(230, 'DCSA')), 0.6);
    s += pop(u, sayAt(c, 1, 'near real'), 1060, 175, chip(0, 0, 'Near real time', { size: 20, fill: C.yellow }), 0.4);
  }
  return s;
};

// ---------- Part 4, step 4: what you report ----------
const reportCast = u => actor('alex', 220, 560, 0.95, { t: u, mood: 'happy', look: 5 }) + nameTag(220, 292, 'Alex') +
  actor('fso', 1090, 560, 0.95, { t: u, mood: 'happy', look: -5 }) + nameTag(1090, 292, 'FSO');
SCENES.report = c => {
  const { local: u, L } = c;
  let s = bgRoom(u, { window: false });
  s += actor('alex', 220, 560, 0.95, { t: u, mood: 'happy', look: 5, talk: u > L[0] + 1 && u < L[0] + 4 }) + nameTag(220, 292, 'Alex');
  s += slideIn(u, 0.2, 1400, 560, 1090, 560, actor('fso', 0, 0, 0.95, { t: u, mood: 'happy', look: -5 }), 0.6) + op(fade(u, 0.6), nameTag(1090, 292, 'FSO'));
  s += reportArrow(u, L[0] + 0.6);
  const o0 = 1 - fade(u, L[1] + 0.5, 0.4);
  if (o0 > 0) {
    let k = '';
    [[P.plane(56), ['Foreign travel'], 'foreign travel'], [P.globe(28), ['Foreign contacts'], 'contacts'], [P.dollar(28), ['Money trouble'], 'money'], [P.handcuffs(1.3), ['An arrest'], 'arrest']].forEach(([icon, labs, key], i) => {
      k += iconTile(u, sayAt(c, 0, key), 440 + i * 150, 270, icon, labs);
    });
    s += op(o0, k);
  }
  // personal foreign travel
  const tr = span(u, L[1] + 0.6, L[2] - 0.1);
  if (tr > 0) {
    let k = pop(u, L[1] + 0.8, 490, 255, card(230, 200, txt(0, -72, 'Before the trip', 21, { weight: 700 }) + g(at(0, 12), P.doc(84, 100, 'Itinerary', { head: C.teal, lines: 2, size: 13 })) + g(at(62, -22, 0.8), P.plane(50))), 0.45);
    k += pop(u, sayAt(c, 1, 'Report changes'), 805, 255, card(340, 200,
      txt(0, -72, 'Within 5 business days', 21, { weight: 700 }) + g(at(-110, 18), P.calendar('5', 'days', 92)) +
      txt(-42, -14, 'Changes to the trip', 18, { anchor: 'start', weight: 600 }) + txt(-42, 18, 'Unplanned day trips', 18, { anchor: 'start', weight: 600 }) + txt(-42, 42, 'to Canada or Mexico', 18, { anchor: 'start', weight: 600 })), 0.45);
    s += op(tr, k);
  }
  // official travel
  const of = span(u, L[2] + 0.1, L[3] - 0.1);
  if (of > 0) {
    let k = pop(u, L[2] + 0.3, 640, 250, card(360, 160, g(at(-120, 0), P.briefcase(60)) + g(at(-60, -26, 0.9), P.plane(50)) + txt(50, -14, 'Official travel', 22, { weight: 700 }) + txt(50, 18, 'for your contract', 22, { weight: 700 })), 0.45);
    k += pop(u, sayAt(c, 2, "doesn't"), 640, 362, chip(0, 0, 'No report needed', { size: 20, fill: '#bfe8cc' }), 0.4);
    s += op(of, k);
  }
  // foreign ties; suspected intelligence officers
  if (u > L[3]) {
    s += pop(u, sayAt(c, 3, 'close and continuing'), 495, 255, card(270, 210,
      g(at(-50, -24), P.globe(32)) + actor('neighbor', 30, 18, 0.3, { t: u }) + actor('cow2', 74, 18, 0.3, { t: u + 1 }) + txt(0, 52, 'Close, continuing', 20, { weight: 700 }) + txt(0, 76, 'foreign ties', 20, { weight: 700 })), 0.45);
    s += pop(u, sayAt(c, 3, 'foreign intelligence'), 795, 255, card(270, 210,
      actor('stranger', -10, 24, 0.36, { t: u, mood: 'neutral' }) + g(at(58, -50), `<circle r="20" fill="${C.yellow}" ${S2}/>` + txt(0, 2, '?', 26, { weight: 700 })) +
      txt(0, 52, 'Possible foreign', 20, { weight: 700 }) + txt(0, 76, 'intelligence officer', 20, { weight: 700 })), 0.45);
  }
  return s;
};
SCENES.report2 = c => {
  const { local: u, L } = c;
  let s = bgRoom(u, { window: false });
  s += reportCast(u);
  s += op(1 - fade(u, L[3], 0.4), reportArrow(u, -1));
  const row = (line, items, x0, dx) => {
    const o = span(u, L[line], line + 1 < L.length ? L[line + 1] - 0.1 : 1e9, 0.3);
    return o > 0 ? op(o, items.map(([icon, labs, key], i) => iconTile(u, sayAt(c, line, key), x0 + i * dx, 250, icon, labs)).join('')) : '';
  };
  s += row(0, [[g('translate(0 6)', P.lock(40, C.yellow)) + g('translate(20 -22)', `<circle r="12" fill="${C.red}" ${S2}/>` + txt(0, 1, '?', 15, { fill: '#fff', weight: 700 })), ['Attempts to get', 'classified info'], 'attempts'],
    [P.handcuffs(1.2), ['An arrest'], 'arrest'], [P.medcross(), ['Alcohol or drug', 'treatment'], 'alcohol'],
    [P.doc(46, 56, 'BK', { head: C.red, lines: 2, size: 11 }), ['Bankruptcy'], 'bankruptcy'], [P.calendar('120', 'days', 50), ['Debt 120+ days', 'past due'], 'debt']], 360, 150);
  s += row(1, [[P.globe(26), ['Applying for', 'foreign citizenship'], 'foreign citizenship'], [P.passport(32), ['Using a', 'foreign passport'], 'foreign passport'], [P.mic(), ['Media contacts', 'about classified'], 'media']], 460, 180);
  if (u > L[2] && u < L[3] + 0.4) s += op(1 - fade(u, L[3] - 0.1, 0.3), pop(u, L[2] + 0.3, 660, 140, chip(0, 0, 'Top Secret holders also report', { size: 20, fill: C.yellow }), 0.4));
  s += row(2, [[P.rings(), ['Marriage'], 'marriage'], [P.house(46), ['Cohabitation'], 'cohabitation'], [P.bank(), ['Foreign bank', 'accounts or', 'property'], 'foreign bank'], [P.ballot(), ['Voting in a', 'foreign election'], 'voting']], 420, 160);
  if (u > L[3]) {
    s += slideIn(u, L[3] + 0.1, 640, 760, 640, 560, actor('cow2', 0, 0, 0.85, { t: u, mood: 'neutral', look: 3 }), 0.5);
    s += op(fade(u, L[3] + 0.5), nameTag(640, 320, 'Cleared coworker'));
    s += pop(u, sayAt(c, 3, 'reportable'), 720, 250, `<circle r="22" fill="${C.red}" ${S2}/>` + txt(0, 2, '!', 28, { fill: '#fff', weight: 700 }), 0.35);
    const ap = easeOut(prog(u, sayAt(c, 3, 'tell'), 0.8));
    if (ap > 0) s += `<path d="M300 230 Q660 40 ${lerp(300, 1030, ap).toFixed(1)} ${lerp(230, 230, ap).toFixed(1)}" fill="none" stroke="${C.ink}" stroke-width="5" stroke-dasharray="12 10" stroke-linecap="round"/>`;
    s += pop(u, sayAt(c, 3, 'tell') + 0.5, 660, 138, chip(0, 0, 'Tell your FSO', { size: 22, fill: C.yellow }), 0.4);
  }
  return s;
};

// ---------- Part 4, step 5: changing jobs, and leaving ----------
SCENES.moves = c => {
  const { local: u, L } = c;
  let s = bgSky(u);
  s += g(at(160, 482, 0.62), officeBuilding(240, 250, 'Old job'));
  s += g(at(1120, 482, 0.62), officeBuilding(240, 250, 'New job', '#d9ead3'));
  const wp = prog(u, L[0] + 0.8, 2.8), ax = lerp(300, 800, easeInOut(wp)), walking = wp > 0 && wp < 1;
  const armR = -40, conf = sayAt(c, 0, 'confirms');
  s += actor('alex', ax, 560, 0.85, { t: u, walk: walking, mood: 'happy', look: 4, armR, propR: u < L[1] ? inHand(armR, g('scale(0.42)', shield()), 0, 14) : '' });
  s += nameTag(ax, 320, 'Alex');
  s += op(fade(u, L[0] + 2.6), actor('fso', 970, 560, 0.85, { t: u, mood: 'happy', look: -4 }) + nameTag(970, 320, 'New FSO'));
  const o0 = 1 - fade(u, L[1], 0.4);
  if (o0 > 0) {
    let k = pop(u, L[0] + 1.0, 500, 160, chip(0, 0, 'Eligibility generally comes with you', { size: 20, fill: C.cream }), 0.4);
    k += pop(u, sayAt(c, 0, 'reciprocity'), 640, 222, chip(0, 0, 'Reciprocity', { size: 22, fill: C.yellow }), 0.4);
    k += pop(u, conf, 900, 265, P.check(22), 0.35);
    k += pop(u, conf + 0.6, 1030, 160, chip(0, 0, 'Confirmed, not restarted', { size: 19, fill: '#bfe8cc' }), 0.4);
    s += op(o0, k);
  }
  if (u > L[1]) {
    s += pop(u, sayAt(c, 1, 'debriefs'), 370, 250, P.doc(170, 200, 'Debriefing', { head: C.navy, lines: 4 }), 0.45);
    const t312 = sayAt(c, 1, 'Your SF 312');
    s += pop(u, t312, 580, 250, P.doc(170, 200, 'SF 312', { head: C.purple, lines: 3 }), 0.45, 4);
    s += pop(u, t312 + 0.8, 580, 432, chip(0, 0, 'Obligations never end', { size: 20, fill: C.yellow }), 0.4);
    s += op(fade(u, t312 + 1.0), txt(580, 386, '∞', 48, { weight: 700, fill: C.purple, font: 'DejaVu Sans' }));
  }
  return s;
};
