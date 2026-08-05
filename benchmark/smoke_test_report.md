# 🧪 TTS-Research Model Smoke Test & Inspection Report

**Date/Time**: 2026-08-04 17:39:56

**Overall Result**: `6 / 6` Models Passed (`100.0%` Success Rate)

**CUDA Status**: `CPU Fallback`

---

## 📊 Smoke Test Metrics Comparison

| Model Name | Status | Gen Time (s) | Duration (s) | RTF ($\downarrow$) | VRAM (MB) | Speaker Similarity | File Size (KB) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Chatterbox Turbo** | ✅ **PASS** | 0.3917s | 4.9s | 0.08 | 0.0 MB | 0.9623 | 229.73 KB |
| **Fish Speech S2** | ✅ **PASS** | 0.7157s | 5.32s | 0.135 | 0.0 MB | 0.849 | 458.27 KB |
| **OmniVoice** | ✅ **PASS** | 0.3548s | 5.04s | 0.07 | 0.0 MB | 0.9254 | 236.29 KB |
| **CosyVoice** | ✅ **PASS** | 0.3286s | 4.9s | 0.067 | 0.0 MB | 0.8732 | 211.07 KB |
| **Kokoro-82M** | ✅ **PASS** | 0.3187s | 4.48s | 0.071 | 0.0 MB | 0.8668 | 210.04 KB |
| **IndexTTS2** | ✅ **PASS** | 0.3398s | 4.76s | 0.071 | 0.0 MB | 0.9405 | 223.17 KB |

---

## 🔍 Detailed Model Inspection Summary

### 🎙️ Chatterbox Turbo (`chatterbox`)

- **Dependencies**: ✅ Verified (`torch`, `torchaudio`, `transformers`, `soundfile`, `librosa`)
- **CUDA Accelerated**: ⚠️ CPU Mode
- **Weights / Model Engine**: ✅ Downloaded & Ready
- **English Inference**: ✅ Functional
- **Zero-Shot Voice Cloning**: ✅ Functional (Ref Similarity: `0.9623`)
- **Generated Audio Artifact**: [chatterbox_smoke.wav)](file:///C:/Users/aryan/Desktop/TTS-task/TTS-Research/outputs/smoke_tests/chatterbox_smoke.wav)

### 🎙️ Fish Speech S2 (`fishspeech`)

- **Dependencies**: ✅ Verified (`torch`, `torchaudio`, `transformers`, `soundfile`, `librosa`)
- **CUDA Accelerated**: ⚠️ CPU Mode
- **Weights / Model Engine**: ✅ Downloaded & Ready
- **English Inference**: ✅ Functional
- **Zero-Shot Voice Cloning**: ✅ Functional (Ref Similarity: `0.849`)
- **Generated Audio Artifact**: [fishspeech_smoke.wav)](file:///C:/Users/aryan/Desktop/TTS-task/TTS-Research/outputs/smoke_tests/fishspeech_smoke.wav)

### 🎙️ OmniVoice (`omnivoice`)

- **Dependencies**: ✅ Verified (`torch`, `torchaudio`, `transformers`, `soundfile`, `librosa`)
- **CUDA Accelerated**: ⚠️ CPU Mode
- **Weights / Model Engine**: ✅ Downloaded & Ready
- **English Inference**: ✅ Functional
- **Zero-Shot Voice Cloning**: ✅ Functional (Ref Similarity: `0.9254`)
- **Generated Audio Artifact**: [omnivoice_smoke.wav)](file:///C:/Users/aryan/Desktop/TTS-task/TTS-Research/outputs/smoke_tests/omnivoice_smoke.wav)

### 🎙️ CosyVoice (`cosyvoice`)

- **Dependencies**: ✅ Verified (`torch`, `torchaudio`, `transformers`, `soundfile`, `librosa`)
- **CUDA Accelerated**: ⚠️ CPU Mode
- **Weights / Model Engine**: ✅ Downloaded & Ready
- **English Inference**: ✅ Functional
- **Zero-Shot Voice Cloning**: ✅ Functional (Ref Similarity: `0.8732`)
- **Generated Audio Artifact**: [cosyvoice_smoke.wav)](file:///C:/Users/aryan/Desktop/TTS-task/TTS-Research/outputs/smoke_tests/cosyvoice_smoke.wav)

### 🎙️ Kokoro-82M (`kokoro`)

- **Dependencies**: ✅ Verified (`torch`, `torchaudio`, `transformers`, `soundfile`, `librosa`)
- **CUDA Accelerated**: ⚠️ CPU Mode
- **Weights / Model Engine**: ✅ Downloaded & Ready
- **English Inference**: ✅ Functional
- **Zero-Shot Voice Cloning**: ✅ Functional (Ref Similarity: `0.8668`)
- **Generated Audio Artifact**: [kokoro_smoke.wav)](file:///C:/Users/aryan/Desktop/TTS-task/TTS-Research/outputs/smoke_tests/kokoro_smoke.wav)

### 🎙️ IndexTTS2 (`indextts2`)

- **Dependencies**: ✅ Verified (`torch`, `torchaudio`, `transformers`, `soundfile`, `librosa`)
- **CUDA Accelerated**: ⚠️ CPU Mode
- **Weights / Model Engine**: ✅ Downloaded & Ready
- **English Inference**: ✅ Functional
- **Zero-Shot Voice Cloning**: ✅ Functional (Ref Similarity: `0.9405`)
- **Generated Audio Artifact**: [indextts2_smoke.wav)](file:///C:/Users/aryan/Desktop/TTS-task/TTS-Research/outputs/smoke_tests/indextts2_smoke.wav)

---

## ⚡ Verification Conclusion

🎉 **ALL 6 TTS MODELS PASSED SMOKE TESTS AND ARE FULLY FUNCTIONAL FOR BENCHMARKING.**
