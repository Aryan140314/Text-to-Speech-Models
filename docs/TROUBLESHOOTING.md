# 🔧 Troubleshooting Guide

Solutions for common runtime setup and execution issues.

---

## ❓ Frequently Encountered Errors & Solutions

### 1. `StreamlitAPIException: The default value ... is not part of the options`
- **Cause**: Streamlit selectbox/multiselect default list contained a deprecated model name (`Kokoro-82M` or `Audio8-TTS-Preview`).
- **Fix**: Updated default list in `dashboard.py` to active models: `default=["F5-TTS", "Chatterbox Turbo", "Fish Speech S2"]`.

### 2. `FFmpeg not found on PATH`
- **Cause**: System missing global FFmpeg executable for `.m4a` audio conversion.
- **Fix**: The codebase automatically uses `imageio_ffmpeg` executable dynamically.

### 3. `CUDA Out of Memory (OOM)`
- **Cause**: Large text prompt exceeding model context length.
- **Fix**: `IntelligentChunker` in `scripts/tts_adapters.py` automatically splits text into model-safe ~60-word chunks.

### 4. `HuggingFace Hub Network Connection Timeout`
- **Cause**: Flaky internet connection while checking HF models.
- **Fix**: The codebase automatically handles offline cache loading.
