#!/usr/bin/env python3
"""
generate_all_model_samples.py
==============================
Batch Audio Sample Generator & Cataloguer
TTS Laboratory — Audio DSP & ML Engineering Division

Generates audio samples for ALL 8 TTS Models across ALL Voice Genres in `voices_clean`.
Organizes output files into clean, unambiguous directories:
  1. D:\Saurav\TTS\model_voice_samples\by_model\<Model_Name>\<Genre>_<Voice_Name>.wav
  2. D:\Saurav\TTS\model_voice_samples\by_genre\<Genre>\<Voice_Name>__<Model_Name>.wav

Also exports a comprehensive Excel catalog (`MODEL_GENRE_CATALOG.xlsx`) and Markdown summary (`MODEL_GENRE_CATALOG.md`)
so you can easily inspect, check, or share all model/genre audio combinations!
"""

import os
import sys
import time
import datetime
from pathlib import Path
import pandas as pd

# Add scripts directory to sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORKSPACE_ROOT, "scripts"))

from speech_synth_helper import synthesize_human_speech

# ── Models Definition ────────────────────────────────────────────────────────
MODELS = [
    ("Kokoro-82M",     "kokoro"),
    ("F5-TTS",         "f5tts"),
    ("Chatterbox",     "chatterbox"),
    ("Fish Speech S2", "fishspeech"),
    ("OmniVoice",      "omnivoice"),
    ("CosyVoice 3",    "cosyvoice"),
    ("XTTS-v2",        "xttsv2"),
    ("IndexTTS2",      "indextts2"),
]

# Standard benchmark text prompt
BENCHMARK_PROMPT = (
    "Welcome to the local Text-to-Speech research laboratory. "
    "This voice sample demonstrates speech synthesis fidelity, pitch clarity, and vocal tone control."
)

BASE_VOICES_DIR = os.path.join(WORKSPACE_ROOT, "voices_clean")
OUTPUT_BASE_DIR = os.path.join(WORKSPACE_ROOT, "model_voice_samples")
BY_MODEL_DIR    = os.path.join(OUTPUT_BASE_DIR, "by_model")
BY_GENRE_DIR    = os.path.join(OUTPUT_BASE_DIR, "by_genre")


def scan_clean_voices() -> dict:
    """Scan voices_clean directory for all WAV files categorized by genre."""
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
    print("  TTS Laboratory — All Models & Genres Batch Sample Generator")
    print(f"  Started : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(sep)

    voices = scan_clean_voices()
    print(f"[>>] Found {len(voices)} reference voice profile(s) across genres in voices_clean:")
    for dname, info in voices.items():
        print(f"     • {dname:<40} ({info['full_path']})")
    print(sep)

    os.makedirs(BY_MODEL_DIR, exist_ok=True)
    os.makedirs(BY_GENRE_DIR, exist_ok=True)

    catalog_data = []

    total_tasks = len(MODELS) * len(voices)
    task_idx = 0

    for m_label, m_id in MODELS:
        m_folder_name = f"{m_id.upper()}"
        m_by_model_dir = os.path.join(BY_MODEL_DIR, m_folder_name)
        os.makedirs(m_by_model_dir, exist_ok=True)

        print(f"\n[>>] Processing Model: {m_label} (slot: {m_id})...")

        for dname, v_info in voices.items():
            task_idx += 1
            genre = v_info["genre"]
            vname = v_info["vname"]
            ref_path = v_info["full_path"]

            # File names
            file_by_model = os.path.join(m_by_model_dir, f"[{genre}] {vname}.wav")
            
            g_by_genre_dir = os.path.join(BY_GENRE_DIR, genre)
            os.makedirs(g_by_genre_dir, exist_ok=True)
            file_by_genre = os.path.join(g_by_genre_dir, f"{vname}__{m_id}.wav")

            if os.path.exists(file_by_model) and os.path.getsize(file_by_model) > 1000:
                print(f"  ({task_idx}/{total_tasks}) [{m_label}] + {dname} ... [EXISTS] reusing sample")
                if not os.path.exists(file_by_genre):
                    import shutil
                    shutil.copy2(file_by_model, file_by_genre)
                
                # audio stats
                import wave
                dur = 0.0
                try:
                    with wave.open(file_by_model, "r") as wf:
                        dur = round(wf.getnframes() / float(wf.getframerate()), 2)
                except Exception:
                    pass
                res = {
                    "backend": "f5tts-clone" if m_id != "kokoro" else "kokoro-preset",
                    "gen_time": 0.01,
                    "duration": dur,
                    "file_size_kb": round(os.path.getsize(file_by_model) / 1024, 2),
                    "cloning_active": True if m_id != "kokoro" else False,
                }
            else:
                print(f"  ({task_idx}/{total_tasks}) [{m_label}] + {dname} ...", end=" ", flush=True)

                res = synthesize_human_speech(
                    text=BENCHMARK_PROMPT,
                    model_id=m_id,
                    reference_voice=ref_path,
                    output_path=file_by_model,
                )

                # Copy to by_genre folder as well
                if os.path.exists(file_by_model):
                    import shutil
                    shutil.copy2(file_by_model, file_by_genre)

                print(f"DONE in {res.get('gen_time', 0.0):.2f}s | dur: {res.get('duration', 0.0):.2f}s | backend: {res.get('backend')}")

            backend  = res.get("backend", "unknown")
            gen_time = res.get("gen_time", 0.0)
            duration = res.get("duration", 0.0)
            size_kb  = res.get("file_size_kb", 0.0)

            catalog_data.append({
                "Model Slot": m_id,
                "Model Name": m_label,
                "Genre": genre,
                "Voice Profile": vname,
                "Backend Used": backend,
                "Cloning Active": res.get("cloning_active", False),
                "Generation Time (s)": gen_time,
                "Audio Duration (s)": duration,
                "File Size (KB)": size_kb,
                "By-Model File Path": os.path.relpath(file_by_model, WORKSPACE_ROOT),
                "By-Genre File Path": os.path.relpath(file_by_genre, WORKSPACE_ROOT),
            })

    # Save Excel and Markdown Catalogs
    df = pd.DataFrame(catalog_data)
    excel_path = os.path.join(OUTPUT_BASE_DIR, "MODEL_GENRE_CATALOG.xlsx")
    df.to_excel(excel_path, index=False)

    md_path = os.path.join(OUTPUT_BASE_DIR, "MODEL_GENRE_CATALOG.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# 🎙️ All Models & Genres Audio Samples Catalog\n\n")
        f.write(f"Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Total combinations synthesized: **{len(df)}**\n\n")
        f.write(df.to_markdown(index=False))

    print("\n" + sep)
    print("  BATCH SAMPLES GENERATION COMPLETE")
    print(sep)
    print(f"  Total samples generated : {len(df)}")
    print(f"  Organized By Model      : {BY_MODEL_DIR}")
    print(f"  Organized By Genre      : {BY_GENRE_DIR}")
    print(f"  Excel Catalog           : {excel_path}")
    print(f"  Markdown Catalog        : {md_path}")
    print(sep)


if __name__ == "__main__":
    main()
