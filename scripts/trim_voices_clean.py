#!/usr/bin/env python3
"""
trim_voices_clean.py
====================
Utility to trim all audio files in D:\Saurav\TTS\voices_clean to maximum 15 seconds.
Applies a smooth 50ms fade-out at the 15s boundary to prevent digital clicks.
"""

import os
import sys
from pathlib import Path
import numpy as np
import soundfile as sf
import librosa

TARGET_DIR = r"D:\Saurav\TTS\voices_clean"
MAX_DURATION_S = 15.0
FADE_MS = 50.0  # 50 ms fade-out at cutoff

SUPPORTED_EXTS = (".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac", ".opus")

def trim_audio_file(file_path: Path) -> dict:
    """Trim a single audio file to MAX_DURATION_S seconds."""
    result = {
        "file": str(file_path),
        "orig_dur": 0.0,
        "new_dur": 0.0,
        "trimmed": False,
        "status": "success",
        "error": None
    }
    
    try:
        # Load audio preserving sample rate
        audio, sr = librosa.load(str(file_path), sr=None, mono=True)
        orig_dur = len(audio) / float(sr)
        result["orig_dur"] = round(orig_dur, 2)
        
        max_samples = int(MAX_DURATION_S * sr)
        
        if len(audio) > max_samples:
            # Trim
            trimmed_audio = audio[:max_samples].copy()
            
            # Apply smooth 50ms cosine fade-out at the end
            fade_samples = min(int(FADE_MS / 1000.0 * sr), len(trimmed_audio) // 4)
            if fade_samples > 0:
                t = np.linspace(0.0, 1.0, fade_samples)
                fade_out = (1.0 + np.cos(np.pi * t)) / 2.0
                trimmed_audio[-fade_samples:] *= fade_out.astype(np.float32)
            
            # Save trimmed audio back as WAV
            out_file = file_path.with_suffix(".wav")
            sf.write(str(out_file), trimmed_audio, sr, subtype="PCM_16")
            
            # If original file was not .wav, remove old format file after converting to wav
            if file_path.suffix.lower() != ".wav" and out_file.exists():
                try:
                    os.remove(file_path)
                except Exception:
                    pass
                    
            result["new_dur"] = round(len(trimmed_audio) / float(sr), 2)
            result["trimmed"] = True
        else:
            result["new_dur"] = round(orig_dur, 2)
            result["trimmed"] = False

    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
        
    return result

def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    print("-" * 70)
    print("  TTS Laboratory -- Audio Trimming Utility (Max 15 Seconds)")
    print(f"  Target Directory: {TARGET_DIR}")
    print("-" * 70)
    
    target_path = Path(TARGET_DIR)
    if not target_path.exists():
        print(f"[ERROR] Directory not found: {TARGET_DIR}")
        sys.exit(1)
        
    audio_files = []
    for root, _, files in os.walk(target_path):
        for f in files:
            if Path(f).suffix.lower() in SUPPORTED_EXTS:
                audio_files.append(Path(root) / f)
                
    audio_files.sort()
    print(f"[>>] Found {len(audio_files)} audio file(s) in {TARGET_DIR}")
    print("-" * 70)
    
    trimmed_count = 0
    unchanged_count = 0
    failed_count = 0
    
    for fpath in audio_files:
        res = trim_audio_file(fpath)
        rel_name = fpath.relative_to(target_path)
        
        if res["status"] == "success":
            if res["trimmed"]:
                trimmed_count += 1
                print(f"[TRIMMED]   {str(rel_name):<45} : {res['orig_dur']:>5.2f}s -> {res['new_dur']:>5.2f}s")
            else:
                unchanged_count += 1
                print(f"[UNCHANGED] {str(rel_name):<45} : {res['orig_dur']:>5.2f}s (<= 15s)")
        else:
            failed_count += 1
            print(f"[FAILED]    {str(rel_name):<45} : {res['error']}")
            
    print("-" * 70)
    print("  TRIMMING SUMMARY")
    print("-" * 70)
    print(f"  Total files processed : {len(audio_files)}")
    print(f"  Trimmed to 15.0s     : {trimmed_count}")
    print(f"  Unchanged (<= 15.0s) : {unchanged_count}")
    print(f"  Failed               : {failed_count}")
    print("-" * 70)

if __name__ == "__main__":
    main()
