# DD 254 six-part course — handoff for a local chat

**Load this file together with `dd254-course-script-review.md`** (sent in the cloud session on 4 Oct 2026). That review doc is the authoritative copy of the full narration for all six parts. This file holds everything else: the brief, the decisions, the constraints, the verified sources, the open questions and the next steps.

> **Status:** checkpoint 2, the script review, was delivered and is **awaiting the owner's approval**. No scenes are built. The cloud scratch workspace was lost (see "What was lost"). This file and the surviving narration were committed to `claude/dd254-video` on 17 Nov 2026.

---

## 1. What this is
- **Course:** a narrated cartoon course on completing **DD Form 254** (Contract Security Classification Specification, APR 2018 edition).
- **Shape:** six videos of about 9 minutes each, roughly 53½ minutes in all.
- **Approach:** the course follows one DD 254 down the chain, from the government, to the prime contractor, to the subcontractor.
- **Style:** it matches the existing PCL (personnel clearance) video in the DCSA Librarian repo's `video-toolkit/`.
- **Repo:** `adamsdarin/dcsa-librarian`, branch `claude/dd254-video`. The branch has no commits for this work yet.
- **Original brief:**
  - Work in a scratch copy of `video-toolkit/`, never inside the repo tree.
  - Don't touch the repo's code, `state/` or `config/`.
  - Stop for approval at the scope checkpoint and at the script checkpoint.
  - After approval: build every scene, review contact sheets, run `render_full.sh`, and verify duration, audio peak (≤ −1.4 dB) and chunk joins.
  - Deliver the MP4s and the final script doc.
  - Commit `video-toolkit/examples/dd254/` (script.json, scenes.js, review doc), any toolkit fixes with their pitfalls recorded in the README, and one `HANDOFF.md` log entry.
  - Never commit MP4s, voices or the venv. No PR unless asked.
  - Run `audit_say.py` after every script change.
  - When the owner pastes edits as tables, diff them line by line, fix typos, and flag factual changes for sign-off.

## 2. Owner decisions so far (in order)
1. Originally there was one short video per audience (GCA, prime, subcontractor). This was **superseded**.
2. "Rebuild the animation so it matches the current DD 254." Done: the on-screen form is drawn from the real fillable PDF's XFA geometry (4 pages).
3. "We are not mentioning NCCS or NI2 in this training at all." The DAU/AFMC 254 webinar transcript was supplied to improve the script.
4. "Build a script that takes roughly an hour, with logical stopping points every 10 minutes: videos 1–6."
   - Structure chosen: **follow the 254 down**.
   - The three short videos are **replaced** by the course.

## 3. Standing constraints
- **No NCCS or NI2 anywhere** (narration, on-screen text, sources list).
- **NISS** appears only in two places: verifying facility clearances (it is the system of record), and the warning never to upload a classified 254.
- **No agency seals.** The end cards say "Unofficial training aid · Not legal advice".
- **Voice:** Kokoro `bf_emma`, speed 0.95, `en-gb`.
- **Every claim traces** to the DCSA instructions for the DD 254 (APR 2018), the FAR, or 32 CFR 117.
  - The webinar shaped emphasis only. None of its Air Force–specific process is used.
  - Its claim that a prime "can't add" requirements is corrected to "not without GCA approval" (instructions 14(3)).
  - DCSA Voice of Industry newsletters are presented as reported practice, never as requirements.
- **Example contract** (fictional, unclassified by design) runs through all six parts:
  - A Secret radar signal-processor upgrade, performed at the contractor plant and a government test range.
  - **Morgan** (GCA) writes the form, **Jordan** (the prime's FSO) receives it, and **Riley's** machine shop is the subcontractor, under 11d only.
- **Owner preferences:** be critical and direct; push back where warranted; ask before any significant effort.

## 4. Course structure and runtimes (voiced 4 Oct 2026)
| Part | Title | Runtime | Words |
|---|---|---|---|
| 1 | Foundations | 9:29 | 1362 |
| 2 | Building the prime 254: items 1 to 9 | 8:56 | 1350 |
| 3 | Items 10 and 11 in depth | 9:07 | 1267 |
| 4 | Items 12 to 18, and getting it right | 8:32 | 1208 |
| 5 | The prime contractor: reading yours, issuing a subcontract 254 | 9:10 | 1294 |
| 6 | The subcontractor: living with it, and course recap | 8:10 | 1210 |
| | **Total** | **53:27** | |

- Every part opens with "where we are" and closes with "coming up next". Part 6 closes with a course recap instead.
- Every part has its own title card and a 6-second end card (sources and disclaimer).
- **Pacing:** about 0.42 s per word including pauses, so about 1,400 words makes 10 minutes.

### Scene ids and on-screen plan (narration is in the review doc)
**Part 1:**

| Scene | On screen |
|---|---|
| title | Title card |
| welcome | Course map; the cast wave in |
| example | Storyboard strip of the example contract |
| what | Real form page; item 13 text magnified |
| copies | One form, three copies: FSO, DCSA, government |
| classified | FAR 52.204-2 clause card; licences, grants and agreements; CUI-only document gets a no-mark |
| rules | Stacked books: executive order → FAR → NISPOM (32 CFR 117) → DoD manual |
| who | Org chart: GCA team, DCSA, contractor FSO |
| fcl | FCL rosette; sponsor arrow; padlock until granted; safeguarding badge; NISS card; prime ≥ sub ladder |
| terms | Classification levels, guide, derivative classification, need-to-know |
| pcl | Company FCL vs employee PCL; SF 312 |
| form | Four real pages, lit by block group |
| kinds | Solicitation, original, revised, final, subcontract forms |
| life | Life-cycle circle |
| myths | Three myth cards |
| next | Course map |

**Part 2:**

| Scene | On screen |
|---|---|
| title | Title card |
| intro | Course map; items 1–9 lit |
| prep | Morgan's prep meeting; SOW vs 254 |
| s1 | Item 1 drop-downs; NISS card |
| scenarios | Three 1a/1b situations, mapped to 11a, 11b and 11c |
| verify | NISS fields mapped to 6b, 1a and 1b; sponsorship package |
| preaward | Bidders needing classified access; GCA sponsorship during the solicitation |
| s2 | Items 2 and 3 |
| s3 | Items 4 and 5 |
| s4 | Items 6–8; DCSA as CSO; overseas row turns red |
| s5 | Item 9 |
| example | Items 1–9 filled live |
| faq | Q&A cards |
| recap | Course map |

**Part 3:**

| Scene | On screen |
|---|---|
| title | Title card |
| intro | Items 10 and 11 magnified |
| t10 | Item 10: access, not storage |
| t10a | 10a with 11h; COMSEC account |
| t10bcd | 10b, 10c, 10d; ticking 10c auto-ticks 10b |
| t10e | 10e(1) and (2); item 15 for SCI |
| t10f | 10f → item 14 "Yes" |
| t10g | NATO; SIPRNet trap |
| t10ik | 10i, 10j, 10k |
| pitfalls10 | Trap cards |
| t11 | Item 11 rules; forbidden pairings flash red |
| decide11 | Five-question flowchart |
| t11f | 11f–11m; DD 1540 to DTIC |
| costs | Cost tokens per box |
| example | Radar contract: 11c and 11d |
| recap | Course map |

**Part 4:**

| Scene | On screen |
|---|---|
| title | Title card |
| intro | Items 12–18 lit |
| s12 | Release route |
| s13 | Item 13 with guides attached |
| weak13 | Weak vs strong item 13 entry |
| example13 | Item 13 filled with the radar entries |
| s14 | Items 14 and 15 |
| s16 | Items 16 and 17 |
| dist | Item 18 distribution |
| coord | Review chain |
| check | Pre-signature checklist |
| why | Three consequence panels |
| after | Revisions, 2-year reviews, final 254 |
| faq | Q&A cards |
| recap | Course map |

**Part 5:**

| Scene | On screen |
|---|---|
| title | Title card |
| intro | Jordan receives the prime 254 |
| s1 | Read the prime form |
| actions | The 254 becomes a to-do list |
| s2 | Need test |
| bidders | Prospective subcontractors |
| s3 | NISS check; sponsorship |
| s4 | GCA approval gates |
| s5 | Sub form 2a/2b, 3a, 6–8 |
| s6 | Flow down only; added box needs a GCA stamp |
| example | Radar subcontract filled live |
| flowup | A Secret prime cannot hold a TS sub |
| s7 | Items 16 and 17; distribution |
| mistakes | Five mistake cards |
| s8 | Life of the sub form |
| chain | Three-tier chain |
| recap | Course map |

**Part 6:**

| Scene | On screen |
|---|---|
| title | Title card |
| intro | Riley receives the subcontract 254 |
| s1 | Mismarked SECRET copy; NISS upload gets a no-mark |
| s2 | Revisions |
| s3 | FCL gauge vs 1a; storage; visits |
| s4 | Duties per box (COMSEC, CNWDI, NATO) |
| s5 | Derivative classifier; training calendar |
| papers | Working papers |
| s6 | Release route |
| report | Reporting route |
| s7 | Classification challenge flow, 60 / 120 days |
| review | When DCSA visits |
| s8 | Close-out; retention |
| example | Riley's checklist |
| course | Course recap; the cast together |

## 5. Corrections made at the last fact-check (4 Oct). These are already in the review doc.
1. **11d** (part 3, "decide11"): now reads "That's 11d. Alongside 11c, add 11d only if the hardware won't fit in a standard security container." The container rule applies only when 11c is also checked (instructions 11c(2)).
2. **Pre-award access** (part 2, "preaward"): the unsupported claim that item 13 of the solicitation 254 explains pre-award access is replaced with "the GCA can sponsor them during the solicitation itself" (32 CFR 117.9(a)(10)).
3. **Continued processing** (part 5, "bidders"): now adds "as long as the delay wasn't the subcontractor's doing" (117.17(a)(3)(i)).

## 6. Decisions waiting on the owner (from the review doc)
1. **Length.** Accept 53½ minutes as "roughly an hour", or add about 1½ minutes each to:
   - part 4: a worked revision;
   - part 6: a fuller derivative-classification example;
   - part 2: a second worked example.
2. **Example contract.** Keep the fictional radar upgrade, or use something closer to the owner's work?
3. **"Not cleared or not approved to store yet? Keep going."** (part 2). This is the webinar's emphasis and is consistent with 117.9 and 117.17, with the guardrail that nothing classified moves for storage before DCSA approval.
4. **Overseas storage** is stated as a rule: 117.19 forbids contractor storage abroad except under US government control.
5. **"DCSA uses its copy to oversee the contractor"** (part 1, "Who holds a copy, and why") and **"DCSA uses them to see what you're authorized to access, store, and do"** (part 6, "When DCSA visits").
   - This is true in practice, and item 18 makes DCSA a required recipient, but no source in hand says it outright.
   - Keep it, or soften to "DCSA gets a copy because it oversees your security program"?

## 7. Verified sources (cite these; don't add claims without one)
- **32 CFR 117.3:** definitions. A classified contract includes licences, agreements and grants, and all phases of the contract.
- **117.8(c), (d):** the sub notifies the prime of certain reports; loss or compromise → preliminary inquiry and report to the CSA (and to the head of a USG site).
- **117.9(a):**
  - (4) no access until the FCL is granted;
  - (5) the prime's FCL must be ≥ the sub's;
  - (6) storage needs CSA-approved safeguarding;
  - (10) a contractor can't apply for its own FCL; a GCA or a cleared contractor sponsors it, at any point including the solicitation.
- **117.12(h):** derivative-classification training before starting, then every 2 years.
- **117.13(c)–(e):** the classification block; challenges escalate at 60 days → CSA and 120 days → ISCAP via ISOO; no adverse action for challenging.
- **117.15(j):** retention lists; working papers.
- **117.16:** visits.
- **117.17:**
  - (a)(1)(ii)(A)–(B): no FCL needed to bid if there's no pre-award access; if access is needed, the prime asks the CSA to process the bidder;
  - (a)(2): verify prospective subs;
  - (a)(3): lead time, and continued processing if the delay wasn't the sub's fault;
  - (b)–(d): subcontracting.
- **117.18:** the CSA authorizes classified information systems before use.
- **117.19:** NATO briefings and annual refresher; no contractor storage abroad except under USG control (US military facility, embassy, consulate).
- **117.20:** CNWDI briefing and records; GCA prior written approval to subcontract. Per 117.20(d), the approval may be in the 254, in another contract document, or in separate correspondence.
- **117.21:** COMSEC account and briefing; GCA written approval to subcontract.
- **117.23(a):** special categories exceed the baseline and are applied through specific contract requirements.
- **FAR:** 4.402(a)–(d); 4.403(c)(1); 52.204-2 (c) equitable adjustment for changed requirements, and (d) flow-down.
- **DCSA instructions for items 1–18 (APR 2018):**
  - 7c / 8c: no CSO other than DCSA, unless a different one applies;
  - 11a(3): if 11a, don't check 11b, 11c, 11d, 11h, 11i or 11k;
  - 11b(2): if 11b, 1b must be completed;
  - 11c(2): if 11c, don't check 11a or 11b, and check 11d only for hardware too large for a GSA container;
  - 11d/11e: recommend not checking 11e with 11c or 11d;
  - 11g(1): the GCA submits the DD 1540;
  - 11l: CUI, only alongside 10j;
  - 14(3): a prime needs GCA approval to add requirements;
  - 18: minimum distribution is DCSA, the contractor FSO, the sub FSO, the GCA POCs, and all offices checked.
- **Preliminary pages of the instructions:** NISS is the FCL system of record; the GCA or prime sponsors an FCL or an upgrade.

## 8. Pronunciation rules (the TTS "say" layer)
- "DD 254" → "D D two fifty-four"; "254" → "two fifty-four"; "254s" → "two fifty-fours".
- "FAR 52.204-2" → "far fifty-two, two oh four, dash two"; "(c)" → "paragraph C".
- "32 CFR Part 117" → "thirty-two C F R, part one seventeen".
- NISPOM → "Nisspom"; NISS → "Niss"; NISP → "N I S P"; SIPRNet → "sipper net"; NATO → "Nato"; COMSEC/OPSEC/TEMPEST/CAGE → lowercase words; CUI → "C U I"; FSO → "F S O"; DD 1540 → "D D Form fifteen forty".
- Block references: 11g → "eleven G", 1a → "one A", 17e → "seventeen E", and so on.
- Never space out an acronym ending in A before a word (DCSA and GCA are read correctly as-is). Possessives and plurals use spaced letters: "D C S A's", "G C A's".
- `audit_say.py` checks only acronym-shaped text, so hand-check any new term.
- On 4 Oct all six parts passed the audit with 0 flagged.

## 9. Toolkit notes and pitfalls (record these in the toolkit README when committing)
- **espeak error** (`phontab` not found, with kokoro-onnx 0.6.1 / espeakng-loader 0.2.4 / phonemizer 3.4.0):
  - `apt-get install libespeak-ng1 espeak-ng-data`;
  - `export PHONEMIZER_ESPEAK_LIBRARY=/usr/lib/x86_64-linux-gnu/libespeak-ng.so.1`.
- **`stills.py` naming bug:** times must be formatted like JavaScript, "3" not "3.0", or the still filenames won't match. Fix:
  ```python
  times = [f"{round(start[sc] + float(t), 2):g}" for sc, t in pairs]
  ```
- **`pkill -f tts.py` kills its own shell.** Use the pattern `"[t]ts.py bf_emma"`.
- **Long TTS runs die at the 600 s tool timeout.** Run them detached (`setsid nohup … & disown`) and wait for a done-file.
- **`scenes.html` must load** `engine.js` → `form254.js` → `props.js` → `scenes.js`.
- **The real form:**
  - The official DD 254 PDF is encrypted. Use pypdf with `cryptography` to pull the XFA template.
  - A small layout engine emulates XFA lr-tb, tb and positioned flow in mm, on a Letter page (content area x 6.35, y 8.89, w 203.2, h 257.785).
  - Result: 4 pages — items 1–8 on p1, 9–13 on p2, 13–16 on p3, 16–18 on p4.
  - `form254.js` exposes `f254page`, `f254block`, `f254zoom`. Text width is about 0.6 × font size, and short values are drawn bottom-right.
- **Props added for this course:** cast (morgan, jordan, riley, subco); helpers (card, flyer, tag, noMark, arrow, leader); form widgets (field, pills, checkbox); `formWithZoom` layout (form at x 178, y 318; zoom panel x 820, y 100, 880×300); PCL props copied in (calendar, book, magnifier, key, board, rosette).

## 10. What was lost (container reset between 4 Oct and 31 Oct)
The whole scratch workspace was lost. None of it was committed:
- `mkcourse.py`, the source of truth for the six scripts, including the regex "say" map and the scene builder;
- `mkcoursereview.py` and the review template;
- the XFA layout tooling (`xfa_layout.py`, `build_form.py`, `form254.tmpl.js`, `form254.json`);
- `props.js`;
- the earlier GCA scene code;
- the voiced audio;
- the downloaded sources.

**Recoverable:**
- All narration and on-screen notes, from the review doc.
- Everything in this file.
- The approach, which is reproducible: re-download the DD 254 PDF and instructions from DCSA / the DoD forms site, and 32 CFR 117 from eCFR.

**Lesson for next time:** commit scratch tooling to the work branch at each checkpoint, even before approval, outside `examples/` if necessary, so a container reset can't wipe it.

## 11. Next steps once the owner approves
1. Apply the owner's answers to section 6, and any pasted edits (diff line by line; flag factual changes).
2. Rebuild the toolkit for the course:
   - `script.json` per part, generated from the review doc's narration plus the say rules in section 8;
   - the form tooling and `props.js`.
3. Voice all six parts, verify the timelines match the scripts, and run `audit_say.py`.
4. Build `scenes.js` per part, then review contact sheets scene by scene.
5. `render_full.sh` per part. Verify duration, audio peak ≤ −1.4 dB, and the chunk joins.
6. Commit to `claude/dd254-video`:
   - `video-toolkit/examples/dd254/` (scripts, scenes, review doc, form tooling);
   - the toolkit fixes, with the README pitfalls from section 9;
   - one `HANDOFF.md` log entry.
   - No MP4s, voices or venv. No PR unless asked.

## 12. Repo housekeeping (CLAUDE.md rules)
- `HANDOFF.md` at the repo root is the shared state between Claude and Codex.
- **At session start:** read it, and check what changed since its `Last updated` watermark.
- **While working:** append a log entry after each meaningful unit of work. Overwrite `Current State`, and keep the log trimmed to about 15 entries.
- Entries stay at decision level: no transcripts, no personal data.
