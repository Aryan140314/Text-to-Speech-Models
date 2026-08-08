# 🎙️ TTS-Research: Local ElevenLabs Alternative & Benchmarking Laboratory

A dedicated local Text-to-Speech (TTS) research and benchmarking laboratory evaluating 8 leading open-source TTS models against ElevenLabs on Windows 11 (NVIDIA RTX 3060 GPU).

---

## 🚀 8 Supported TTS Engines

| Model | Engine ID | Architecture | Voice Cloning Support | Primary Use Case |
| :--- | :--- | :--- | :---: | :--- |
| **Chatterbox Turbo** | `chatterbox` | Zero-Shot Diffusion | ✅ Yes | Conversational Low-Latency Audio |
| **Fish Speech S2** | `fishspeech` | VQ-GAN + LLM Codec | ✅ Yes | 44.1kHz High Resolution YouTube Audio |
| **OmniVoice** | `omnivoice` | Expressive Audio LM | ✅ Yes | Multi-Speaker Expressive Speech |
| **CosyVoice 3** | `cosyvoice` | FunAudioLLM Engine | ✅ Yes | Audiobook & Long-Form Stability |
| **XTTS-v2** | `xttsv2` | Coqui Multilingual Engine | ✅ Yes | Multilingual Zero-Shot Voice Cloning |
| **F5-TTS** | `f5tts` | Non-Autoregressive Flow Matching | ✅ Yes | Ultra-Fast Speed & Flow Matching |
| **IndexTTS2** | `indextts2` | Index Retrieval Acoustic | ✅ Yes | Speaker Similarity & Timbre Fidelity |
| **Kokoro-82M** | `kokoro` | Lightweight TTS (82M) | ✅ Yes | Ultra-Low VRAM AI Assistants |

---

## ⚡ Unified Interactive Launcher

No manual virtual environment switching is required. Simply run:
```cmd
python launcher.py
```
*(Or double-click `launch.bat`)*

Selecting any model (1 to 8) automatically:
- Loads model runner environment
- Detects reference voice `voices/my_voice.wav`
- Auto-checks zero-shot voice cloning capability
- Prompts for English text input
- Generates speech audio and saves to `outputs/`

---

## 🖥️ Local ElevenLabs Streamlit Studio

Launch the interactive web application:
```cmd
streamlit run dashboard.py
```
- Paste English text
- Select any of the 8 TTS models
- Click **Generate Speech Audio** to listen instantly
- View real-time latency, duration, and VRAM benchmarking tables

---

## 📊 Run Automated Master Benchmarks

To benchmark all 8 models + ElevenLabs baseline across Short, Medium, and Long prompts:
```cmd
python run_all_models.py
```
Results are exported to `benchmark/benchmark_results.csv`.

---

## 🧹 Voice Dataset Cleaning Pipeline (`clean_voice_dataset.py`)

A production-ready standalone audio DSP utility that scans all voice samples and removes background noise, music, environmental sounds, static, hum, and hiss while strictly preserving speaker voice identity, timbre, and natural dynamics.

### 🛠️ Required Packages & Installation
```cmd
pip install numpy scipy soundfile librosa noisereduce DeepFilterNet pydub tqdm
```
*(Note: Requires FFmpeg installed on system PATH for `.m4a`, `.mp3`, `.aac`, `.opus` audio decoding).*

### 🚀 How to Run
```cmd
# Run with defaults (input: D:\Saurav\TTS\voices, output: D:\Saurav\TTS\voices_clean)
python clean_voice_dataset.py

# Custom input/output directories
python clean_voice_dataset.py --input "D:\Saurav\TTS\voices" --output "D:\Saurav\TTS\voices_clean"

# Adjust noise reduction aggressiveness (0.0 = off, 1.0 = maximum)
python clean_voice_dataset.py --strength 0.8 --format wav

# Force re-processing of already existing files
python clean_voice_dataset.py --overwrite
```

### ⚙️ Configuration Options
Edit the `Config` dataclass at the top of `clean_voice_dataset.py` or use CLI flags:
- `noise_reduction_strength`: Controls attenuation factor (default `0.75`).
- `music_suppression_strength`: Controls secondary pass music/background audio reduction (default `0.75`).
- `output_format`: `"wav"` (16-bit PCM, default) or `"flac"` (lossless).
- `sample_rate`: Set to integer (e.g., `24000`, `44100`) or `None` to preserve original sample rate.
- `apply_high_pass`: 4th-order Butterworth high-pass filter at `80 Hz` to remove sub-bass rumble/HVAC.
- `apply_noise_gate`: Smooth cosine envelope noise gate at `-48 dBFS` threshold (`5ms` attack, `120ms` release).
- `normalize_output`: Peak normalization to `-1.0 dBFS`.

### 📂 Multi-Tier Processing & Expected Output
The utility auto-detects the best available enhancement backend:
1. **Tier 1 (DeepFilterNet3)**: Deep neural speech enhancement model (~95% quality preservation).
2. **Tier 2 (noisereduce)**: Two-pass non-stationary + stationary statistical noise reduction.
3. **Tier 3 (scipy STFT)**: Spectral subtraction fallback (always available).

**Expected Output Structure:**
- Exact folder hierarchy mirrored from `D:\Saurav\TTS\voices\` to `D:\Saurav\TTS\voices_clean\`.
- Comprehensive log saved to `D:\Saurav\TTS\cleaning_log.txt` (summary stats, processing times, skipped/failed files).

### ⚠️ Limitations & Voice Quality Guarantees
- **Voice Identity First**: Processing prioritizes natural speaker timbre over aggressive artifact creation. If extreme noise removal risks metallic/robotic distortion, subtle background atmosphere is preserved.
- **No Synthesis/Conversion**: Audio is strictly enhanced via DSP/enhancement models; no voice conversion, cloning, or speech resynthesis is performed.

