# Installation Guide for TTS-Research Workspace

This document provides complete instructions for installing and configuring the local Text-to-Speech (TTS) research workspace on Windows 11 with Python 3.11 and CUDA acceleration.

---

## System Requirements

- **Operating System**: Windows 11 (64-bit)
- **Python**: Version 3.11.x
- **GPU**: NVIDIA RTX 3060 Laptop GPU (6GB VRAM) or equivalent CUDA GPU
- **CUDA Toolkit**: Version 12.1 or 11.8 installed
- **Git**: Installed and available in system PATH
- **FFmpeg**: Required for audio transcoding and feature analysis

---

## 1. Quick Workspace Setup

1. Open PowerShell or Command Prompt in the repository directory:
   ```cmd
   cd TTS-Research
   ```

2. Check your hardware and environment diagnostic status:
   ```cmd
   python scripts/check_env.py
   ```

3. Install master Python dependencies:
   ```cmd
   pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
   pip install -r requirements.txt
   ```

---

## 2. Model Environment Installation

Each model in `models/` contains an isolated `install.bat` and `requirements.txt`. You can install them individually:

- **Chatterbox Turbo**: `cd models/chatterbox && install.bat`
- **Fish Speech S2**: `cd models/fishspeech && install.bat`
- **OmniVoice**: `cd models/omnivoice && install.bat`
- **CosyVoice**: `cd models/cosyvoice && install.bat`
- **Kokoro-82M**: `cd models/kokoro && install.bat`
- **IndexTTS2**: `cd models/indextts2 && install.bat`

---

## 3. Automated Model Weights Downloader (Bonus)

To fetch model checkpoints directly from Hugging Face:
```cmd
python download_models.py
```
This automatically downloads weights into `models/<model_name>/weights/`.

---

## 4. Verification

Run the environment verification diagnostic:
```cmd
python scripts/check_env.py
```
If all checks pass with green `[+]` indicators, your installation is complete!
