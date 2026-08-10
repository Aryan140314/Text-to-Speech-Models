# 🎙️ TTS-Research: Local ElevenLabs Alternative & Benchmarking Laboratory

A dedicated local Text-to-Speech (TTS) research studio and benchmarking laboratory evaluating **7 leading open-source zero-shot TTS models** on Windows 11 (NVIDIA RTX 3060 CUDA GPU).

---

## 🚀 7 Supported Zero-Shot TTS Engines

| Model | Engine ID | Architecture | Zero-Shot Voice Cloning | Safe Chunk Size | Primary Use Case |
| :--- | :--- | :--- | :---: | :---: | :--- |
| ⚡ **F5-TTS** | `f5tts` | Non-Autoregressive Flow Matching DiT | ✅ Yes | ~60 Words | Primary Fast Flow Matching Engine |
| 🚀 **Chatterbox Turbo** | `chatterbox` | Zero-Shot Diffusion | ✅ Yes | ~60 Words | Conversational Low-Latency Audio |
| 🐟 **Fish Speech S2** | `fishspeech` | VQ-GAN + LLM Codec (44.1kHz) | ✅ Yes | ~60 Words | High Resolution Voice Synthesis |
| 🎙️ **OmniVoice** | `omnivoice` | Expressive Audio LM | ✅ Yes | ~60 Words | Multi-Speaker Expressive Speech |
| 🔊 **CosyVoice 3** | `cosyvoice` | FunAudioLLM Engine | ✅ Yes | ~80 Words | Audiobook & Long-Form Stability |
| 🌐 **XTTS-v2** | `xttsv2` | Coqui Multilingual Engine | ✅ Yes | ~60 Words | Multilingual Zero-Shot Voice Cloning |
| 🔍 **IndexTTS2** | `indextts2` | Acoustic Retrieval Engine | ✅ Yes | ~60 Words | Speaker Similarity & Timbre Fidelity |

---

## ⚡ Unified Interactive Launcher

No manual environment switching is required. Simply run:
```cmd
python launcher.py
```

Selecting any model (1 to 7) automatically:
- Loads the model adapter framework
- Detects reference voice `voices/my_voice.wav`
- Auto-activates zero-shot voice cloning
- Prompts for text input
- Generates speech audio and saves to `outputs/`

---

## 🖥️ Local ElevenLabs Streamlit Studio

Launch the interactive web application:
```cmd
python -m streamlit run dashboard.py
```
- **2,000-Word Application Ceiling**: Input up to 2,000 words per generation request (`MAX_WORDS = 2000`).
- **Live Counter & Validation**: Displays `Words: X / 2,000 | Characters: Y`. Submit button automatically disables if word limit is exceeded.
- **Intelligent Sentence-Aware Chunking**: `IntelligentChunker` in `scripts/tts_adapters.py` splits long text into model-safe ~60-word chunks (`Paragraph` $\to$ `Sentence` $\to$ `Clause` $\to$ `Word`).
- **Speaker Conditioning Caching**: `SpeakerConditioningCache` caches Whisper transcripts and speaker embeddings to avoid re-extraction overhead.
- **Live Performance & GPU Status**: Displays Real-Time Factor ($\text{RTF} = \text{GenTime} / \text{Duration}$) and CUDA GPU VRAM usage.

---

## 🏗️ Project Architecture & Model Adapters (`scripts/tts_adapters.py`)

The application uses an object-oriented adapter architecture:
- `TTSModelAdapter` (Abstract Base Class): Standardizes `load_model()`, `prepare_text()`, `get_safe_chunk_size()`, `generate()`, and `get_device()`.
- **7 Concrete Adapters**: `F5TTSAdapter`, `ChatterboxAdapter`, `FishSpeechAdapter`, `OmniVoiceAdapter`, `CosyVoiceAdapter`, `XTTSv2Adapter`, `IndexTTS2Adapter`.
- **Master Documentation**: Complete technical reference is documented in [`project_architecture_analysis.md`](file:///D:/S-Project/TTS/project_architecture_analysis.md).

---

## 🧹 Voice Dataset Cleaning Pipeline (`scripts/clean_voice_dataset.py`)

A production-ready audio DSP utility that scans voice recordings and removes background noise, music, and static while preserving speaker voice identity:

```cmd
# Run with defaults (input: voices, output: voices_clean)
python scripts/clean_voice_dataset.py

# Custom input/output directories
python scripts/clean_voice_dataset.py --input "voices" --output "voices_clean" --strength 0.8
```

### Multi-Tier DSP Processing:
1. **Tier 1 (DeepFilterNet3)**: Deep neural speech enhancement model.
2. **Tier 2 (noisereduce)**: Two-pass non-stationary + stationary statistical noise reduction.
3. **Tier 3 (scipy STFT)**: Spectral subtraction fallback.
4. **Post-Filters**: High-pass filter at 80 Hz, noise gate at -48 dBFS, peak normalization to -1.0 dBFS.

---

## 📂 Project Directory Structure

```text
TTS/
├── dashboard.py                 # Streamlit Studio Web Application
├── launcher.py                  # Interactive CLI Launcher Menu
├── project_architecture_analysis.md # Master 52-Section Technical Architecture Report
├── workspace_history.xlsx       # Chronological Development History Log
├── TTS_Voice_Showcase.html      # Portable HTML Voice Showcase Page
├── configs/                     # System & Model Configurations
│   ├── models_config.json       # Model Metadata Registry (7 Active Models)
│   ├── benchmark_config.yaml    # Benchmark Test Configurations
│   └── pronunciation_map.json   # Acronym Phonetic Override Dictionary
├── docs/                        # Project Technical Guides & Documentation
├── models/                      # Individual Model Wrapper Test Scripts
├── outputs/                     # Generated Audio Outputs by Model Slot
├── scripts/                     # Backend Processing Engine
│   ├── tts_adapters.py          # Model Adapter Framework & Intelligent Chunker
│   ├── speech_synth_helper.py   # Speech Synthesis Engine & Fallback Chain
│   ├── clean_voice_dataset.py   # Multi-Tier DSP Audio Dataset Cleaner
│   ├── benchmark_engine.py      # VRAM, RAM, Duration, RTF Profiler
│   └── check_env.py             # CUDA & Dependency Diagnostic Utility
└── voices/                      # Categorized Reference Voice Recordings (17 Genres)
```
