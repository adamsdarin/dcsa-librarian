# Google Flow pilot: style lock, cast sheet and Part 1 clips

**Purpose.** Before committing to six parts, test whether Flow can (a) keep Morgan, Jordan and Riley
consistent across clips and (b) sit next to the toolkit's flat vector graphics without looking like a
different course. Part 1 is the pilot. Spend no credits on Parts 2–6 until the checklist at the end passes.

**Status (17 Nov 2026).** Drafted; owner approved the pilot and kept the fictional radar contract
(decision 2). Character designs below are proposals for the owner to accept or change. Narration
timings for Part 1 are not yet known (the review doc is still missing), so clip lengths are estimates.

**Flow feature names change.** "Ingredients", "Frames to video", "Extend" and the image generator are
named as they were when this was written; check the current Flow UI before relying on them.

---

## 1. Style lock (paste at the start of every prompt)

**Decided 17 Nov 2026: Option A.** Option B is kept below only for the record.

**Option A: flat 2D vector (chosen)**
> Flat 2D vector cartoon, educational explainer style. Thick dark navy-charcoal outlines (#2b2d42) of even
> weight, flat fills, no gradients, no textures, soft simple shadows only. Rounded friendly shapes,
> slightly oversized heads, simple dot eyes. Palette: cream walls (#fbeed7), warm tan floors (#e3c9a0),
> teal (#2a9d8f), navy (#1d3557), mustard yellow (#e9c46a), soft orange (#f4a261), coral (#e76f51),
> pale sky blue (#dff1f7). Gentle, smooth, limited animation. 16:9.

**Option B: soft 3D clay (not chosen)**
> Stylized soft 3D clay-like cartoon, matte surfaces, rounded forms, warm studio lighting, shallow depth of
> field, same palette as above. 16:9.

B will probably look better and drift less in Flow, but it will clash with the flat form graphics. Choose B
only if you're willing to restyle the graphics to match, which is a much bigger job.

## 2. Exclusions (paste at the end of every prompt)

> No text, letters, numbers, labels, signs, screens with readable content, logos, seals, emblems, flags,
> insignia, badges with writing, or uniforms. No real people or likenesses. No dialogue; characters do not
> speak; mouths closed or smiling. No music or voices.

Why "no text" is absolute: Flow garbles text, and anything with words in it (labels, "SECRET" folder marks,
item numbers) is added as a graphic overlay in the editor. That also keeps NCCS, NI2, seals and real
program names out by construction. Mute whatever audio Flow generates anyway.

## 3. Cast sheet (reuse word for word)

These are fresh designs: the originals were lost. **Accepted by the owner on 17 Nov 2026.** If the review
doc later turns out to use pronouns that conflict with a design, flag it rather than silently changing either.

**MORGAN, government contracting officer's security representative (the GCA)**
> MORGAN: a woman in her mid-40s with medium-brown skin, short dark curly hair and round black glasses.
> Navy blazer (#1d3557) over a pale sky-blue shirt (#dff1f7), grey trousers, black flats. Carries a plain
> manila folder. A blank lanyard card with no writing. Calm, organised, precise gestures.

**JORDAN, the prime contractor's facility security officer (FSO)**
> JORDAN: a man in his early 30s with light-olive skin and short straight black hair, neatly parted.
> Teal quarter-zip sweater (#2a9d8f) over a white collar, khaki trousers, brown shoes. Carries a plain
> grey tablet with a blank screen. Friendly, attentive, quick to nod.

**RILEY, owner of the machine-shop subcontractor**
> RILEY: a person in their mid-50s with light skin, a short grey beard and a grey buzz cut. Soft-orange
> work shirt (#f4a261) with sleeves rolled up, dark charcoal canvas apron, clear safety glasses pushed up
> on the forehead. Sturdy, practical, warm smile.

## 4. Location sheet (reuse word for word)

> **GOV OFFICE:** a tidy government office with cream walls, a wooden desk, a grey filing cabinet, a potted
> plant and a window with pale blue sky. Plain walls: no flags, seals, framed emblems or posters.

> **PLANT LAB:** a clean, bright electronics lab at a contractor plant. A workbench with a generic grey
> electronics chassis, its lid open to show green circuit boards, and a small instrument with a blank
> screen. Teal and white walls, no signs.

> **MACHINE SHOP:** a small, warm-lit machine shop with a milling machine, a workbench, neat tool racks and
> a few bare aluminium housings on a cart. No signs or labels.

> **TEST RANGE:** open desert scrubland under a wide pale-blue sky. A trailer-mounted radar dish, painted
> plain white, slowly turning behind a chain-link fence. No vehicles with markings, no military insignia.

## 5. Making the references (do this first; about 10 image generations)

1. Generate each character alone, full body, standing, front three-quarter view, plain cream background,
   using: style lock + that character's line + exclusions. Make 3–4 variants each and pick one.
2. Generate each location empty, same way. Pick one each.
3. Save the picked images; they're the ingredients for every clip. Commit their **prompts and seeds**, not
   the images, to this folder once chosen (decide later whether the images themselves belong in the repo).
4. Optional style anchor: a still of the toolkit's flat-vector look can be uploaded as a style reference.
   The PCL video's frames are the closest thing that exists today.


### 5a. Ready-to-paste reference image prompts

Each block is complete: style lock, subject and exclusions already joined. Generate 3–4 variants of each and keep one.

**R1 · MORGAN (character reference)**
```
Flat 2D vector cartoon, educational explainer style. Thick dark navy-charcoal outlines (#2b2d42) of even weight, flat fills, no gradients, no textures, soft simple shadows only. Rounded friendly shapes, slightly oversized heads, simple dot eyes. Palette: cream walls (#fbeed7), warm tan floors (#e3c9a0), teal (#2a9d8f), navy (#1d3557), mustard yellow (#e9c46a), soft orange (#f4a261), coral (#e76f51), pale sky blue (#dff1f7). 16:9. Full-body character reference: MORGAN: a woman in her mid-40s with medium-brown skin, short dark curly hair and round black glasses. Navy blazer (#1d3557) over a pale sky-blue shirt (#dff1f7), grey trousers, black flats. Carries a plain manila folder. A blank lanyard card with no writing. Calm, organised, precise gestures. Standing alone, front three-quarter view, neutral pose, plain cream background (#fbeed7). No text, letters, numbers, labels, signs, screens with readable content, logos, seals, emblems, flags, insignia, badges with writing, or uniforms. No real people or likenesses. No dialogue; characters do not speak; mouths closed or smiling. No music or voices.
```

**R2 · JORDAN (character reference)**
```
Flat 2D vector cartoon, educational explainer style. Thick dark navy-charcoal outlines (#2b2d42) of even weight, flat fills, no gradients, no textures, soft simple shadows only. Rounded friendly shapes, slightly oversized heads, simple dot eyes. Palette: cream walls (#fbeed7), warm tan floors (#e3c9a0), teal (#2a9d8f), navy (#1d3557), mustard yellow (#e9c46a), soft orange (#f4a261), coral (#e76f51), pale sky blue (#dff1f7). 16:9. Full-body character reference: JORDAN: a man in his early 30s with light-olive skin and short straight black hair, neatly parted. Teal quarter-zip sweater (#2a9d8f) over a white collar, khaki trousers, brown shoes. Carries a plain grey tablet with a blank screen. Friendly, attentive, quick to nod. Standing alone, front three-quarter view, neutral pose, plain cream background (#fbeed7). No text, letters, numbers, labels, signs, screens with readable content, logos, seals, emblems, flags, insignia, badges with writing, or uniforms. No real people or likenesses. No dialogue; characters do not speak; mouths closed or smiling. No music or voices.
```

**R3 · RILEY (character reference)**
```
Flat 2D vector cartoon, educational explainer style. Thick dark navy-charcoal outlines (#2b2d42) of even weight, flat fills, no gradients, no textures, soft simple shadows only. Rounded friendly shapes, slightly oversized heads, simple dot eyes. Palette: cream walls (#fbeed7), warm tan floors (#e3c9a0), teal (#2a9d8f), navy (#1d3557), mustard yellow (#e9c46a), soft orange (#f4a261), coral (#e76f51), pale sky blue (#dff1f7). 16:9. Full-body character reference: RILEY: a person in their mid-50s with light skin, a short grey beard and a grey buzz cut. Soft-orange work shirt (#f4a261) with sleeves rolled up, dark charcoal canvas apron, clear safety glasses pushed up on the forehead. Sturdy, practical, warm smile. Standing alone, front three-quarter view, neutral pose, plain cream background (#fbeed7). No text, letters, numbers, labels, signs, screens with readable content, logos, seals, emblems, flags, insignia, badges with writing, or uniforms. No real people or likenesses. No dialogue; characters do not speak; mouths closed or smiling. No music or voices.
```

**R4 · GOV OFFICE (location reference)**
```
Flat 2D vector cartoon, educational explainer style. Thick dark navy-charcoal outlines (#2b2d42) of even weight, flat fills, no gradients, no textures, soft simple shadows only. Rounded friendly shapes, slightly oversized heads, simple dot eyes. Palette: cream walls (#fbeed7), warm tan floors (#e3c9a0), teal (#2a9d8f), navy (#1d3557), mustard yellow (#e9c46a), soft orange (#f4a261), coral (#e76f51), pale sky blue (#dff1f7). 16:9. Empty establishing view, no people: GOV OFFICE: a tidy government office with cream walls, a wooden desk, a grey filing cabinet, a potted plant and a window with pale blue sky. Plain walls: no flags, seals, framed emblems or posters. Wide shot, eye level. No text, letters, numbers, labels, signs, screens with readable content, logos, seals, emblems, flags, insignia, badges with writing, or uniforms. No real people or likenesses. No dialogue; characters do not speak; mouths closed or smiling. No music or voices.
```

**R5 · PLANT LAB (location reference)**
```
Flat 2D vector cartoon, educational explainer style. Thick dark navy-charcoal outlines (#2b2d42) of even weight, flat fills, no gradients, no textures, soft simple shadows only. Rounded friendly shapes, slightly oversized heads, simple dot eyes. Palette: cream walls (#fbeed7), warm tan floors (#e3c9a0), teal (#2a9d8f), navy (#1d3557), mustard yellow (#e9c46a), soft orange (#f4a261), coral (#e76f51), pale sky blue (#dff1f7). 16:9. Empty establishing view, no people: PLANT LAB: a clean, bright electronics lab at a contractor plant. A workbench with a generic grey electronics chassis, its lid open to show green circuit boards, and a small instrument with a blank screen. Teal and white walls, no signs. Wide shot, eye level. No text, letters, numbers, labels, signs, screens with readable content, logos, seals, emblems, flags, insignia, badges with writing, or uniforms. No real people or likenesses. No dialogue; characters do not speak; mouths closed or smiling. No music or voices.
```

**R6 · MACHINE SHOP (location reference)**
```
Flat 2D vector cartoon, educational explainer style. Thick dark navy-charcoal outlines (#2b2d42) of even weight, flat fills, no gradients, no textures, soft simple shadows only. Rounded friendly shapes, slightly oversized heads, simple dot eyes. Palette: cream walls (#fbeed7), warm tan floors (#e3c9a0), teal (#2a9d8f), navy (#1d3557), mustard yellow (#e9c46a), soft orange (#f4a261), coral (#e76f51), pale sky blue (#dff1f7). 16:9. Empty establishing view, no people: MACHINE SHOP: a small, warm-lit machine shop with a milling machine, a workbench, neat tool racks and a few bare aluminium housings on a cart. No signs or labels. Wide shot, eye level. No text, letters, numbers, labels, signs, screens with readable content, logos, seals, emblems, flags, insignia, badges with writing, or uniforms. No real people or likenesses. No dialogue; characters do not speak; mouths closed or smiling. No music or voices.
```

**R7 · TEST RANGE (location reference)**
```
Flat 2D vector cartoon, educational explainer style. Thick dark navy-charcoal outlines (#2b2d42) of even weight, flat fills, no gradients, no textures, soft simple shadows only. Rounded friendly shapes, slightly oversized heads, simple dot eyes. Palette: cream walls (#fbeed7), warm tan floors (#e3c9a0), teal (#2a9d8f), navy (#1d3557), mustard yellow (#e9c46a), soft orange (#f4a261), coral (#e76f51), pale sky blue (#dff1f7). 16:9. Empty establishing view, no people: TEST RANGE: open desert scrubland under a wide pale-blue sky. A trailer-mounted radar dish, painted plain white, behind a chain-link fence. No vehicles with markings, no military insignia. Wide shot, eye level. No text, letters, numbers, labels, signs, screens with readable content, logos, seals, emblems, flags, insignia, badges with writing, or uniforms. No real people or likenesses. No dialogue; characters do not speak; mouths closed or smiling. No music or voices.
```

## 6. Part 1: footage or graphics, scene by scene

Part 1 runs 9:29 over 16 scenes, so about 35 s per scene on average. Flow clips are about 8 s.

| Scene | On screen (from course-handoff.md) | Flow? | Clips |
|---|---|---|---|
| title | Title card | Graphics. Optional background plate: reuse clip P1-04 | 0 |
| welcome | Course map; the cast wave in | **Flow** for the wave-in, then cut to the graphic map | 1 |
| example | Storyboard strip of the example contract | **Flow**: four establishing shots, one per place | 4 |
| what | Real form page; item 13 magnified | Graphics only | 0 |
| copies | One form, three copies | Graphics; optional Flow cutaway of Jordan | 0–1 |
| classified | FAR clause card; CUI no-mark | Graphics only | 0 |
| rules | Stacked books | Graphics only | 0 |
| who | Org chart | Graphics, with **character stills** from §5 as portraits | 0 |
| fcl | FCL rosette, NISS card, ladder | Graphics only | 0 |
| terms | Classification terms | Graphics only | 0 |
| pcl | Company FCL vs employee PCL; SF 312 | Graphics only (don't generate the SF 312) | 0 |
| form | Four real pages | Graphics only | 0 |
| kinds | Five form types | Graphics only | 0 |
| life | Life-cycle circle | Graphics only | 0 |
| myths | Myth cards | Graphics only | 0 |
| next | Course map | Graphics; optional reuse of P1-01 | 0 |

**Total: 5 clips, plus 1 optional.** Roughly 40–50 s of footage in a 9½-minute part (about 8%). The four
establishing shots in `example` are reusable throughout the course, so they're the best value in the pilot.

## 7. Part 1 clip prompts

Every prompt is: **style lock + the text below + exclusions**, with the named character and location
reference images attached as ingredients.

**P1-01 · welcome · cast wave-in (8 s)** — ingredients: Morgan, Jordan, Riley
> MORGAN, JORDAN and RILEY walk in from the left, one after another, onto a plain cream background, stop
> side by side facing the camera and give a small friendly wave. Static camera, medium-wide shot.

**P1-02 · example · Morgan's office (8 s)** — ingredients: Morgan, GOV OFFICE
> In the GOV OFFICE, MORGAN sits at the desk, closes a plain manila folder, stands and holds it out toward
> the right of frame as if handing it on. Slow push-in, medium shot.

**P1-03 · example · the plant lab (8 s)** — ingredients: Jordan, PLANT LAB
> In the PLANT LAB, JORDAN walks along the workbench past the open grey electronics chassis, glances at the
> blank tablet and nods. Slow pan
> left to right.

**P1-04 · example · the test range (8 s)** — ingredients: TEST RANGE
> At the TEST RANGE, the white radar dish turns slowly on its trailer behind the chain-link fence. Light
> heat shimmer, a few small clouds drift. Wide establishing shot, very slow push-in. No people.

**P1-05 · example · Riley's shop (8 s)** — ingredients: Riley, MACHINE SHOP
> In the MACHINE SHOP, RILEY lifts a bare aluminium housing from the cart, turns it over to inspect it,
> and sets it on the workbench with a satisfied nod. Medium shot, static camera.

**P1-06 (optional) · copies · Jordan files the form (8 s)** — ingredients: Jordan, PLANT LAB
> At a desk in a corner of the PLANT LAB, JORDAN places a plain blank sheet of paper into a grey
> binder and closes it. Close-medium shot, static camera.

The paper in P1-06 must stay blank; the real DD 254 page is composited over it if needed. If Flow puts
writing on it, regenerate or drop the clip.

## 8. Pilot pass/fail checklist

Run all five core clips, then judge:
1. **Identity.** Is each character recognisably the same person across every clip they're in (face, hair,
   clothing colours)? Two failed regenerations in a row for one character is a fail.
2. **Style match.** Put a clip next to a flat-vector graphic frame. Do they read as one course?
3. **No text.** Is any letter-like mark visible anywhere? Even garbled text is a fail; regenerate.
4. **Nothing realistic.** No seals, flags, insignia or real-looking marked documents.
5. **Cost.** Record credits used per kept clip. Multiply by the clips needed for Parts 2–6 (estimated at
   3–8 per part) before going further.

**If 1 or 2 fails:** the fallback is the original plan, toolkit-only animation, which needs the lost
tooling rebuilt (course-handoff.md §10–11). That decision goes to the owner with the pilot results.

## 9. Still open for this pilot
- Which editor composites clips, graphics, captions and narration.
- `dd254-course-script-review.md` is still needed: it fixes the scene timings and any character pronouns.
