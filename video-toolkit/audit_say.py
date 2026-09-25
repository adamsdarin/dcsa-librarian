"""Print the phonemes for every acronym in script.json, in context, and flag known misreads.

Kokoro reads a spaced single letter "A" before a word as the article ("D C S A may" -> "D C S a-may"),
and drops the possessive from an all-caps acronym ("DOHA's" -> "Doha-r", "DCSA's" -> "DCSA").
Run this after every script edit; listen for anything flagged.
Usage: venv/bin/python audit_say.py [lang]"""
import json, re, sys
from kokoro_onnx import Kokoro
lang = sys.argv[1] if len(sys.argv) > 1 else "en-gb"
k = Kokoro("voices/kokoro-v1.0.onnx", "voices/voices-v1.0.bin")
flags = 0
for sc in json.load(open("script.json"))["scenes"]:
    for line in sc["lines"]:
        say = line.get("say", line["cap"])
        for m in re.finditer(r"\b(?:[A-Z] )+[A-Z]\b|\b[A-Z]{2,}\b|\d[\d-]{3,}", say):
            frag = say[max(0, m.start() - 6): m.end() + 10]
            tail = say[m.start(): m.end() + 3]
            risky = bool(re.search(r"\b[A-Z] A \w", tail) or re.match(r"[A-Z]{2,}'s", tail))
            flags += risky
            print(("FLAG " if risky else "     ") + f"{sc['id']:8s} {frag!r:36s} {k.tokenizer.phonemize(frag, lang=lang)}")
print(f"{flags} flagged")
