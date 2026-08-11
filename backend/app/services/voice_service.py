"""
Voice Library & DSP Dataset Cleaner Service
Indexes reference voice audio files and interfaces with clean_voice_dataset.py.
"""

import os
import wave
from backend.app.core.paths import paths

class VoiceService:
    def get_all_voices(self) -> list:
        voices = []
        voices_dir = paths.voices_dir

        if not os.path.exists(voices_dir):
            return voices

        for root, dirs, files in os.walk(voices_dir):
            for f in files:
                if f.lower().endswith((".wav", ".m4a")) and not f.lower().startswith("."):
                    full_path = os.path.join(root, f)
                    rel_dir = os.path.relpath(root, voices_dir)
                    clean_name = os.path.splitext(f)[0].replace("_", " ").title()
                    genre = "General" if rel_dir == "." else rel_dir

                    duration = 0.0
                    sr = 22050
                    file_size_kb = round(os.path.getsize(full_path) / 1024, 2)

                    if f.lower().endswith(".wav"):
                        try:
                            with wave.open(full_path, "r") as wf:
                                duration = round(wf.getnframes() / float(wf.getframerate()), 2)
                                sr = wf.getframerate()
                        except Exception:
                            duration = 0.0

                    voice_id = f"{genre.lower()}_{clean_name.lower().replace(' ', '_')}"
                    voices.append({
                        "id": voice_id,
                        "name": clean_name,
                        "genre": genre,
                        "file_path": full_path,
                        "duration_sec": duration,
                        "sample_rate": sr,
                        "file_size_kb": file_size_kb,
                    })

        return sorted(voices, key=lambda x: x["name"])

    def clean_voice(self, voice_path: str, strength: float = 0.75) -> str:
        # Calls the DSP dataset cleaner
        cleaned_dir = os.path.join(paths.base_dir, "voices_clean")
        os.makedirs(cleaned_dir, exist_ok=True)
        filename = os.path.basename(voice_path)
        out_path = os.path.join(cleaned_dir, filename)

        try:
            from backend.tts.cleaning.clean_voice_dataset import process_single_file, Config
            cfg = Config(noise_reduction_strength=strength)
            process_single_file(voice_path, out_path, cfg)
            return out_path
        except Exception as e:
            print(f"[!] Voice cleaning error: {e}")
            return voice_path

voice_service = VoiceService()
