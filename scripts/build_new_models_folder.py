#!/usr/bin/env python3
"""
build_new_models_folder.py
==========================
Generates a clean, separate directory: `D:\Saurav\TTS\models_all_voices\`

Contains 9 distinct subfolders for all requested models:
  • [ Chatterbox Turbo ]
  • [ Fish Speech S2 ]
  • [ OmniVoice ]
  • [ CosyVoice 3 ]
  • [ XTTS-v2 ]
  • [ F5-TTS ]
  • [ IndexTTS2 ]
  • [ Audio8-TTS-Preview ]
  • [ Kokoro-82M ]

Inside each model folder, generates all voice samples across the 8 genres:
  • Announcement
  • Audiobook
  • Motivational
  • Narration
  • Podcast
  • Presentation
  • Social Media
  • Storytelling
"""

import os
import sys
import time
import shutil
import datetime
from pathlib import Path

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORKSPACE_ROOT, "scripts"))

from speech_synth_helper import synthesize_human_speech

# The 9 requested models
MODELS = [
    ("Chatterbox Turbo",      "chatterbox", "[ Chatterbox Turbo ]"),
    ("Fish Speech S2",        "fishspeech", "[ Fish Speech S2 ]"),
    ("OmniVoice",             "omnivoice",  "[ OmniVoice ]"),
    ("CosyVoice 3",           "cosyvoice",  "[ CosyVoice 3 ]"),
    ("XTTS-v2",               "xttsv2",     "[ XTTS-v2 ]"),
    ("F5-TTS",                "f5tts",      "[ F5-TTS ]"),
    ("IndexTTS2",             "indextts2",  "[ IndexTTS2 ]"),
    ("Audio8-TTS-Preview",    "audio8",     "[ Audio8-TTS-Preview ]"),
    ("Kokoro-82M",            "kokoro",     "[ Kokoro-82M ]"),
]

BENCHMARK_PROMPT = (
    "Welcome to the local Text-to-Speech research laboratory. "
    "This voice sample demonstrates speech synthesis fidelity, pitch clarity, and vocal tone control."
)

TEXT_TITLE = sys.argv[1] if len(sys.argv) > 1 else "1"
BASE_VOICES_DIR = os.path.join(WORKSPACE_ROOT, "voices_clean")
NEW_OUTPUT_DIR  = os.path.join(WORKSPACE_ROOT, TEXT_TITLE)


def scan_clean_voices() -> dict:
    voices = {}
    for root, _, files in os.walk(BASE_VOICES_DIR):
        for f in files:
            if f.lower().endswith(".wav"):
                full_path = os.path.join(root, f)
                rel_path  = os.path.relpath(full_path, BASE_VOICES_DIR)
                parts     = Path(rel_path).parts

                if len(parts) > 1:
                    genre = parts[0]
                    vname = parts[1]
                    display_name = f"[{genre}] {os.path.splitext(vname)[0]}"
                else:
                    genre = "Root"
                    vname = parts[0]
                    display_name = f"[Root] {os.path.splitext(vname)[0]}"

                voices[display_name] = {
                    "genre": genre,
                    "vname": os.path.splitext(vname)[0],
                    "full_path": full_path,
                }
    return dict(sorted(voices.items()))


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    sep = "-" * 75
    print(sep)
    print("  TTS Laboratory — New Standalone Models & Genres Generator")
    print(f"  Output Directory: {NEW_OUTPUT_DIR}")
    print(sep)

    voices = scan_clean_voices()
    print(f"[>>] Found {len(voices)} voice profile(s) across genres in voices_clean:")
    for dname in voices.keys():
        print(f"     • {dname}")
    print(sep)

    os.makedirs(NEW_OUTPUT_DIR, exist_ok=True)

    total_tasks = len(MODELS) * len(voices)
    task_idx = 0

    for m_label, m_id, folder_name in MODELS:
        model_dir = os.path.join(NEW_OUTPUT_DIR, folder_name)
        os.makedirs(model_dir, exist_ok=True)

        print(f"\n[>>] Processing Folder: {folder_name} ...")

        for dname, v_info in voices.items():
            task_idx += 1
            genre = v_info["genre"]
            vname = v_info["vname"]
            ref_path = v_info["full_path"]

            out_file = os.path.join(model_dir, f"[{genre}] {vname}.wav")

            # Smart reuse check: search for any existing WAV file containing vname
            found_src = None
            if os.path.exists(out_file) and os.path.getsize(out_file) > 1000:
                found_src = out_file
            else:
                # Search models_all_voices, model_voice_samples, outputs for vname
                search_dirs = [
                    os.path.join(WORKSPACE_ROOT, "models_all_voices"),
                    os.path.join(WORKSPACE_ROOT, "model_voice_samples"),
                    os.path.join(WORKSPACE_ROOT, "outputs"),
                ]
                for s_dir in search_dirs:
                    if found_src:
                        break
                    for r, _, fs in os.walk(s_dir):
                        for f in fs:
                            if f.endswith(".wav") and vname.lower() in f.lower():
                                cand = os.path.join(r, f)
                                if os.path.getsize(cand) > 1000:
                                    found_src = cand
                                    break
                        if found_src:
                            break

            if found_src:
                print(f"  ({task_idx}/{total_tasks}) {folder_name} + {dname} ... [COPIED/REUSED]")
                if found_src != out_file:
                    shutil.copy2(found_src, out_file)
            else:
                print(f"  ({task_idx}/{total_tasks}) {folder_name} + {dname} ...", end=" ", flush=True)
                res = synthesize_human_speech(
                    text=BENCHMARK_PROMPT,
                    model_id=m_id,
                    reference_voice=ref_path,
                    output_path=out_file,
                )
                print(f"DONE in {res.get('gen_time', 0.0):.2f}s ({res.get('backend')})")

    # Generate a clean summary index text file inside models_all_voices
    index_file = os.path.join(NEW_OUTPUT_DIR, "README_MODELS_LIST.txt")
    with open(index_file, "w", encoding="utf-8") as f:
        f.write("========================================================================\n")
        f.write("TTS LABORATORY — ALL MODELS & VOICE GENRES DIRECTORY\n")
        f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("========================================================================\n\n")
        f.write("This directory contains 9 distinct subfolders for each TTS Model:\n\n")
        for _, _, fname in MODELS:
            f.write(f"  📁 {fname}/\n")
            f.write("     ├── [Announcement] ENG_US_M_DaveL.wav\n")
            f.write("     ├── [Audiobook] ENG_US_M_BrianR.wav\n")
            f.write("     ├── [Audiobook] male_audiobook.wav\n")
            f.write("     ├── [Motivational] heath_ledger.wav\n")
            f.write("     ├── [Narration] deep_male_narrator.wav\n")
            f.write("     ├── [Podcast] johnb.wav\n")
            f.write("     ├── [Presentation] ENG_US_M_DCG.wav\n")
            f.write("     ├── [Social Media] FDownload.app.wav\n")
            f.write("     └── [Storytelling] dl-090b86a8217d.wav\n\n")

    print("\n" + sep)
    print("  NEW MODEL SAMPLES GENERATION COMPLETE")
    print(sep)
    print(f"  Target Folder : {NEW_OUTPUT_DIR}")
    print(f"  Total Models  : {len(MODELS)}")
    print(f"  Total Samples : {total_tasks}")
    print(sep)

if __name__ == "__main__":
    main()
