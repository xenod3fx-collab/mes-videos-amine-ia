#!/usr/bin/env python3
"""Génère les voix off ElevenLabs (un fichier par hook et par plan) dans montage/voix-off."""
import os, sys, json, urllib.request, importlib.util
here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("build", os.path.join(here, "build.py"))
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
OUT = os.path.join(here, "..", "montage", "voix-off"); os.makedirs(OUT, exist_ok=True)
VOICES = {"homme": "Qrl71rx6Yg8RvyPYRGCQ",   # Olivier (fr)
          "femme": "Hy28BjVfgieDVMiyQpQe"}   # Chloé (fr, UGC)
def tts(text, voice, path):
    if os.path.exists(path): return
    body = json.dumps({"text": text, "model_id": "eleven_multilingual_v2", "language_code": "fr",
        "voice_settings": {"stability": 0.4, "similarity_boost": 0.75, "style": 0.15, "use_speaker_boost": True}}).encode()
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128",
        data=body, headers={"xi-api-key": "dummy", "Content-Type": "application/json"})
    open(path, "wb").write(urllib.request.urlopen(req).read()); print(path)
for vid, angle, ref, dur, dh, alts, voix, plans in b.V:
    v = VOICES[voix]
    for h in [dh] + alts:
        tts(b.HOOKS[h], v, f"{OUT}/V{vid}_{angle}_hook_H{h}.mp3")
    for i, (a, e, img, son, vo, tx) in enumerate(plans):
        if vo == "HOOK" or "[offre]" in vo: continue   # carton final : offre/site pas encore connus
        tts(vo, v, f"{OUT}/V{vid}_{angle}_plan{i+1}_{a}-{e}s.mp3")
