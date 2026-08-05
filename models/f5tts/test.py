"""
F5-TTS Standalone Inference & Benchmarking Script
"""

import os
import sys
import argparse
import torch

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(os.path.join(WORKSPACE_ROOT, "scripts"))
from speech_synth_helper import synthesize_human_speech

SUPPORTS_VOICE_CLONING = True

def generate_f5tts_speech(text: str, reference_voice: str = None, output_path: str = None) -> dict:
    if output_path is None:
        output_path = os.path.join(WORKSPACE_ROOT, "outputs", "f5tts", "f5tts_sample.wav")
    if reference_voice is None:
        reference_voice = os.path.join(WORKSPACE_ROOT, "voices", "my_voice.wav")
        
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[*] Running F5-TTS inference on device: {device}")
    return synthesize_human_speech(text, "f5tts", reference_voice, output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="F5-TTS Test Runner")
    parser.add_argument("--text", type=str, default="F5-TTS utilizes non-autoregressive flow matching for fast speech generation.")
    parser.add_argument("--ref", type=str, default="../../voices/my_voice.wav")
    parser.add_argument("--output", type=str, default="../../outputs/f5tts/f5tts_sample.wav")
    args = parser.parse_args()
    
    generate_f5tts_speech(args.text, args.ref, args.output)
