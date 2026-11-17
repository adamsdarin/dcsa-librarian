# DD 254 course in Google Flow: handoff for a local chat

Load this file at the start of a local Claude chat (desktop app, with Computer use and Claude in Chrome on). It is self-contained. The repo files below give more detail if you can reach them.

## What we're making
- **The course:** a six-part narrated cartoon course on completing **DD Form 254** (APR 2018 edition), about 53 minutes in all.
- **Approach:** it follows one form down the chain: the government builds it, the prime contractor issues a subcontract form, the subcontractor lives with it.
- **The example contract** is fictional: a Secret radar signal-processor upgrade.
- **Production** is in **Google Flow**. **Part 1 is the pilot**; nothing is generated for Parts 2–6 until the pilot passes.

## Files
- **Repo:** `adamsdarin/dcsa-librarian`, branch **`claude/dd254-video`**, folder `video-toolkit/examples/dd254/`:
  - `course-handoff.md`: brief, rules, scene-by-scene plan for all six parts, sources, pronunciation, the 5 open decisions;
  - `flow-pilot-part1.md`: the fixed art style, cast sheet (Morgan, Jordan, Riley), location prompts, Part 1 clip drafts, pilot checklist;
  - `google-flow-notes.md`: what Flow should and shouldn't make;
  - `surviving-narration.md`: narration for 9 scenes.
- **`dd254-course-script-review.md`:** the full narration for all six parts. It is **not in the repo**; the owner has it locally. Ask for it before writing any clip-level narration.

## Decisions already made (don't reopen)
1. **Voices:** use Flow's own character voices, not a separate voice-over.
2. **A narrator character, AVERY,** speaks all the narration. Morgan (GCA), Jordan (prime FSO) and Riley (machine-shop subcontractor) act but don't speak.
3. **Art style:** flat 2D vector ("Option A" in `flow-pilot-part1.md`). The cast designs there are accepted.
4. **Part 1 first,** as the pilot.

## Hard rules
- **No NCCS or NI2** anywhere: not in narration, prompts or backgrounds.
- **No agency seals, logos, flags, insignia or real program names.** No real people or likenesses.
- **Never generate the DD 254 form, or any readable text, in Flow.** Flow garbles text. Form close-ups, block numbers, captions and labels are added as graphics in the editor.
- **Ask before generating anything.** Every Flow generation costs credits.
- **The owner chooses voices by ear.** Claude can't hear audio: shortlist from names and descriptions only.

## AVERY, the narrator (new; not yet created in Flow)
**Character description** (paste into Flow's Character tool, named AVERY):
> Flat 2D vector cartoon, educational explainer style. Thick dark navy-charcoal outlines (#2b2d42) of even weight, flat fills, no gradients, no textures, soft simple shadows only. Rounded friendly shapes, slightly oversized heads, simple dot eyes. Palette: cream walls (#fbeed7), warm tan floors (#e3c9a0), teal (#2a9d8f), navy (#1d3557), mustard yellow (#e9c46a), soft orange (#f4a261), coral (#e76f51), pale sky blue (#dff1f7). 16:9. Full-body character reference: AVERY, the course narrator and guide: a woman in her late 50s with warm brown skin, silver-grey hair in a neat low bun, and small rectangular tortoiseshell glasses. Mustard-yellow cardigan (#e9c46a) over a cream top, a coral scarf (#e76f51), dark navy trousers, comfortable tan shoes. Holds a slim pointer stick. Warm, unhurried, encouraging; speaks directly to the viewer like a favourite instructor. Standing alone, front view facing camera, relaxed open-hand gesture, plain cream background (#fbeed7). No text, letters, numbers, labels, signs, logos, seals, emblems, flags, insignia, badges with writing, or uniforms. No real people or likenesses.

AVERY's colours (mustard and coral) are deliberately unused by the other three characters.

**Presenter set** (location for on-camera shots):
> *[style lock from `flow-pilot-part1.md` §1]* Empty establishing view, no people: PRESENTER SET: a simple, bright studio corner with a cream wall (#fbeed7), a warm tan floor (#e3c9a0), a tall mustard-yellow stool, a small potted plant, and a large blank pale-sky-blue board (#dff1f7) on an easel, its surface completely empty for graphics to be added later. Medium-wide shot, eye level. *[exclusions from §2]*

The blank board is where form close-ups get composited, so AVERY can "point at" the DD 254 without Flow drawing it.

**Ending for AVERY's speaking clips.** This replaces "No dialogue; characters do not speak; mouths closed":
> AVERY speaks directly to camera, clear natural lip movement, calm pace. Only AVERY speaks. No music.

Non-speaking clips keep the original exclusions line.

## Voice selection criteria for AVERY
- Calm, clear, mid-pitched, unhurried, with crisp consonants. Clarity matters more than personality: she says "eleven C" and "D D two fifty-four" hundreds of times.
- A **British female** voice if Flow has one, to match the owner's earlier clearance video. Otherwise any clear female voice.
- Avoid breathy, very bright or announcer-style voices; they tire viewers over 53 minutes.
- **Test line** for each finalist: "Item eleven C on the D D two fifty-four means the contractor will receive, store, and generate classified information."

## Pronunciation in spoken lines
Write lines exactly as they should be spoken:

| Written | Spoken |
|---|---|
| DD 254 | D D two fifty-four |
| 254 | two fifty-four |
| 11c | eleven C (same pattern for other blocks) |
| NISPOM | Nisspom |
| NISS | Niss |
| NISP | N I S P |
| FSO | F S O |
| CUI | C U I |
| FAR 52.204-2 | far fifty-two, two oh four, dash two |
| 32 CFR Part 117 | thirty-two C F R, part one seventeen |
| SIPRNet | sipper net |

Possessives use spaced letters: "D C S A's", "G C A's". Captions in the editor use the normal spelling.

## First task for the local chat
1. Open Google Flow in Chrome. Find the character voice list (Character tool or Voice ingredients; names may have changed).
2. Record **every** voice's name and any written description in a table. Change nothing and generate nothing.
3. Shortlist **3–4 for AVERY** against the criteria above, with a one-line reason each.
4. Stop. The owner generates the test line with each finalist and picks by ear.

## Next tasks (after the voice is chosen)
1. Create AVERY in Flow with the chosen voice, plus the presenter set.
2. **Voice test, 3 clips:**
   - AVERY on camera;
   - AVERY speaking off camera over a shot of Jordan;
   - a term-dense line (the test line above).

   Confirm that her voice holds when she's out of frame. If it doesn't, she must appear in every speaking clip, which reshapes the build sheet.
3. **Build `flow-buildsheet-part1.md`** from the review doc: one row per ~8 s clip, all 16 Part 1 scenes in order. Columns:
   - clip ID and running time;
   - AVERY's line, at most about 18 words, written as spoken;
   - narrator on or off camera;
   - the paste-ready Flow prompt;
   - the ingredients to attach;
   - the editor overlay (form graphics, captions, arrows).

   Stop for the owner's review before Parts 2–6.

## Working style the owner expects
Be critical and direct; push back when something is suboptimal. Ask before any significant effort or credit spend. Report outcomes honestly, including what didn't work.
