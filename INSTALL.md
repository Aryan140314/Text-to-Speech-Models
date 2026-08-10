# 🛠️ Installation & Environment Setup Guide

Follow these steps to set up and run the local **Text-to-Speech (TTS) Laboratory** on Windows with NVIDIA CUDA GPU acceleration.

---

## 📋 System Requirements

- **Operating System**: Windows 10/11 (64-bit)
- **Python**: Python 3.10.11
- **GPU Hardware**: NVIDIA GPU with minimum 6GB VRAM (NVIDIA GeForce RTX 3060 12GB recommended)
- **CUDA Toolkit**: CUDA 12.1 / cuDNN
- **System Binaries**: FFmpeg (auto-provided by `imageio_ffmpeg`)

---

## 🚀 Quickstart Installation

### 1. Clone Repository & Navigate to Workspace
```cmd
git clone https://github.com/Aryan140314/Text-to-Speech-Models.git
cd Text-to-Speech-Models
```

### 2. Create Virtual Environment
```cmd
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install PyTorch with CUDA Support
```cmd
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 4. Install Dependencies
```cmd
pip install -r requirements.txt
```

---

## 🏃 Running the Application

### Launch Streamlit Studio (Recommended)
```cmd
python -m streamlit run dashboard.py
```
*Opens interactive Web Studio at `http://localhost:8501`.*

### Launch CLI Interactive Menu
```cmd
python launcher.py
```

### Verify Environment & CUDA Setup
```cmd
python scripts/check_env.py
```

---

## 📊 Supported Models (7 Zero-Shot Engines)
1. ⚡ **F5-TTS** (`f5tts`)
2. 🚀 **Chatterbox Turbo** (`chatterbox`)
3. 🐟 **Fish Speech S2** (`fishspeech`)
4. 🎙️ **OmniVoice** (`omnivoice`)
5. 🔊 **CosyVoice 3** (`cosyvoice`)
6. 🌐 **XTTS-v2** (`xttsv2`)
7. 🔍 **IndexTTS2** (`indextts2`)
