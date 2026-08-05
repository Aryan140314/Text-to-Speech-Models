"""
Kokoro-82M Standalone Inference & Benchmarking Script
"""

import os
import sys
import argparse
import torch

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(os.path.join(WORKSPACE_ROOT, "scripts"))
from speech_synth_helper import synthesize_human_speech

def generate_kokoro_speech(text: str, reference_voice: str, output_path: str) -> dict:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[*] Running Kokoro-82M inference on device: {device}")
    return synthesize_human_speech(text, "kokoro", reference_voice, output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kokoro-82M TTS Test Runner")
    parser.add_argument("--text", type=str, default="Kokoro-82M provides ultra-fast lightweight speech synthesis with low VRAM footprint.")
    parser.add_argument("--ref", type=str, default="../../voices/reference.wav")
    parser.add_argument("--output", type=str, default="../../outputs/kokoro/kokoro_sample.wav")
    args = parser.parse_args()
    
    generate_kokoro_speech(args.text, args.ref, args.output)
