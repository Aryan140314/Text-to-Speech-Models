"""
Kokoro-82M — Benchmarking runner delegate.
Wraps the unified speech_synth_helper pipeline for benchmark_engine compatibility.

NOTE: This module lives in models/kokoro_runner/ (not models/kokoro/) to avoid
naming collision with the installed `kokoro` Python package.
"""
import os
import sys

_workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_scripts_path = os.path.join(_workspace_root, "scripts")
if _scripts_path not in sys.path:
    sys.path.insert(0, _scripts_path)

from speech_synth_helper import synthesize_human_speech


def generate_kokoro_speech(text: str, ref_audio_path: str, output_path: str) -> dict:
    """
    Generate speech using Kokoro-82M lightweight neural TTS via the unified synthesis pipeline.
    Kokoro runs in preset voice mode (no zero-shot cloning); ref_audio_path is ignored.

    Returns:
        dict with keys: model, backend, cloning_active, gen_time, duration, file_size_kb, output_path
    """
    return synthesize_human_speech(
        text=text,
        model_id="kokoro",
        reference_voice=None,  # Kokoro is preset-only, no cloning
        output_path=output_path,
    )
