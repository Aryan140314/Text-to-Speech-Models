# 🎤 Zero-Shot Voice Cloning Guide

Learn how to perform high-fidelity zero-shot voice cloning locally.

---

## 🎙️ How Zero-Shot Cloning Works

Zero-shot voice cloning uses **5 to 10 seconds of reference audio** from any speaker. The neural model extracts acoustic speaker embeddings and speaks any target text in that exact voice **without training or fine-tuning.**

---

## 📋 Best Practices for Reference Audio

1. **Duration**: 5 to 10 seconds of clear, uninterrupted speech.
2. **Quality**: Recorded in a quiet room without background noise, echo, or music.
3. **Format**: WAV or M4A format (auto-converted to 22,050 Hz Mono WAV).
4. **Placement**: Save your audio recording to `voices/my_voice.wav` or select any profile from the studio dropdown menu.

---

## 🚀 Cloning Across All 7 Models

All 7 models in the laboratory support zero-shot voice cloning:
- **F5-TTS**: Fast flow matching voice cloning.
- **Chatterbox Turbo**: Conversational diffusion cloning.
- **Fish Speech S2**: 44.1kHz studio resolution cloning.
- **OmniVoice**: Expressive multi-speaker audio LM.
- **CosyVoice 3**: FunAudioLLM zero-shot cloning.
- **XTTS-v2**: Multilingual zero-shot cloning.
- **IndexTTS2**: Timbre-fidelity acoustic retrieval.
