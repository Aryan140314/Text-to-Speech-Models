"""
OmniVoice Standalone Inference & Benchmarking Script
"""

import os
import sys
import argparse
import torch

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(os.path.join(WORKSPACE_ROOT, "scripts"))
from speech_synth_helper import synthesize_human_speech

def generate_omnivoice_speech(text: str, reference_voice: str, output_path: str) -> dict:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[*] Running OmniVoice inference on device: {device}")
    return synthesize_human_speech(text, "omnivoice", reference_voice, output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OmniVoice TTS Test Runner")
    parser.add_argument("--text", type=str, default="OmniVoice brings expressive multi-speaker audio generation and zero-shot voice cloning.")
    parser.add_argument("--ref", type=str, default="../../voices/reference.wav")
    parser.add_argument("--output", type=str, default="../../outputs/omnivoice/omnivoice_sample.wav")
    args = parser.parse_args()
    
    generate_omnivoice_speech(args.text, args.ref, args.output)
