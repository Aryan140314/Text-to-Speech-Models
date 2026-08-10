# 🛠️ Documentation — Installation & Environment Setup Guide

Detailed setup instructions for the local **TTS Research Laboratory**.

---

## 📋 Requirements
- **OS**: Windows 10/11 (64-bit)
- **Python**: 3.10.11
- **CUDA**: 12.1 (NVIDIA RTX 3060 12GB recommended)

---

## 🚀 Setup Steps

```cmd
# 1. Activate Virtual Environment
.venv\Scripts\activate

# 2. Install PyTorch with CUDA 12.1
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# 3. Install Required Libraries
pip install -r requirements.txt

# 4. Verify CUDA GPU Detection
python scripts/check_env.py
```

---

## 🖥️ Application Launch Commands

- **Streamlit Web Studio**: `python -m streamlit run dashboard.py`
- **CLI Terminal Menu**: `python launcher.py`
- **Multi-Tier Audio Cleaner**: `python scripts/clean_voice_dataset.py`
