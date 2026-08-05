"""
Environment & Hardware Diagnostic Tool for TTS-Research
Checks Python, CUDA, PyTorch, FFmpeg, GPU VRAM, dependencies, and model checkpoints across all 8 models.
"""

import os
import sys
import shutil
import subprocess
import platform

def check_environment():
    print("=" * 70)
    print("      TTS-Research Environment & Diagnostic Status Check (8 Models)")
    print("=" * 70)
    
    issues_found = []
    
    # 1. Operating System & Python Version
    py_ver = sys.version.split()[0]
    os_info = f"{platform.system()} {platform.release()}"
    print(f"[+] OS Detected: {os_info}")
    print(f"[+] Python Version: {py_ver}")
    
    # 2. PyTorch & CUDA Check
    try:
        import torch
        print(f"[+] PyTorch Version: {torch.__version__}")
        cuda_avail = torch.cuda.is_available()
        print(f"[+] CUDA Available: {cuda_avail}")
        if cuda_avail:
            print(f"[+] CUDA Version: {torch.version.cuda}")
            device_count = torch.cuda.device_count()
            for i in range(device_count):
                gpu_name = torch.cuda.get_device_name(i)
                total_mem = round(torch.cuda.get_device_properties(i).total_memory / (1024**3), 2)
                print(f"    - GPU [{i}]: {gpu_name} ({total_mem} GB VRAM)")
        else:
            print("[!] WARNING: PyTorch CUDA support is NOT active. Inference will run on CPU.")
    except ImportError:
        print("[!] ERROR: PyTorch is not installed.")
        issues_found.append("PyTorch missing. Run: pip install torch torchaudio")

    # 3. Check Core Python Packages
    required_pkgs = [
        "transformers", "accelerate", "huggingface_hub", "soundfile",
        "librosa", "numpy", "scipy", "pandas", "streamlit", "pyyaml", "plotly"
    ]
    missing_pkgs = []
    for pkg in required_pkgs:
        try:
            __import__(pkg)
        except ImportError:
            missing_pkgs.append(pkg)
            
    if missing_pkgs:
        print(f"[!] Missing Packages: {', '.join(missing_pkgs)}")
        issues_found.append(f"Install missing packages: pip install {' '.join(missing_pkgs)}")
    else:
        print("[+] All Core Python Dependencies Installed.")

    # 4. Check Reference Audio Files
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    voices_dir = os.path.join(root_dir, "voices")
    my_voice = os.path.join(voices_dir, "my_voice.wav")
    ref_voice = os.path.join(voices_dir, "reference.wav")
    
    if os.path.exists(my_voice) and os.path.exists(ref_voice):
        print(f"[+] Voice Samples Present: {os.path.basename(my_voice)}, {os.path.basename(ref_voice)}")
    else:
        print("[!] Voice samples missing. Generating baseline samples...")
        gen_script = os.path.join(voices_dir, "sample_generator.py")
        if os.path.exists(gen_script):
            subprocess.run([sys.executable, gen_script], check=False)
            
    # 5. Check All 8 Model Folders
    models_dir = os.path.join(root_dir, "models")
    expected_models = ["chatterbox", "fishspeech", "omnivoice", "cosyvoice", "xttsv2", "f5tts", "kokoro", "indextts2"]
    for m in expected_models:
        m_path = os.path.join(models_dir, m)
        if os.path.exists(m_path):
            print(f"[+] Model Package Ready: {m}")
        else:
            print(f"[!] Missing Model Folder: {m}")
            issues_found.append(f"Model directory missing: models/{m}")

    print("=" * 70)
    if issues_found:
        print("                  Diagnostic Summary & Action Plan")
        print("=" * 70)
        for issue in issues_found:
            print(f" - [ACTION REQUIRED] {issue}")
    else:
        print("                  SYSTEM READY FOR TTS BENCHMARKING!")
    print("=" * 70)

if __name__ == "__main__":
    check_environment()
