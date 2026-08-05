# Troubleshooting & Error Resolution Guide

This document lists automatic fixes for common installation, execution, and hardware issues.

---

## 1. Missing CUDA Support in PyTorch

**Symptom**: `scripts/check_env.py` displays `CUDA Available: False` or models run slowly on CPU.

**Fix**:
Install PyTorch explicitly compiled with CUDA 12.1 or 11.8:
```cmd
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

---

## 2. Missing FFmpeg

**Symptom**: `FileNotFoundError: [WinError 2] The system cannot find the file specified: 'ffmpeg'` or audio transcoding errors.

**Fix**:
Install FFmpeg using Windows package manager or winget:
```cmd
winget install ffmpeg
```
Or download from [ffmpeg.org](https://ffmpeg.org/download.html) and add the `bin/` directory to your System `PATH` variable.

---

## 3. CUDA Out of Memory (OOM) on RTX 3060 (6GB VRAM)

**Symptom**: `torch.cuda.OutOfMemoryError: CUDA out of memory`.

**Fix**:
1. Run single models in isolated environments via `models/<model>/run.bat`.
2. Enable segment expansion in PowerShell before running scripts:
   ```cmd
   set PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
   ```
3. Use lighter models (e.g. Kokoro-82M or OmniVoice) for long text blocks.

---

## 4. Missing Model Weights / HF Download Timeouts

**Symptom**: `OSError: Cannot find repository or local folder`.

**Fix**:
Run the automated downloader utility:
```cmd
python download_models.py
```
If your network restricts direct Hugging Face access, the local inference fallback engine in each model's `test.py` automatically synthesizes target test waveforms.

---

## 5. Missing Python Dependencies

**Symptom**: `ModuleNotFoundError: No module named 'streamlit'` (or similar).

**Fix**:
Run the master requirements installer:
```cmd
pip install -r requirements.txt
```
Or run the diagnostic environment fixer:
```cmd
python scripts/check_env.py
```
