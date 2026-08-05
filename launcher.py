"""
Unified Interactive Launcher for Local Text-to-Speech Research Laboratory
Provides zero-configuration model execution across 8 open-source TTS models with automatic zero-shot voice cloning detection.
"""

import os
import sys
import time

WORKSPACE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(WORKSPACE_ROOT, "scripts"))
sys.path.append(os.path.join(WORKSPACE_ROOT, "models"))

from chatterbox.test import generate_chatterbox_speech
from fishspeech.test import generate_fishspeech_speech
from omnivoice.test import generate_omnivoice_speech
from cosyvoice.test import generate_cosyvoice_speech
from xttsv2.test import generate_xttsv2_speech
from f5tts.test import generate_f5tts_speech
from indextts2.test import generate_indextts2_speech
from kokoro.test import generate_kokoro_speech

MODEL_REGISTRY = {
    "1": {"id": "chatterbox", "name": "Chatterbox Turbo", "fn": generate_chatterbox_speech, "supports_cloning": True},
    "2": {"id": "fishspeech", "name": "Fish Speech S2", "fn": generate_fishspeech_speech, "supports_cloning": True},
    "3": {"id": "omnivoice", "name": "OmniVoice", "fn": generate_omnivoice_speech, "supports_cloning": True},
    "4": {"id": "cosyvoice", "name": "CosyVoice 3", "fn": generate_cosyvoice_speech, "supports_cloning": True},
    "5": {"id": "xttsv2", "name": "XTTS-v2", "fn": generate_xttsv2_speech, "supports_cloning": True},
    "6": {"id": "f5tts", "name": "F5-TTS", "fn": generate_f5tts_speech, "supports_cloning": True},
    "7": {"id": "indextts2", "name": "IndexTTS2", "fn": generate_indextts2_speech, "supports_cloning": True},
    "8": {"id": "kokoro", "name": "Kokoro-82M", "fn": generate_kokoro_speech, "supports_cloning": True}
}

def show_menu():
    print("\n" + "=" * 70)
    print("      🎙️  TTS-RESEARCH: UNIFIED LOCAL TTS MODEL LAUNCHER")
    print("=" * 70)
    print("Select a model to synthesize speech (Zero-shot voice cloning supported):\n")
    for key, info in MODEL_REGISTRY.items():
        cloning_tag = "[Voice Cloning: Yes]" if info["supports_cloning"] else "[Voice Cloning: No]"
        print(f"  {key}. {info['name']:<22} {cloning_tag}")
    print("  0. Exit Launcher")
    print("=" * 70)

def run_launcher():
    while True:
        show_menu()
        choice = input("Enter choice (1-8 or 0 to exit): ").strip()
        
        if choice == "0":
            print("\nExiting TTS-Research Launcher. Goodbye!")
            sys.exit(0)
            
        if choice not in MODEL_REGISTRY:
            print("\n[!] Invalid selection. Please choose a number between 1 and 8.")
            continue
            
        model_info = MODEL_REGISTRY[choice]
        m_id = model_info["id"]
        m_name = model_info["name"]
        gen_fn = model_info["fn"]
        
        print(f"\n[+] Selected Model: [{m_name}]")
        
        # Check reference voice sample
        my_voice_path = os.path.join(WORKSPACE_ROOT, "voices", "my_voice.wav")
        ref_voice_to_use = None
        
        if os.path.exists(my_voice_path) and model_info["supports_cloning"]:
            ref_voice_to_use = my_voice_path
            print(f"[+] Detected Voice Sample: {my_voice_path} (Auto zero-shot cloning ACTIVE)")
        else:
            print("[+] Using default speaker profile.")
            
        text_input = input("\nEnter English text to synthesize (Press Enter for default prompt):\n> ").strip()
        if not text_input:
            text_input = "Hello! This is a real-time zero-shot voice synthesis test running locally on the TTS-Research laboratory."
            
        out_dir = os.path.join(WORKSPACE_ROOT, "outputs", m_id)
        os.makedirs(out_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        out_file = os.path.join(out_dir, f"{m_id}_generated_{timestamp}.wav")
        
        print(f"\n[*] Synthesizing speech with [{m_name}]...")
        result = gen_fn(text_input, ref_voice_to_use, out_file)
        
        print("\n" + "=" * 70)
        print(f"✅ Speech Generation Successful!")
        print(f"   - Model: {m_name}")
        print(f"   - Output Audio: {out_file}")
        print(f"   - Duration: {result.get('duration', 'N/A')}s")
        print(f"   - Gen Time: {result.get('gen_time', 'N/A')}s")
        print("=" * 70)
        
        input("\nPress Enter to return to main menu...")

if __name__ == "__main__":
    run_launcher()
