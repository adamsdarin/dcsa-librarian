// Frame-exact cartoon engine: renderAt(t) draws the whole stage for time t (seconds).
// Everything is a pure function of t, so any frame can be rendered in any order.

// ---------- math ----------
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const lerp = (a, b, p) => a + (b - a) * p;
const prog = (t, a, d) => clamp((t - a) / d);
const easeOut = p => 1 - Math.pow(1 - p, 3);
const easeInOut = p => (p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2);
const easeBack = p => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(p - 1, 3) + c1 * Math.pow(p - 1, 2); };
const popS = (t, a, d = 0.45) => { const p = prog(t, a, d); return p <= 0 ? 0 : easeBack(p); };
const fade = (t, a, d = 0.4) => easeOut(prog(t, a, d));
const wob = (t, f = 1, a = 1, ph = 0) => Math.sin(t * f * Math.PI * 2 + ph) * a;

// ---------- palette ----------
const C = {
  ink: '#2b2d42', navy: '#1d3557', teal: '#2a9d8f', tealL: '#8fd3c8', yellow: '#e9c46a',
  orange: '#f4a261', red: '#e76f51', cream: '#fdf6e3', white: '#ffffff', sky: '#dff1f7',
  gray: '#8d99ae', light: '#edf2f4', green: '#57a773', purple: '#6a4c93', pink: '#ff8fa3',
  wall: '#fbeed7', floor: '#e3c9a0', paper: '#fffdf7',
};
const S = `stroke="${C.ink}" stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round"`;
const S2 = `stroke="${C.ink}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"`;

// ---------- svg helpers ----------
const g = (tr, inner, extra = '') => `<g transform="${tr}" ${extra}>${inner}</g>`;
const at = (x, y, s = 1, r = 0) => `translate(${x.toFixed(2)} ${y.toFixed(2)}) rotate(${r.toFixed(2)}) scale(${s.toFixed(4)})`;
const op = (o, inner) => (o <= 0 ? '' : o >= 1 ? inner : `<g opacity="${o.toFixed(3)}">${inner}</g>`);
function pop(t, a, x, y, inner, d = 0.45, r = 0) { const s = popS(t, a, d); return s <= 0 ? '' : g(at(x, y, s, r), inner); }
function slideIn(t, a, x0, y0, x1, y1, inner, d = 0.6) {
  const p = prog(t, a, d); if (p <= 0) return '';
  const e = easeOut(p); return g(at(lerp(x0, x1, e), lerp(y0, y1, e)), inner);
}
function txt(x, y, s, size = 22, o = {}) {
  const { fill = C.ink, weight = 600, anchor = 'middle', font = 'Fredoka', extra = '' } = o;
  return `<text x="${x}" y="${y}" font-family="${font}, sans-serif" font-weight="${weight}" font-size="${size}" fill="${fill}" text-anchor="${anchor}" dominant-baseline="middle" ${extra}>${s}</text>`;
}
function chip(x, y, label, o = {}) {
  const { fill = C.cream, color = C.ink, size = 20, pad = 14 } = o;
  const w = label.length * size * 0.56 + pad * 2, h = size + 16;
  return `<rect x="${x - w / 2}" y="${y - h / 2}" width="${w}" height="${h}" rx="${h / 2}" fill="${fill}" ${S2}/>` + txt(x, y + 1, label, size, { fill: color });
}
// Point on a quadratic bezier
function qb(p0, p1, p2, u) {
  const a = (1 - u) * (1 - u), b = 2 * (1 - u) * u, c = u * u;
  return [a * p0[0] + b * p1[0] + c * p2[0], a * p0[1] + b * p1[1] + c * p2[1]];
}

// ---------- characters ----------
// Feet at the origin, about 250 px tall at scale 1. Arm angles in degrees: 0 = hanging,
// positive swings the hand outward-left for armL; negative outward-right for armR.
function person(o) {
  const {
    t = 0, skin = '#c68642', hair = '#2b1d14', hairStyle = 'curly', top = C.teal, pants = '#264653',
    mood = 'happy', armL = 12, armR = -12, walk = false, glasses = false, blazer = null, tie = null,
    propL = '', propR = '', talk = false, robe = null, hat = null, look = 0, seed = 0,
  } = o;
  const legA = walk ? Math.sin(t * 9) * 24 : 0;
  const bob = walk ? -Math.abs(Math.sin(t * 9)) * 5 : wob(t, 0.45, 1.6, seed);
  const blink = ((t + seed * 1.3) * 1000) % 3900 < 130;
  const sleeve = blazer || top;
  let s = '';
  // legs
  if (!robe) {
    s += g(`rotate(${legA.toFixed(2)} -14 -78)`, `<rect x="-26" y="-80" width="22" height="76" rx="10" fill="${pants}" ${S}/><ellipse cx="-19" cy="-4" rx="17" ry="8" fill="${C.ink}"/>`);
    s += g(`rotate(${(-legA).toFixed(2)} 14 -78)`, `<rect x="4" y="-80" width="22" height="76" rx="10" fill="${pants}" ${S}/><ellipse cx="19" cy="-4" rx="17" ry="8" fill="${C.ink}"/>`);
  } else {
    s += `<path d="M-46 -150 L-58 -4 L58 -4 L46 -150 Z" fill="${robe}" ${S}/>`;
  }
  // arms (behind torso is fine for the back arm; we draw both after torso for readability)
  const arm = (side, ang, prop) => {
    const sx = side * 40;
    return g(`rotate(${ang.toFixed(2)} ${sx} -150)`,
      `<rect x="${sx - 11}" y="-156" width="22" height="74" rx="11" fill="${robe || sleeve}" ${S}/>` +
      `<circle cx="${sx}" cy="-80" r="12" fill="${skin}" ${S}/>` + (prop ? g(`translate(${sx} -80)`, prop) : ''));
  };
  // torso
  s += `<rect x="-44" y="-164" width="88" height="96" rx="28" fill="${robe || blazer || top}" ${S}/>`;
  if (blazer && !robe) {
    s += `<path d="M-16 -163 L0 -128 L16 -163 Z" fill="${C.white}" ${S2}/>`;
    if (tie) s += `<path d="M0 -140 L-6 -128 L0 -100 L6 -128 Z" fill="${tie}" ${S2}/>`;
  }
  if (robe) s += `<path d="M-14 -163 L0 -140 L14 -163 Z" fill="${C.white}" ${S2}/>`;
  s += arm(-1, armL, propL) + arm(1, armR, propR);
  // head
  const hx = 0, hy = -206;
  s += `<circle cx="-41" cy="${hy + 2}" r="9" fill="${skin}" ${S}/><circle cx="41" cy="${hy + 2}" r="9" fill="${skin}" ${S}/>`;
  s += `<circle cx="${hx}" cy="${hy}" r="42" fill="${skin}" ${S}/>`;
  s += hairSvg(hairStyle, hair, hy);
  // face
  const ex = 15, ey = hy - 4;
  if (blink) {
    s += `<path d="M${-ex - 5 + look} ${ey} h10 M${ex - 5 + look} ${ey} h10" ${S}/>`;
  } else {
    for (const sx of [-ex, ex]) {
      s += `<ellipse cx="${sx + look}" cy="${ey}" rx="5" ry="6.5" fill="${C.ink}"/><circle cx="${sx + look + 1.6}" cy="${ey - 2.2}" r="1.8" fill="#fff"/>`;
    }
  }
  if (mood === 'worried') s += `<path d="M${-ex - 8} ${ey - 16} L${-ex + 6} ${ey - 12} M${ex + 8} ${ey - 16} L${ex - 6} ${ey - 12}" ${S2}/>`;
  if (mood === 'surprised') s += `<path d="M${-ex - 7} ${ey - 16} q7 -6 14 0 M${ex - 7} ${ey - 16} q7 -6 14 0" fill="none" ${S2}/>`;
  if (glasses) s += `<g fill="none" ${S2}><circle cx="${-ex + look}" cy="${ey}" r="11"/><circle cx="${ex + look}" cy="${ey}" r="11"/><path d="M${-ex + 11 + look} ${ey} h${2 * ex - 22}"/></g>`;
  s += `<circle cx="-25" cy="${hy + 12}" r="7" fill="${C.pink}" opacity=".45"/><circle cx="25" cy="${hy + 12}" r="7" fill="${C.pink}" opacity=".45"/>`;
  const my = hy + 20;
  if (talk) {
    const open = 3 + Math.abs(Math.sin(t * 13)) * 7;
    s += `<ellipse cx="${look}" cy="${my}" rx="9" ry="${open.toFixed(2)}" fill="#7a2e2e" ${S2}/>`;
  } else if (mood === 'happy') {
    s += `<path d="M${-13 + look} ${my - 3} Q${look} ${my + 13} ${13 + look} ${my - 3} Z" fill="#7a2e2e" ${S2}/>`;
  } else if (mood === 'worried') {
    s += `<path d="M${-10 + look} ${my + 4} Q${look} ${my - 5} ${10 + look} ${my + 4}" fill="none" ${S}/>`;
  } else if (mood === 'surprised') {
    s += `<ellipse cx="${look}" cy="${my + 2}" rx="7" ry="9" fill="#7a2e2e" ${S2}/>`;
  } else {
    s += `<path d="M${-10 + look} ${my} h20" ${S}/>`;
  }
  if (hat) s += hat;
  return g(`translate(0 ${bob.toFixed(2)})`, s);
}

function hairSvg(style, col, hy) {
  if (style === 'curly') {
    let s = '';
    for (let a = 190; a <= 350; a += 20) {
      const r = (a * Math.PI) / 180;
      s += `<circle cx="${(Math.cos(r) * 36).toFixed(1)}" cy="${(hy + Math.sin(r) * 36).toFixed(1)}" r="15" fill="${col}" ${S2}/>`;
    }
    return s + `<circle cx="0" cy="${hy - 30}" r="18" fill="${col}"/>`;
  }
  if (style === 'bob') {
    return `<path d="M-46 ${hy + 22} Q-52 ${hy - 50} 0 ${hy - 48} Q52 ${hy - 50} 46 ${hy + 22} L34 ${hy + 22} Q38 ${hy - 14} 12 ${hy - 26} Q-20 ${hy - 10} -34 ${hy + 22} Z" fill="${col}" ${S}/>`;
  }
  if (style === 'short') {
    return `<path d="M-42 ${hy - 2} Q-44 ${hy - 50} 0 ${hy - 46} Q44 ${hy - 50} 42 ${hy - 2} Q30 ${hy - 26} 0 ${hy - 26} Q-30 ${hy - 26} -42 ${hy - 2} Z" fill="${col}" ${S}/>`;
  }
  if (style === 'bun') {
    return `<circle cx="0" cy="${hy - 50}" r="17" fill="${col}" ${S}/>` +
      `<path d="M-42 ${hy} Q-44 ${hy - 50} 0 ${hy - 46} Q44 ${hy - 50} 42 ${hy} Q26 ${hy - 30} 0 ${hy - 28} Q-26 ${hy - 30} -42 ${hy} Z" fill="${col}" ${S}/>`;
  }
  if (style === 'bald') {
    return `<path d="M-43 ${hy + 4} q2 -22 12 -26 M43 ${hy + 4} q-2 -22 -12 -26" stroke="${col}" stroke-width="9" fill="none" stroke-linecap="round"/>`;
  }
  if (style === 'spiky') {
    return `<path d="M-42 ${hy - 4} L-36 ${hy - 44} L-22 ${hy - 32} L-12 ${hy - 56} L2 ${hy - 36} L14 ${hy - 58} L22 ${hy - 34} L38 ${hy - 46} L42 ${hy - 4} Q20 ${hy - 26} -42 ${hy - 4} Z" fill="${col}" ${S}/>`;
  }
  return '';
}

// Cast
const CAST = {
  alex: o => person({ skin: '#b87a4b', hair: '#2b1d14', hairStyle: 'curly', top: C.teal, pants: '#264653', seed: 0, ...o }),
  fso: o => person({ skin: '#f1c27d', hair: '#8d4a2b', hairStyle: 'bob', blazer: C.navy, glasses: true, pants: '#3d405b', seed: 1.7, ...o }),
  investigator: o => person({ skin: '#8d5524', hair: '#555', hairStyle: 'short', top: '#c8a165', blazer: '#c8a165', tie: C.red, pants: '#6b705c', seed: 2.3, ...o }),
  adjudicator: o => person({ skin: '#e0ac69', hair: '#4a3728', hairStyle: 'bun', top: C.purple, pants: '#3d405b', glasses: true, seed: 3.1, ...o }),
  attorney: o => person({ skin: '#a0522d', hair: '#1b1b1b', hairStyle: 'spiky', blazer: '#3d405b', tie: C.teal, pants: '#3d405b', seed: 4.2, ...o }),
  judge: o => person({ skin: '#ffdbac', hair: '#bbb', hairStyle: 'bald', robe: '#22223b', seed: 5.5, ...o }),
};
function actor(name, x, y, s, o = {}, flip = false) {
  return g(`translate(${x.toFixed(2)} ${y.toFixed(2)}) scale(${(flip ? -s : s).toFixed(4)} ${s.toFixed(4)})`, CAST[name](o));
}
function nameTag(x, y, label, fill = C.cream) { return chip(x, y, label, { fill, size: 19 }); }

// ---------- props (drawn centered on the origin) ----------
const P = {
  envelope: (w = 64) => { const h = w * 0.66; return `<rect x="${-w / 2}" y="${-h / 2}" width="${w}" height="${h}" rx="4" fill="${C.white}" ${S}/><path d="M${-w / 2} ${-h / 2} L0 ${h * 0.1} L${w / 2} ${-h / 2}" fill="none" ${S}/>`; },
  doc: (w = 120, h = 150, title = '', o = {}) => {
    const { fill = C.paper, head = C.teal, lines = 4, size = 16 } = o;
    let s = `<rect x="${-w / 2}" y="${-h / 2}" width="${w}" height="${h}" rx="8" fill="${fill}" ${S}/>`;
    if (title) s += `<rect x="${-w / 2}" y="${-h / 2}" width="${w}" height="30" rx="8" fill="${head}" ${S}/>` + txt(0, -h / 2 + 16, title, size, { fill: '#fff' });
    for (let i = 0; i < lines; i++) { const y = -h / 2 + 48 + i * ((h - 60) / Math.max(lines, 1)); s += `<path d="M${-w / 2 + 14} ${y} h${w - 28 - (i % 2) * 22}" stroke="${C.gray}" stroke-width="4" stroke-linecap="round"/>`; }
    return s;
  },
  folder: (w = 110, label = '', col = C.yellow) => { const h = w * 0.72; return `<path d="M${-w / 2} ${-h / 2 + 10} h${w * 0.36} l10 -12 h${w * 0.64 - 10} v${h + 2} h${-w} Z" fill="${col}" ${S}/>` + (label ? txt(0, 6, label, 16) : ''); },
  laptop: (w = 220, screen = '') => { const h = w * 0.62; return `<rect x="${-w / 2}" y="${-h}" width="${w}" height="${h}" rx="10" fill="${C.ink}"/><rect x="${-w / 2 + 9}" y="${-h + 9}" width="${w - 18}" height="${h - 18}" rx="4" fill="${C.light}"/>` + g(`translate(0 ${-h / 2})`, screen) + `<path d="M${-w / 2 - 22} 0 h${w + 44} l-12 14 h${-w - 20} Z" fill="${C.gray}" ${S}/>`; },
  monitor: (w = 150, screen = '') => { const h = w * 0.66; return `<rect x="-10" y="0" width="20" height="30" fill="${C.gray}" ${S2}/><rect x="-36" y="26" width="72" height="10" rx="4" fill="${C.gray}" ${S2}/><rect x="${-w / 2}" y="${-h}" width="${w}" height="${h}" rx="10" fill="${C.ink}"/><rect x="${-w / 2 + 8}" y="${-h + 8}" width="${w - 16}" height="${h - 16}" rx="4" fill="${C.light}"/>` + g(`translate(0 ${-h / 2})`, screen); },
  desk: (w = 300) => `<rect x="${-w / 2}" y="0" width="${w}" height="22" rx="6" fill="#b5835a" ${S}/><rect x="${-w / 2 + 16}" y="22" width="18" height="70" fill="#9c6b45" ${S}/><rect x="${w / 2 - 34}" y="22" width="18" height="70" fill="#9c6b45" ${S}/>`,
  check: (r = 26, col = C.green) => `<circle r="${r}" fill="${col}" ${S}/><path d="M${-r * 0.45} 0 L${-r * 0.1} ${r * 0.38} L${r * 0.5} ${-r * 0.35}" fill="none" stroke="#fff" stroke-width="${r * 0.22}" stroke-linecap="round" stroke-linejoin="round"/>`,
  cross: (r = 26, col = C.red) => `<circle r="${r}" fill="${col}" ${S}/><path d="M${-r * 0.35} ${-r * 0.35} L${r * 0.35} ${r * 0.35} M${r * 0.35} ${-r * 0.35} L${-r * 0.35} ${r * 0.35}" stroke="#fff" stroke-width="${r * 0.22}" stroke-linecap="round"/>`,
  stamp: (label, col = C.red, size = 34) => { const w = label.length * size * 0.62 + 36, h = size + 26; return `<rect x="${-w / 2}" y="${-h / 2}" width="${w}" height="${h}" rx="10" fill="none" stroke="${col}" stroke-width="6"/><rect x="${-w / 2 + 7}" y="${-h / 2 + 7}" width="${w - 14}" height="${h - 14}" rx="6" fill="none" stroke="${col}" stroke-width="2.5"/>` + txt(0, 3, label, size, { fill: col, weight: 700, extra: 'letter-spacing="2"' }); },
  bubble: (w, h, inner, tail = 'left') => { const tx = tail === 'left' ? -w / 2 + 34 : w / 2 - 34; return `<path d="M${tx - 12} ${h / 2 - 2} L${tx + (tail === 'left' ? -18 : 18)} ${h / 2 + 26} L${tx + 14} ${h / 2 - 2}" fill="${C.white}" ${S}/><rect x="${-w / 2}" y="${-h / 2}" width="${w}" height="${h}" rx="22" fill="${C.white}" ${S}/><path d="M${tx - 10} ${h / 2 - 1.5} h24" stroke="${C.white}" stroke-width="5"/>` + inner; },
  sticky: (w, h, lines, col = '#ffe66d') => { let s = `<path d="M${-w / 2} ${-h / 2} h${w} v${h - 18} l-18 18 h${-w + 18} Z" fill="${col}" ${S}/>`; lines.forEach((l, i) => { s += txt(0, -h / 2 + 30 + i * 28, l, 21); }); return s; },
  fingerprint: (r = 34, col = C.navy) => {
    let s = `<ellipse rx="${(r * 0.78).toFixed(1)}" ry="${r}" fill="#f7e3cf" ${S2}/>`;
    for (let i = 1; i <= 4; i++) { const k = i / 4.7; s += `<ellipse rx="${(r * 0.78 * k).toFixed(1)}" ry="${(r * k).toFixed(1)}" cy="${(r * 0.08).toFixed(1)}" fill="none" stroke="${col}" stroke-width="2.6" stroke-linecap="round" stroke-dasharray="${(r * k * 2.4).toFixed(1)} 6" stroke-dashoffset="${i * 11}"/>`; }
    return s;
  },
  house: (w = 40, col = C.orange) => `<path d="M${-w / 2} ${-w * 0.05} L0 ${-w / 2} L${w / 2} ${-w * 0.05} V${w / 2} H${-w / 2} Z" fill="${col}" ${S2}/><rect x="${-w * 0.12}" y="${w * 0.12}" width="${w * 0.24}" height="${w * 0.38}" fill="${C.ink}"/>`,
  briefcase: (w = 42, col = '#9c6b45') => `<rect x="${-w * 0.2}" y="${-w * 0.45}" width="${w * 0.4}" height="${w * 0.2}" rx="4" fill="none" ${S2}/><rect x="${-w / 2}" y="${-w * 0.28}" width="${w}" height="${w * 0.66}" rx="6" fill="${col}" ${S2}/>`,
  cap: (w = 44) => `<path d="M${-w / 2} ${-w * 0.08} L0 ${-w * 0.32} L${w / 2} ${-w * 0.08} L0 ${w * 0.16} Z" fill="${C.ink}"/><path d="M${-w * 0.28} ${w * 0.02} v${w * 0.24} q${w * 0.28} ${w * 0.14} ${w * 0.56} 0 v${-w * 0.24}" fill="${C.ink}"/><path d="M${w * 0.4} ${-w * 0.04} v${w * 0.3}" stroke="${C.yellow}" stroke-width="3"/>`,
  globe: (r = 21, col = C.tealL) => `<circle r="${r}" fill="${col}" ${S2}/><ellipse rx="${r * 0.45}" ry="${r}" fill="none" ${S2}/><path d="M${-r} 0 h${2 * r} M${-r * 0.85} ${-r * 0.5} h${r * 1.7} M${-r * 0.85} ${r * 0.5} h${r * 1.7}" ${S2}/>`,
  plane: (w = 46, col = C.white) => `<g transform="rotate(-20)"><path d="M${-w / 2} 0 Q${-w / 2} -5 ${-w * 0.3} -5 H${w * 0.42} Q${w / 2} 0 ${w * 0.42} 5 H${-w * 0.3} Q${-w / 2} 5 ${-w / 2} 0 Z" fill="${col}" ${S2}/><path d="M${-w * 0.05} -4 L${-w * 0.2} ${-w * 0.42} H${-w * 0.06} L${w * 0.16} -4 Z M${-w * 0.05} 4 L${-w * 0.2} ${w * 0.42} H${-w * 0.06} L${w * 0.16} 4 Z" fill="${col}" ${S2}/><path d="M${-w * 0.44} -4 L${-w * 0.5} ${-w * 0.22} H${-w * 0.4} L${-w * 0.32} -4 Z" fill="${col}" ${S2}/></g>`,
  dollar: (r = 21, col = C.green) => `<circle r="${r}" fill="${col}" ${S2}/>` + txt(0, 2, '$', r * 1.3, { fill: '#fff', weight: 700 }),
  lock: (w = 40, col = C.yellow) => `<path d="M${-w * 0.28} ${-w * 0.1} v${-w * 0.18} a${w * 0.28} ${w * 0.28} 0 0 1 ${w * 0.56} 0 v${w * 0.18}" fill="none" ${S}/><rect x="${-w / 2}" y="${-w * 0.12}" width="${w}" height="${w * 0.72}" rx="7" fill="${col}" ${S}/><circle cy="${w * 0.2}" r="${w * 0.08}" fill="${C.ink}"/>`,
  phone: (w = 60) => `<rect x="${-w / 2}" y="${-w}" width="${w}" height="${w * 2}" rx="10" fill="${C.ink}"/><rect x="${-w / 2 + 5}" y="${-w + 10}" width="${w - 10}" height="${w * 2 - 22}" rx="3" fill="${C.light}"/>`,
  pen: (l = 60) => `<g transform="rotate(35)"><rect x="-5" y="${-l}" width="10" height="${l - 12}" rx="3" fill="${C.navy}" ${S2}/><path d="M-5 -12 L0 0 L5 -12 Z" fill="${C.cream}" ${S2}/></g>`,
  scanner: (w = 200, glow = 0) => `<rect x="${-w / 2}" y="-50" width="${w}" height="100" rx="18" fill="${C.gray}" ${S}/><rect x="${-w / 2 + 30}" y="-36" width="${w - 60}" height="72" rx="10" fill="${glow > 0 ? `rgba(87,167,115,${(0.25 + 0.5 * glow).toFixed(3)})` : C.tealL}" ${S2}/>`,
};

// Stars/sparkle burst
function burst(t, a, x, y, col = C.yellow, n = 8, R = 60) {
  const p = prog(t, a, 0.7); if (p <= 0 || p >= 1) return '';
  let s = '';
  for (let i = 0; i < n; i++) {
    const ang = (i / n) * Math.PI * 2, r = lerp(R * 0.3, R, easeOut(p));
    s += `<path d="M${(x + Math.cos(ang) * r * 0.6).toFixed(1)} ${(y + Math.sin(ang) * r * 0.6).toFixed(1)} L${(x + Math.cos(ang) * r).toFixed(1)} ${(y + Math.sin(ang) * r).toFixed(1)}" stroke="${col}" stroke-width="${(6 * (1 - p)).toFixed(2)}" stroke-linecap="round"/>`;
  }
  return s;
}
function confetti(t, a, x, y, n = 26) {
  const p = t - a; if (p < 0 || p > 2.4) return '';
  const cols = [C.yellow, C.red, C.teal, C.orange, C.purple, C.green];
  let s = '';
  for (let i = 0; i < n; i++) {
    const ang = -Math.PI / 2 + ((i / n) - 0.5) * 2.4, v = 260 + (i * 37) % 160;
    const px = x + Math.cos(ang) * v * p, py = y + Math.sin(ang) * v * p + 380 * p * p;
    s += `<rect x="${px.toFixed(1)}" y="${py.toFixed(1)}" width="10" height="16" rx="2" fill="${cols[i % cols.length]}" transform="rotate(${(p * 400 + i * 40) % 360} ${px.toFixed(1)} ${py.toFixed(1)})" opacity="${clamp(2.4 - p).toFixed(2)}"/>`;
  }
  return s;
}

// ---------- backgrounds ----------
function bgRoom(t, o = {}) {
  const { wall = C.wall, floor = C.floor, window: win = true, horizon = 470 } = o;
  let s = `<rect width="1280" height="720" fill="${wall}"/>`;
  s += `<rect y="${horizon}" width="1280" height="${720 - horizon}" fill="${floor}"/><path d="M0 ${horizon} H1280" ${S}/>`;
  if (win) {
    s += `<g transform="translate(560 90)"><rect width="200" height="150" rx="10" fill="${C.sky}" ${S}/>` +
      `<ellipse cx="${(60 + wob(t, 0.02, 30)).toFixed(1)}" cy="55" rx="34" ry="14" fill="#fff"/><path d="M100 0 V150 M0 75 H200" ${S2}/></g>`;
  }
  return s;
}
function bgSky(t, o = {}) {
  const { top = '#bfe6f5', bottom = '#effaff', ground = '#a8d8a0', horizon = 480 } = o;
  let s = `<defs><linearGradient id="skyg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${top}"/><stop offset="1" stop-color="${bottom}"/></linearGradient></defs>`;
  s += `<rect width="1280" height="720" fill="url(#skyg)"/>`;
  for (const [cx, cy, sp] of [[200, 110, 8], [760, 70, 5], [1100, 150, 7]]) {
    const x = ((cx + t * sp) % 1500) - 110;
    s += `<g transform="translate(${x.toFixed(1)} ${cy})" fill="#fff"><ellipse rx="60" ry="20"/><ellipse cx="-26" cy="-12" rx="28" ry="20"/><ellipse cx="20" cy="-16" rx="32" ry="24"/></g>`;
  }
  s += `<rect y="${horizon}" width="1280" height="${720 - horizon}" fill="${ground}"/><path d="M0 ${horizon} H1280" ${S}/>`;
  return s;
}
function bgNight(t, clear = [300, 1000, 120, 350]) {
  let s = `<defs><radialGradient id="nightg" cx="0.5" cy="0.35" r="0.8"><stop offset="0" stop-color="#2d5a8a"/><stop offset="1" stop-color="#14243d"/></radialGradient></defs><rect width="1280" height="720" fill="url(#nightg)"/>`;
  for (let i = 0; i < 46; i++) {
    const x = (i * 283) % 1280, y = (i * 157) % 460;
    if (x > clear[0] && x < clear[1] && y > clear[2] && y < clear[3]) continue;
    const tw = 0.35 + 0.65 * Math.abs(Math.sin(t * 1.3 + i));
    s += `<circle cx="${x}" cy="${y}" r="${1.5 + (i % 3)}" fill="#fff" opacity="${tw.toFixed(2)}"/>`;
  }
  return s;
}

// ---------- buildings ----------
function govBuilding(w = 260, label = 'DCSA', col = '#e9eef3') {
  const h = w * 0.72;
  let s = `<path d="M${-w / 2 - 16} ${-h + 34} L0 ${-h - 26} L${w / 2 + 16} ${-h + 34} Z" fill="${col}" ${S}/>`;
  s += `<rect x="${-w / 2 - 10}" y="${-h + 34}" width="${w + 20}" height="22" fill="${col}" ${S}/>`;
  const n = 5;
  for (let i = 0; i < n; i++) { const x = -w / 2 + 14 + (i * (w - 48)) / (n - 1); s += `<rect x="${x}" y="${-h + 56}" width="20" height="${h - 76}" fill="${col}" ${S2}/>`; }
  s += `<rect x="${-w / 2 - 16}" y="-20" width="${w + 32}" height="20" fill="${col}" ${S}/>`;
  s += txt(0, -h + 5, label, 26, { weight: 700 });
  return s;
}
function officeBuilding(w = 240, h = 250, sign = 'Your Employer', col = '#f4d8b8') {
  let s = `<rect x="${-w / 2}" y="${-h}" width="${w}" height="${h}" rx="6" fill="${col}" ${S}/>`;
  for (let r = 0; r < 3; r++) for (let c = 0; c < 4; c++) s += `<rect x="${-w / 2 + 22 + c * ((w - 44) / 4)}" y="${-h + 64 + r * 52}" width="${(w - 44) / 4 - 14}" height="32" rx="4" fill="${C.sky}" ${S2}/>`;
  s += `<rect x="-24" y="-54" width="48" height="54" fill="${C.teal}" ${S}/>`;
  s += `<rect x="${-w / 2 + 16}" y="${-h + 14}" width="${w - 32}" height="36" rx="8" fill="${C.navy}" ${S2}/>` + txt(0, -h + 33, sign, 20, { fill: '#fff' });
  return s;
}

// ---------- journey bar ----------
// Journey-bar config. A video's scenes.js may reassign these three.
let STEPS = ['FSO starts', 'You apply', 'FSO review', 'DCSA check', 'Temporary', 'Investigate', 'Adjudicate', 'DOHA review', 'You respond', 'Decision'];
let BAR_BRACKET = { from: 8, to: 10, label: 'only if issues' };
function journeyBar(t, step, o = {}) {
  const { y = 668, allDone = false, reveal = 1 } = o;
  const x0 = 96, x1 = 1184, n = STEPS.length, dx = (x1 - x0) / (n - 1);
  let s = `<rect x="0" y="${y - 30}" width="1280" height="${720 - y + 30}" fill="rgba(253,246,227,0.96)"/><path d="M0 ${y - 30} H1280" ${S2}/>`;
  s += `<path d="M${x0} ${y} H${x1}" stroke="${C.gray}" stroke-width="6" stroke-linecap="round"/>`;
  const done = allDone ? n : step - 1;
  if (done > 0) s += `<path d="M${x0} ${y} H${x0 + dx * Math.min(done, n - 1)}" stroke="${C.teal}" stroke-width="6" stroke-linecap="round"/>`;
  // optional dashed bracket over a run of steps (BAR_BRACKET = null to hide)
  if (BAR_BRACKET) {
  const bx0 = x0 + dx * (BAR_BRACKET.from - 1) - 34, bx1 = x0 + dx * (BAR_BRACKET.to - 1) + 34;
  s += `<path d="M${bx0} ${y - 6} V${y - 22} H${bx1} V${y - 6}" fill="none" stroke="${C.red}" stroke-width="2.5" stroke-dasharray="6 5"/>`;
  s += `<rect x="${(bx0 + bx1) / 2 - 62}" y="${y - 32}" width="124" height="20" rx="10" fill="${C.cream}"/>` + txt((bx0 + bx1) / 2, y - 21, BAR_BRACKET.label, 14, { fill: C.red });
  }
  for (let i = 0; i < n; i++) {
    const x = x0 + dx * i, k = i + 1;
    const vis = clamp(reveal * n - i);
    if (vis <= 0) continue;
    const cur = !allDone && k === step, past = allDone || k < step;
    const r = cur ? 17 + wob(t, 1.2, 1.5) : 13;
    let node = '';
    if (cur) node += `<circle r="${(24 + 8 * ((t * 1.2) % 1)).toFixed(2)}" fill="none" stroke="${C.yellow}" stroke-width="3" opacity="${(1 - ((t * 1.2) % 1)).toFixed(2)}"/>`;
    node += `<circle r="${r.toFixed(2)}" fill="${cur ? C.yellow : past ? C.teal : C.white}" ${S2}/>`;
    node += txt(0, 1.5, String(k), cur ? 17 : 14, { fill: past ? '#fff' : C.ink, weight: 700 });
    s += g(at(x, y, vis), node);
    s += txt(x, y + 32, STEPS[i], 14, { fill: cur ? C.ink : C.gray, weight: cur ? 700 : 600 });
  }
  return s;
}

// ---------- overlays ----------
const $ = id => document.getElementById(id);
function setCaption(text, bottom) {
  const el = $('caption');
  if (!text) { el.style.display = 'none'; return; }
  el.style.display = 'block'; el.style.bottom = bottom + 'px';
  if (el.textContent !== text) el.textContent = text;
}
function setBadge(scene, local) {
  const el = $('badge');
  if (!scene.label || scene.id === 'title' || scene.id === 'end') { el.style.display = 'none'; return; }
  el.style.display = 'flex';
  const p = easeOut(prog(local, 0.15, 0.5));
  el.style.transform = `translateX(${lerp(-420, 0, p).toFixed(1)}px)`;
  const num = scene.step ? String(scene.step) : '';
  const html = `<div class="num${num ? '' : ' small'}">${num || '&#9733;'}</div><div>${scene.label}</div>`;
  if (el.dataset.k !== scene.id) { el.innerHTML = html; el.dataset.k = scene.id; }
}

// ---------- timeline + render ----------
let TL = null;
const SCENES = {};  // id -> function(ctx) returning svg; registered in scenes.js
let BAR_SCENES = new Set(['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10']);

function init(timeline) { TL = timeline; return document.fonts.ready.then(() => true); }

function sceneAt(t) {
  const sc = TL.scenes;
  for (let i = 0; i < sc.length; i++) if (t < sc[i].end || i === sc.length - 1) return i;
  return sc.length - 1;
}
function ctxFor(i, t) {
  const sc = TL.scenes[i];
  const local = t - sc.start;
  const L = sc.lines.map(l => l.start);
  const Le = sc.lines.map(l => l.end);
  return { t, local, sc, L, Le, D: sc.end - sc.start };
}
function drawScene(i, t) {
  const c = ctxFor(i, t), fn = SCENES[c.sc.id] || SCENES._placeholder;
  return fn(c);
}

const IRIS = 0.55;
function renderAt(t) {
  const i = sceneAt(t), sc = TL.scenes[i], local = t - sc.start;
  let body;
  if (i > 0 && local < IRIS) {
    const prev = TL.scenes[i - 1];
    const r = easeInOut(local / IRIS) * 780;
    body = drawScene(i - 1, prev.end - 0.001) +
      `<defs><clipPath id="iris"><circle cx="640" cy="330" r="${r.toFixed(1)}"/></clipPath></defs>` +
      `<g clip-path="url(#iris)">${drawScene(i, t)}</g>` +
      `<circle cx="640" cy="330" r="${r.toFixed(1)}" fill="none" stroke="${C.ink}" stroke-width="8"/>`;
  } else {
    body = drawScene(i, t);
  }
  const bar = BAR_SCENES.has(sc.id);
  if (bar) body += journeyBar(t, sc.step);
  $('svg').innerHTML = body;
  // caption: current line, held until the next line starts
  let cap = '';
  for (let k = 0; k < sc.lines.length; k++) {
    const next = k + 1 < sc.lines.length ? sc.lines[k + 1].start : sc.lines[k].end + 0.5;
    if (local >= sc.lines[k].start - 0.05 && local < next - 0.02) cap = sc.lines[k].cap;
  }
  setCaption(cap, bar ? 96 : 26);
  setBadge(sc, local);
  return true;
}

SCENES._placeholder = c => bgRoom(c.local) + txt(640, 300, c.sc.label || c.sc.id, 48, { weight: 700 });
