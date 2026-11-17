# Notes for producing the course in Google Flow

These notes record the constraints from the course's design that carry over to any AI video tool. They are not a shot list. Read `course-handoff.md` first.

## Where Flow fits and where it doesn't
- **Use it for:**
  - character moments (Morgan, Jordan and Riley at work, handing over a form, a facility, a test range, a machine shop);
  - establishing shots;
  - transitions.
- **Don't use it for the DD 254 itself.**
  - Generative video garbles small text, and this course depends on viewers reading real block numbers (1a, 11c, item 13) on the **real APR 2018 form**.
  - Keep every form close-up, block highlight and filled-in value as rendered graphics, from the toolkit's XFA-based form or a screen recording of the official fillable PDF. Composite them over Flow footage in an editor.
- **Clips are short** (about 8 seconds each), and each scene in the review doc runs 15–50 seconds. Plan several clips per scene, or one clip plus a graphic.
- **Narration:**
  - Keep a single voice for all six parts: Kokoro `bf_emma`, 0.95, en-gb, or one human narrator.
  - Mixing in Flow-generated speech will change the voice between clips.
  - If Flow adds audio, mute it and lay the narration under the footage.

## Hard rules that still apply
- **No NCCS or NI2** anywhere: not on a screen in the background, not in a prompt.
- **No agency seals, logos or real program names.** The end card says "Unofficial training aid · Not legal advice".
- **Don't depict realistic classified material.**
  - Marked props are fine as obvious cartoons ("SECRET" on a folder).
  - Never generate anything that could pass for a real marked document, a real facility or a real person.
- **The example contract stays fictional:** a Secret radar signal-processor upgrade, the contractor plant, a government test range, and Riley's machine shop.

## Consistency across clips
- **Write one character sheet before generating anything,** and reuse it word for word in every prompt. For each of Morgan (GCA), Jordan (prime FSO) and Riley (machine-shop owner), give appearance, clothing, colour palette and art style.
  - The original cartoon designs were lost in the container reset, so this is a fresh design decision for the owner.
  - Use Flow's reference-image ("ingredients") feature to lock the look.
- **Fix one art style for the whole course** (flat 2D cartoon, matching the PCL video's look) and state it in every prompt.

## Mapping
Use the scene ids and on-screen notes in `course-handoff.md` §4 as the shot plan. Each "On screen" note marks which elements are footage (characters, places) and which are graphics (the form, chips, arrows, checklists).
