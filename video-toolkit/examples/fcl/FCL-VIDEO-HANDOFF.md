# FCL explainer video: handoff for a local chat

Load this file into a new chat to continue the work. It stands alone: the decisions, the research
findings, the draft script and the draft scene code are all here. The cloud session that produced it
was reclaimed, so this file is the only copy of the drafts. Nothing in `examples/fcl/` was rendered or
approved.

## 1. The task

Make narrated cartoon explainer videos (about 5 minutes each) on the **Facility Clearance (FCL) process** under the
NISP. They are companions to the finished PCL video (`video-toolkit/examples/pcl/`) and should match its style and
quality. Use the toolkit in `video-toolkit/` (see its README for setup, pipeline, owner preferences and pitfalls).
Work in a scratch copy of `video-toolkit/`, never inside the repo tree, and don't touch the Librarian's code,
`state/` or `config/`.

**Owner decisions so far**
- **Three separate videos, done in order.** Each one starts only after the owner approves the one before it:
  1. **Company leadership** (a small company new to the NISP, pursuing its first FCL). *Draft below. Awaiting approval.*
  2. **Sponsor side** (GCA / cleared prime writing the sponsorship request). Not started.
  3. **New FSO** (hands-on: NISS screens, document checklist, the ISR's review items). Not started.
- **Anchor:** the July 2026 FCL Orientation Handbook's process flow (roadmap §1.2). No separate process map.
- Voice: Kokoro `bf_emma`, speed 0.95, `en-gb`. Burned-in captions, step badge, journey bar. Label it
  "Unofficial training aid". No seals or logos.

**Checkpoint process, per video**
1. Send the script review doc and a 20–30 s sample (`node render.js --ranges a-b --out build/sample.mp4`).
   **Stop and wait for approval.**
2. The owner edits by pasting a revised table. Diff it line by line against the draft. Fix obvious typos. For any
   factual problem, propose a fix and flag it for sign-off; don't silently change meaning. Run
   `audit_say.py` after every script change.
3. After approval: build every scene, check contact sheets (`stills.py`) for overlaps, then run
   `OUT_NAME=fcl-walkthrough ./render_full.sh`. Check the duration, the audio peak (≤ −1.4 dB) and the chunk joins.
4. Commit `examples/fcl/` (`script.json`, `scenes.js`, the review doc), any toolkit fixes (with the pitfall
   recorded in the README) and one `HANDOFF.md` log entry, then push to `claude/fcl-video`. Never commit MP4s,
   voices or the venv. No PR unless asked.

**Where things stand (as of this handoff)**
- Video 1's script and a 30 s sample of Step 1 were sent to the owner on 2026-09-25. **The owner has not
  replied yet.** The sample MP4 is gone. Re-render it from the code below if it's needed again.
- Scenes are built for `title`, `meet` and `s1` only. All others render as placeholders.
- Branch: `origin/claude/fcl-video` holds a HANDOFF checkpoint commit (`ececa21`). A later local checkout of the
  branch was based on newer toolkit commits (`1aad4b7`: `kokoro_setup.py`, script-level timeline settings), so
  the two lines have diverged. Merge rather than force-push.

## 2. Open items needing the owner's sign-off (video 1)

| # | Where | Issue | Current handling |
|---|---|---|---|
| 1 | Once you're cleared | **The ISR orientation meeting comes after the FCL, not before.** The original brief put it among the pre-decision steps, which matches the superseded editions. The July 2026 handbook §2.3 and the Quick Start Guide put it *after* the FCL is granted, with ISR contact within 120 days. | Placed after the FCL. The pre-decision review is DCSA HQ's (Step 7). |
| 2 | Meet Jordan | "For **most** companies in the NISP, DCSA decides." DCSA covers DoW plus 35 agencies; DOE, NRC, ODNI and DHS are separate CSAs. No source gives a share, so "most" is an inference. | Kept. The other option: "For companies working with the Department of War and most other agencies…" |
| 3 | Once you're cleared | Six-month training deadline for the ITPSO: 32 CFR 117.12(d) sets six months for the **FSO** only. The ITPSO deadline comes from DCSA's Quick Start Guide. | Kept both. Can narrow to the FSO. |
| 4 | Step 3 | The handbook contradicts itself on restarting after a discontinuation. App. E says a new package is needed and a new sponsorship is not. App. F says to coordinate with the sponsor to resubmit the sponsorship. | Left out of the narration. |
| 5 | Step 8 | "15 days" means **calendar** days from the Notice of Intent memo (handbook §3.5.1). The appeal window is 30 calendar days. | Narration says "15 days." The on-screen text should say "15 calendar days." |
| 6 | — | DTM 24-004 (covered JVs) is `currency_unresolved`: past its 2026-07-31 expiration, with nothing posted by WHS. | Excluded. JVs are outside this audience's scope. |
| 7 | — | NISS Increment II (NI2) FOCI work tied to DFARS changes expected by Oct 1, 2026 (June 2026 VOI). | Not mentioned. The wording is kept durable. **Today is past Oct 1, so check whether the DFARS change landed.** |

## 3. Research findings (verified on 2026-09-25)

Sources: the owner's Google Drive library (release fcl-intake-20260924b): *FCL Orientation Handbook July 2026*,
*FCL Quick Start Guide*, *FCL Job Aid SF 328*. Also eCFR 32 CFR 117 (current to 2026-09-23; fetch with
`curl --compressed`), DoDM 5220.32 V1 (Ch 2, 2021) and the VOIs of June and August 2026. The 2018 and 2021
handbooks are superseded and were not used.

| Claim | Source |
|---|---|
| FCL = administrative determination that a company is eligible for access (same or lower level); also called "entity eligibility determination" | 117.3(b), via handbook §3.0; 117.9(a)(7) |
| A company can't apply for its own FCL; a GCA or cleared contractor sponsors, at any point including solicitation | 117.9(a)(10) |
| The sponsor's request gives the level and a justification (DD 254, security aspects letter, contract/SOW, RFP/RFQ/BAA, CRADA, IR&D) and is submitted in NISS | DoDM 5220.32 V1 §4.3.b; handbook §1.0 |
| A need for background investigations only for a position or for physical access does **not** meet the FCL requirement | Handbook §3.0, eligibility note |
| CAGE code required for anyone doing business with the USG; SAM required for prime contract holders | Handbook §2.1; Quick Start Guide Phase 1 |
| PKI/ECA token needed for NCAISS/NISS; it takes weeks (ECA 2+ weeks; PKI longer, usually needs a CAC) | Handbook §2.1, App. G |
| FSO and ITPSO must be U.S. citizen employees | 117.9(d)(1)(iii)–(iv) |
| Welcome email = Day 1; initial package due in NISS within **20 days** | Handbook §2.2, §3.0; Quick Start Guide |
| Package: state formation documents, business license, minutes/appointments, legal org chart **with ownership and control percentages**, FSO/ITPSO in NISS, signed and witnessed DD 441 and SF 328, citizenship verification, KMP personal emails, exclusion resolutions, parent documents | Handbook §4.2 table; Quick Start Guide Phase 2 |
| Two chances to fix discrepancies; after that DCSA discontinues, even before day 20 | Handbook §2.2; App. E, F |
| SF 328 (rev. 5/2025): 9 yes/no FOCI questions; a "yes" needs detail; FOCI extends timelines (review, analysis, risk treatment) | SF 328 job aid; handbook §1.0 |
| DD 441: security agreement; one original; signed by the SMO (authority to bind), witnessed; leave the government block and the first-page date blank; SF 328 and DD 441 signed the same day | Handbook §4.5, App. B.1, App. D |
| DD 441 Section II covers DCSA's access to conduct reviews | VOI June 2026 |
| SMO, FSO and ITPSO cleared at or above the FCL level (they cannot be temporarily excluded); other KMP are cleared or excluded by resolution, subject to DCSA concurrence | 117.9(c)(5), (f), (g); handbook §4.1 |
| DCSA initiates eApp and fingerprints for essential KMP and emails due dates; missing them can discontinue the process. Fingerprints go via SWFT (hard-copy FBI cards are not accepted) | Handbook §2.2, App. F; Quick Start Guide |
| DCSA reviews the whole structure (highest U.S. entity; stakeholders with 5% or more, fully diluted). Risk categories: A Ownership, B Business operations, C Financials, D Personnel, E Business conduct | Handbook §4.0, §3.4 |
| Interim FCL possible if there is no unmitigated FOCI and essential KMP have interim eligibility or higher; the final FCL waits until all essential KMP are cleared at the final level | Handbook §1.0; 117.9(h) |
| Denial path: Notice of Intent + SOR, with 15 calendar days to respond; final determination with appeal rights (30 calendar days); independent review board; decision by the Associate Director, Industrial Security | Handbook §3.5.1 |
| After the FCL: 2 DISS accounts within 30 days; ISR contact and orientation meeting within 120 days; FSO (and ITPSO per the Quick Start Guide) training within 6 months | Handbook §2.3, §6.0, §7; Quick Start Guide Phase 3; 117.12(d) |
| Report changed conditions; annual self-inspection certified in writing by the SMO; DCSA security reviews | 117.8(c)(7); 117.7(h)(2)(iii); 117.7(h)(1) |
| No use of the FCL in advertising (advertising cleared positions is fine) | 117.9(a)(9); VOI June/Aug 2026 |
| "Right the first time" accuracy and fast responses are the most important factors within your control | Handbook §1.1 |
| Expedite: a GCA may request one on letterhead, with an impact statement, through the NISS sponsorship; no guarantee | Handbook §3.3 (for video 2) |

Contacts (for end cards): EV Knowledge Center (878) 274-2000, option 2 then 1; NISS technical line, option 2 then 3.

**Stale first** (check these before reusing): handbook deadlines (20 / 30 / 120 days); the NISS/FOCI workflow (NI2, DFARS);
the KMP-clearance systems (initiation moved from NBIS to DISS on 2026-09-30; NBIS Agency shut down 2026-11-30; eApp stays for now; the PVQ is replacing
the SF 86 in phases); the SF 328 revision; the ITPSO training deadline; DTM 24-004.

## 4. Video 1 draft: `script.json`

Voiced at 4:49 (657 words). `audit_say.py`: 0 flagged.

```json
{
 "title": "Your Company's Facility Clearance, Step by Step",
 "scenes": [
  {"id": "title", "step": null, "label": "", "lines": [
   {"cap": "Here's how a company earns a facility clearance, in about five minutes."}
  ]},
  {"id": "meet", "step": null, "label": "Meet Jordan", "lines": [
   {"cap": "Meet Jordan. Jordan runs a small tech company, and a government customer wants it on a classified contract."},
   {"cap": "A facility clearance, or FCL, is the government's decision that a company is eligible for access to classified information.",
    "say": "A facility clearance, or F C L, is the government's decision that a company is eligible for access to classified information."},
   {"cap": "For most companies in the National Industrial Security Program, that decision belongs to DCSA: the Defense Counterintelligence and Security Agency."}
  ]},
  {"id": "s1", "step": 1, "label": "Get sponsored", "lines": [
   {"cap": "Step one: sponsorship. A company can't apply for its own facility clearance."},
   {"cap": "A government contracting activity, or a cleared prime contractor, must sponsor you. That can happen as early as the bidding stage."},
   {"cap": "The sponsor's request in NISS, DCSA's system, states the clearance level and the classified need, such as a DD 254 or a statement of work.",
    "say": "The sponsor's request in NISS, D C S A's system, states the clearance level and the classified need, such as a D D two-fifty-four or a statement of work."},
   {"cap": "No classified need, no clearance. Needing background checks just to enter a building doesn't count."}
  ]},
  {"id": "s2", "step": 2, "label": "Do the pre-work", "lines": [
   {"cap": "Step two: get ready. Much of this can start before the sponsorship is accepted."},
   {"cap": "Get a CAGE code, and if you'll hold the prime contract, register in SAM.",
    "say": "Get a cage code, and if you'll hold the prime contract, register in Sam."},
   {"cap": "Your FSO needs a PKI or ECA token to log in to NISS. It can take weeks, so order it early.",
    "say": "Your F S O needs a P K I or ECA token to log in to NISS. It can take weeks, so order it early."},
   {"cap": "Choose your Facility Security Officer and insider threat official. Both must be U.S. citizen employees."},
   {"cap": "And study DCSA's FCL Orientation Handbook before the clock starts.",
    "say": "And study D C S A's F C L Orientation Handbook before the clock starts."}
  ]},
  {"id": "s3", "step": 3, "label": "Submit the NISS package", "lines": [
   {"cap": "Step three: the package. When DCSA accepts the sponsorship, a welcome email arrives. That's day one."},
   {"cap": "You have 20 days to submit your FCL package in NISS.",
    "say": "You have twenty days to submit your F C L package in NISS."},
   {"cap": "It includes formation and governance documents, a legal org chart with ownership percentages, and your list of key management personnel, or KMP.",
    "say": "It includes formation and governance documents, a legal org chart with ownership percentages, and your list of key management personnel, or K M P."},
   {"cap": "Get it right the first time. DCSA gives you two chances to fix problems. After that, it discontinues the request."}
  ]},
  {"id": "s4", "step": 4, "label": "SF 328: foreign interests", "lines": [
   {"cap": "Two forms in the package deserve a closer look. First, the SF 328, the Certificate Pertaining to Foreign Interests.",
    "say": "Two forms in the package deserve a closer look. First, the S F three-twenty-eight, the Certificate Pertaining to Foreign Interests."},
   {"cap": "Nine yes-or-no questions about foreign ownership, control, or influence, called FOCI.",
    "say": "Nine yes-or-no questions about foreign ownership, control, or influence, called foe-see."},
   {"cap": "A \"yes\" isn't a denial. But it means more review, and possibly mitigation, so it takes longer.",
    "say": "A yes isn't a denial. But it means more review, and possibly mitigation, so it takes longer."}
  ]},
  {"id": "s5", "step": 5, "label": "DD 441: security agreement", "lines": [
   {"cap": "Second, the DD 441, the security agreement between your company and the government.",
    "say": "Second, the D D four-forty-one, the security agreement between your company and the government."},
   {"cap": "Your senior management official signs it in front of a witness."},
   {"cap": "It commits the company to the NISPOM, the program's rulebook, and to DCSA oversight."}
  ]},
  {"id": "s6", "step": 6, "label": "Clear your key people", "lines": [
   {"cap": "Step six: your key people. The senior management official, FSO, and insider threat official must be cleared at the facility's level or higher.",
    "say": "Step six: your key people. The senior management official, F S O, and insider threat official must be cleared at the facility's level or higher."},
   {"cap": "Other leaders may need clearances too. Those who don't can be formally excluded."},
   {"cap": "DCSA emails each person with a deadline for their eApp and fingerprints. Miss it, and the whole process can be discontinued.",
    "say": "DCSA emails each person with a deadline for their e-App and fingerprints. Miss it, and the whole process can be discontinued."}
  ]},
  {"id": "s7", "step": 7, "label": "DCSA reviews the risk", "lines": [
   {"cap": "Step seven: DCSA reviews your whole business structure, including any parent company."},
   {"cap": "Analysts weigh ownership, business operations, finances, your key people, and your business conduct."},
   {"cap": "If there's foreign influence to address, DCSA works with you on a plan to mitigate it."}
  ]},
  {"id": "s8", "step": 8, "label": "The decision", "lines": [
   {"cap": "Step eight: the decision, formally called an entity eligibility determination."},
   {"cap": "DCSA may grant an interim clearance first, if there's no unmitigated FOCI and your key people hold interim eligibility.",
    "say": "DCSA may grant an interim clearance first, if there's no unmitigated foe-see and your key people hold interim eligibility."},
   {"cap": "The final clearance waits until every required key person is fully cleared."},
   {"cap": "If DCSA intends to deny, you get a statement of reasons and 15 days to respond, and you can appeal a denial.",
    "say": "If DCSA intends to deny, you get a statement of reasons and fifteen days to respond, and you can appeal a denial."}
  ]},
  {"id": "after", "step": null, "label": "Once you're cleared", "lines": [
   {"cap": "Cleared! Now the work begins."},
   {"cap": "Within 30 days, set up at least two DISS accounts to manage your employees' clearances.",
    "say": "Within thirty days, set up at least two DISS accounts to manage your employees' clearances."},
   {"cap": "Within 120 days, your Industrial Security Representative, or ISR, meets you for an orientation and a look at your security program.",
    "say": "Within a hundred and twenty days, your Industrial Security Representative, or I S R, meets you for an orientation and a look at your security program."},
   {"cap": "Your FSO and insider threat official finish required training within six months.",
    "say": "Your F S O and insider threat official finish required training within six months."}
  ]},
  {"id": "keep", "step": null, "label": "Keeping it", "lines": [
   {"cap": "Keeping the clearance is ongoing. Report changes like new owners, new key leaders, or new foreign ties."},
   {"cap": "Run a self-inspection every year, which your senior official certifies, and expect DCSA security reviews."},
   {"cap": "One more rule: you can't use your facility clearance in advertising."}
  ]},
  {"id": "recap", "step": null, "label": "Recap", "lines": [
   {"cap": "So: get sponsored, prepare early, submit a complete package on time, and get your key people cleared."},
   {"cap": "Be upfront about foreign interests, and answer DCSA quickly. Accuracy and speed are the parts you control."}
  ]},
  {"id": "end", "step": null, "label": "", "hold": 5.0, "lines": []}
 ]
}
```

Pronunciation choices: keep "ECA" **unspaced**, because a spaced acronym ending in "A" is misread. Use "D C S A's" for the possessive.
"foe-see" is for FOCI, and "cage" and "Sam" are for CAGE and SAM.

### Planned visuals for scenes not yet built (from the review doc)
- **s2:** a checklist: CAGE code · SAM · PKI/ECA token (hourglass, "weeks") · FSO + ITPSO (U.S. citizen employees) · handbook.
- **s3:** welcome email = "Day 1"; 20-day calendar; documents drop into a NISS folder (formation, governance, org chart with %, KMP list);
  two "fix it" tries, then a "Discontinued" stamp *beside* the folder.
- **s4:** SF 328 with 9 Yes/No rows; "FOCI = Foreign Ownership, Control, or Influence"; a "Yes" leads to a longer path (magnifier, mitigation), not a stop sign.
- **s5:** DD 441 between company and government; Jordan (SMO) signs while a witness watches; NISPOM book (32 CFR 117); "DCSA oversight" chip.
- **s6:** SMO / FSO / ITPSO with "≥ FCL level" badges; other officers either "cleared" or "excluded" (resolution document); emails with due dates; eApp and fingerprints.
- **s7:** org chart with a parent; analyst (`CAST.analyst`) with five category cards; a "mitigation plan" handshake.
- **s8:** "Entity eligibility determination"; dashed "Interim FCL" card, then solid "Final FCL" once every KMP shows a check; a small side path:
  Notice of intent + SOR → respond (15 calendar days) → appeal.
- **after:** confetti; three calendars: 30 days (2 DISS accounts), 120 days (the ISR arrives), 6 months (training certificates).
- **keep:** report arrows (owners, KMP, foreign ties); annual self-inspection clipboard with the SMO's signature; ISR visit; a billboard
  reading "FCL cleared!" with a no-sign beside it.
- **recap:** the eight-node journey lights up while Jordan walks it; tips "Be accurate", "Be upfront", "Answer fast".
- **end:** "Questions? Contact DCSA's Entity Vetting Knowledge Center"; sources; "Unofficial training aid · Not legal advice · Current as of <month year>".

## 5. Video 1 draft: `scenes.js`

Build it as: **the first 110 lines of `examples/pcl/scenes.js`** (everything before `// ---------- Title ----------`,
which holds the shared helpers `inHand`, `card`, `flyer`, `P.rosette`, `P.calendar`, `P.book`, `P.magnifier` and others),
followed by the code below. On Linux: `head -n 110 examples/pcl/scenes.js > scenes.js && cat fcl_part.js >> scenes.js`.
Check the line number first with `grep -n "^// ---------- Title" examples/pcl/scenes.js`.
Contact sheets of these three scenes were reviewed; the overlaps were fixed.

```js
// ================= FCL video =================
CAST.jordan = o => person({ skin: '#d9a066', hair: '#3b2a20', hairStyle: 'short', blazer: C.purple, top: '#f1e3ff', pants: '#2b2d42', seed: 10.2, ...o });
CAST.co = o => person({ skin: '#7d4e2d', hair: '#222', hairStyle: 'bun', blazer: C.green, top: C.cream, pants: '#3d405b', seed: 11.7, ...o });
CAST.isr = o => person({ skin: '#e8b98f', hair: '#6b3e26', hairStyle: 'short', blazer: C.navy, tie: C.yellow, pants: '#3d405b', glasses: true, seed: 12.9, ...o });
CAST.analyst = CAST.adjudicator;

STEPS = ['Sponsor', 'Pre-work', 'NISS package', 'SF 328', 'DD 441', 'KMP clearances', 'DCSA review', 'Decision'];
BAR_BRACKET = { from: 3, to: 5, label: '20-day package' };
BAR_SCENES = new Set(['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8']);

const noMark = (r = 30) => `<circle r="${r}" fill="#fff" stroke="${C.red}" stroke-width="${r * 0.27}"/><path d="M${-r * 0.7} ${r * 0.7} L${r * 0.7} ${-r * 0.7}" stroke="${C.red}" stroke-width="${r * 0.27}" stroke-linecap="round"/>`;
const winFrame = (w, h, title, col = C.navy) =>
  `<rect x="${-w / 2}" y="${-h / 2}" width="${w}" height="${h}" rx="16" fill="${C.white}" ${S}/>` +
  `<path d="M${-w / 2} ${-h / 2 + 16} Q${-w / 2} ${-h / 2} ${-w / 2 + 16} ${-h / 2} H${w / 2 - 16} Q${w / 2} ${-h / 2} ${w / 2} ${-h / 2 + 16} V${-h / 2 + 44} H${-w / 2} Z" fill="${col}" ${S}/>` +
  txt(0, -h / 2 + 23, title, 20, { fill: '#fff', weight: 700 });
const classifiedDoc = (w = 96, h = 120, title = 'Contract') => P.doc(w, h, title, { head: C.red, lines: 3, size: 15 });

// ---------- Title ----------
SCENES.title = ({ local: u }) => {
  let s = bgNight(u);
  s += `<ellipse cx="640" cy="598" rx="260" ry="28" fill="rgba(255,255,255,0.12)"/>`;
  s += pop(u, 0.15, 640, 170, txt(0, 0, "Your Company's Facility Clearance", 64, { fill: C.cream, weight: 700 }), 0.6);
  s += pop(u, 0.55, 640, 255, txt(0, 0, 'Step by Step', 50, { fill: C.yellow, weight: 700 }), 0.6);
  s += pop(u, 0.9, 640, 315, txt(0, 0, 'A 5-minute cartoon guide for company leaders', 24, { fill: '#cfe3f7', weight: 500 }), 0.5);
  s += slideIn(u, 0.3, 470, 800, 470, 596, officeBuilding(190, 200, 'Your Company'), 0.7);
  s += pop(u, 1.3, 605, 405, P.rosette('FCL'), 0.5, 10);
  s += slideIn(u, 0.5, 760, 820, 760, 598, actor('jordan', 0, 0, 0.95, { t: u, armR: -150 + wob(u, 1.6, 22), mood: 'happy' }), 0.7);
  s += op(fade(u, 1.0, 0.6), txt(1250, 30, 'Unofficial training aid', 17, { fill: '#9fb8d6', anchor: 'end', weight: 500 }));
  return s;
};

// ---------- Meet Jordan ----------
SCENES.meet = ({ local: u, L }) => {
  let s = bgSky(u);
  s += g(at(170, 482), officeBuilding(220, 230, "Jordan's Co."));
  const wp = prog(u, 0.2, 1.6), jx = lerp(170, 380, easeOut(wp)), walking = wp > 0 && wp < 0.97;
  const handoff = L[0] + 3.6, got = u > handoff + 1.0;
  const cheer = got && u < L[1] + 0.3;
  const armR = cheer ? -150 + wob(u, 1.4, 12) : got ? -40 : -14;
  s += actor('jordan', jx, 560, 1.0, {
    t: u, walk: walking, mood: got ? 'happy' : 'neutral', look: 4, armR,
    propR: got ? inHand(armR, classifiedDoc(70, 88), 0, -54) : '',
  });
  s += op(fade(u, 1.8), nameTag(jx, 292, 'Jordan, CEO'));
  // government customer hands over the classified contract
  const coOut = 1 - fade(u, L[1] - 0.2, 0.4);
  if (coOut > 0) {
    s += op(coOut, slideIn(u, L[0] + 1.2, 1400, 560, 690, 560, actor('co', 0, 0, 0.95, { t: u, mood: 'happy', look: -4, armL: u < handoff ? 60 : 12, propL: u < handoff ? inHand(60, classifiedDoc(70, 88), 0, -54) : '' }), 0.7));
    s += op(coOut * fade(u, L[0] + 1.9), nameTag(690, 292, 'Government customer'));
    s += flyer(u, handoff, 1.0, [640, 400], [540, 250], [440, 420], classifiedDoc(70, 88), -20);
    s += op(coOut, pop(u, handoff + 1.1, 540, 190, chip(0, 0, 'Classified contract!', { fill: C.yellow, size: 22 }), 0.4));
  }
  // what an FCL is
  const cardIn = `<g transform="translate(-170 0)">${P.rosette('FCL')}</g>` +
    txt(50, -66, 'Facility clearance (FCL) =', 25, { weight: 700 }) +
    txt(50, -28, "the government's decision", 22, { weight: 500 }) +
    txt(50, 6, 'that a COMPANY is ELIGIBLE', 22, { weight: 700, fill: C.teal }) +
    txt(50, 40, 'for access to classified', 22, { weight: 500 }) + txt(50, 70, 'information', 22, { weight: 500 });
  s += pop(u, L[1] + 0.3, 740, 240, card(500, 220, cardIn), 0.5);
  // who decides
  s += slideIn(u, L[2] + 0.2, 1110, 760, 1110, 478, govBuilding(230, 'DCSA'), 0.7);
  s += op(fade(u, L[2] + 5.0), txt(1110, 505, 'Defense Counterintelligence', 17, { weight: 600 }) + txt(1110, 526, 'and Security Agency', 17, { weight: 600 }));
  if (u > L[2] + 6.2) {
    const p = easeOut(prog(u, L[2] + 6.2, 0.6));
    s += `<path d="M995 250 Q1040 235 ${lerp(995, 1070, p).toFixed(1)} ${lerp(250, 270, p).toFixed(1)}" fill="none" stroke="${C.ink}" stroke-width="4" stroke-dasharray="10 8"/>`;
    s += pop(u, L[2] + 6.6, 1160, 225, chip(0, 0, 'decides', { size: 18, fill: C.yellow }), 0.35);
  }
  return s;
};

// ---------- Step 1: sponsorship ----------
SCENES.s1 = ({ local: u, L }) => {
  let s = bgSky(u);
  s += g(at(1110, 482, 0.9), govBuilding(230, 'DCSA'));
  const tryT = L[0] + 2.2, bounce = tryT + 1.0;
  // Jordan tries to apply; it bounces back
  const holding = u < tryT || (u > bounce + 0.9 && u < L[1]);
  s += actor('jordan', 190, 560, 0.95, {
    t: u, look: 4, mood: u > bounce && u < L[1] + 0.5 ? 'surprised' : 'happy',
    armR: holding ? -70 : -14, propR: holding ? inHand(-70, P.doc(60, 76, 'FCL', { head: C.purple, lines: 2, size: 14 }), 0, -50) : '',
  });
  s += nameTag(190, 296, 'Jordan');
  if (u < L[1] + 0.4) {
    const fa = 1 - fade(u, L[1], 0.4);
    let a = '';
    if (u > tryT && u < bounce) {
      const p = easeInOut(prog(u, tryT, bounce - tryT)), [x, y] = qb([270, 400], [600, 170], [950, 360], p);
      a += g(at(x, y, 1, p * 20), P.doc(60, 76, 'FCL', { head: C.purple, lines: 2, size: 14 }));
    }
    if (u > bounce && u < bounce + 0.9) {
      const p = easeInOut(prog(u, bounce, 0.9)), [x, y] = qb([950, 360], [640, 230], [270, 400], p);
      a += g(at(x, y, 1, -p * 20), P.doc(60, 76, 'FCL', { head: C.purple, lines: 2, size: 14 }));
    }
    a += pop(u, bounce + 0.1, 860, 250, noMark(34), 0.35);
    a += pop(u, bounce + 0.4, 600, 250, chip(0, 0, "Can't apply for yourself", { fill: '#fde2dc', size: 24 }), 0.4);
    s += op(fa, a);
  }
  // who can sponsor
  if (u > L[1] - 0.2 && u < L[2] + 0.4) {
    const fb = 1 - fade(u, L[2], 0.4);
    let b = pop(u, L[1] + 0.3, 610, 200, txt(0, 0, 'Who can sponsor you?', 30, { weight: 700 }), 0.4);
    b += pop(u, L[1] + 1.2, 480, 330, card(250, 180, g(at(0, 10, 0.42), govBuilding(230, 'GCA')) + txt(0, 44, 'Government', 20, { weight: 600 }) + txt(0, 68, 'contracting activity', 18, { weight: 500 })), 0.45);
    b += pop(u, L[1] + 2.8, 760, 400, txt(0, 0, 'or', 26, { weight: 700, fill: C.gray }), 0.3);
    s += op(fb, b);
    s += op(fb, pop(u, L[1] + 3.2, 790, 330, card(250, 180, g(at(-20, 12, 0.38), officeBuilding(200, 190, 'Prime')) + g(at(78, -28, 0.5), P.rosette('FCL')) + txt(0, 44, 'Cleared prime', 20, { weight: 600 }) + txt(0, 68, 'contractor', 18, { weight: 500 })), 0.45));
    s += op(fb, pop(u, L[1] + 5.0, 635, 470, chip(0, 0, 'As early as the bidding stage', { fill: C.yellow, size: 20 }), 0.4));
  }
  // the sponsorship request in NISS
  if (u > L[2] - 0.2 && u < L[3] + 0.4) {
    const fc = 1 - fade(u, L[3], 0.4), send = L[2] + 7.4, land = send + 1.1;
    let w = winFrame(470, 270, 'NISS · Sponsorship request');
    const rows = [['Company', "Jordan's Co."], ['FCL level', 'SECRET'], ['Why', 'DD 254 · statement of work']];
    rows.forEach(([k, v], i) => {
      const a = L[2] + 1.6 + i * 1.6, y = -52 + i * 52;
      w += op(fade(u, a), txt(-210, y, k, 19, { anchor: 'start', fill: C.gray }) + txt(-90, y, v, 20, { anchor: 'start', weight: 600 }));
    });
    w += `<rect x="-60" y="96" width="120" height="30" rx="15" fill="${u > send ? C.green : C.teal}" ${S2}/>` + txt(0, 112, u > send ? 'Sent!' : 'Submit', 16, { fill: '#fff', weight: 700 });
    let c = pop(u, L[2] + 0.2, 630, 290, w, 0.5);
    c += flyer(u, send, land - send, [630, 400], [880, 150], [1100, 370], P.envelope(60), 0);
    c += burst(u, land, 1100, 370, C.yellow, 10, 80);
    c += pop(u, land + 0.1, 1100, 180, chip(0, 0, 'Sponsored', { fill: C.yellow, size: 20 }), 0.4);
    s += op(fc, c);
  }
  // classified need only
  if (u > L[3] - 0.2) {
    let d = pop(u, L[3] + 0.2, 630, 230, card(500, 110, g(at(-190, 0), classifiedDoc(56, 70, '')) + txt(-140, -14, 'Need access to', 24, { anchor: 'start', weight: 600 }) + txt(-140, 18, 'classified information', 24, { anchor: 'start', weight: 700, fill: C.teal })), 0.45);
    d += pop(u, L[3] + 0.9, 920, 230, P.check(28), 0.35);
    d += pop(u, L[3] + 2.8, 630, 390, card(500, 110, txt(0, -16, 'Background checks just', 23, { weight: 600 }) + txt(0, 16, 'to enter a building', 23, { weight: 600 })), 0.45);
    d += pop(u, L[3] + 3.6, 920, 390, P.cross(28), 0.35);
    d += pop(u, L[3] + 4.0, 630, 470, chip(0, 0, "doesn't count", { fill: '#fde2dc', size: 20 }), 0.35);
    s += d;
  }
  return s;
};
```

Layout notes: the stage is 1280×720. The journey bar sits at y ≥ 638, and on bar scenes the caption box sits about 540–624,
so keep props above y ≈ 520. Actors' feet at y 552–560 (the caption covers their legs, as in the PCL video).
The sample was `node render.js --ranges 32.63-62.6` (all of Step 1, iris included). Line timings shift when the script is re-voiced;
every animation is keyed to `L[i]`.

## 6. Next actions

1. Get the owner's verdict on the video 1 script and the 7 flags in §2. Apply any pasted table edits (line-by-line diff), then
   run `audit_say.py`.
2. Re-check: did the DFARS/NI2 FOCI change land (expected by 2026-10-01)? Check the Sep and Oct 2026 VOIs for FCL changes.
   Has DTM 24-004's status changed? Update §3 and the script if so.
3. Build scenes s2–s8, after, keep, recap and end. Check contact sheets for every scene, then do the full render.
4. Commit `examples/fcl/` (`script.json`, `scenes.js`, `script-review.md`) and a HANDOFF entry, then push to `claude/fcl-video`.
5. Then video 2 (sponsor side: who may sponsor, justification contents, DD 254, expedite requests, notifications on return or discontinuation)
   and video 3 (FSO hands-on), each with its own checkpoint.
