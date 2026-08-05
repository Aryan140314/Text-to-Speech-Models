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
