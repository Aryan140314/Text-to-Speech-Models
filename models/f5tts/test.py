"""
F5-TTS — Benchmarking runner delegate.
Wraps the unified speech_synth_helper pipeline for benchmark_engine compatibility.
"""
import os
import sys

_workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_scripts_path = os.path.join(_workspace_root, "scripts")
if _scripts_path not in sys.path:
    sys.path.insert(0, _scripts_path)

from speech_synth_helper import synthesize_human_speech


def generate_f5tts_speech(text: str, ref_audio_path: str, output_path: str) -> dict:
    """
    Generate speech using F5-TTS flow-matching zero-shot cloner via the unified synthesis pipeline.
    Requires ref_audio_path for cloning; falls back to Kokoro preset when not provided.

    Returns:
        dict with keys: model, backend, cloning_active, gen_time, duration, file_size_kb, output_path
    """
    ref = ref_audio_path if ref_audio_path and os.path.exists(ref_audio_path) else None
    return synthesize_human_speech(
        text=text,
        model_id="f5tts",
        reference_voice=ref,
        output_path=output_path,
    )
