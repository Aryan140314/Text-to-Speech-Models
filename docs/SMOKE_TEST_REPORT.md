# 🧪 Smoke Test Verification Report

Diagnostic summary of automated end-to-end testing performed on all **7 zero-shot TTS model adapters**.

---

## 📊 Verification Matrix

| Model | Adapter Class | Status | Device | Audio Output Verified |
|---|---|:---:|---|:---:|
| **F5-TTS** | `F5TTSAdapter` | PASS | CUDA | ✅ Verified |
| **Chatterbox Turbo** | `ChatterboxAdapter` | PASS | CUDA | ✅ Verified |
| **Fish Speech S2** | `FishSpeechAdapter` | PASS | CUDA | ✅ Verified |
| **OmniVoice** | `OmniVoiceAdapter` | PASS | CUDA | ✅ Verified |
| **CosyVoice 3** | `CosyVoiceAdapter` | PASS | CUDA | ✅ Verified |
| **XTTS-v2** | `XTTSv2Adapter` | PASS | CUDA | ✅ Verified |
| **IndexTTS2** | `IndexTTS2Adapter` | PASS | CUDA | ✅ Verified |

---

## 🛡️ Pipeline Guard Tests

1. **MAX_WORDS Limit Test**: 2,000-word ceiling enforced in UI (`dashboard.py`). Submit button disables automatically when exceeded.
2. **Sentence-Aware Chunker Test**: `IntelligentChunker` splits multi-paragraph text into safe ~60-word segments without cutting words mid-boundary.
3. **Conditioning Cache Test**: `SpeakerConditioningCache` avoids re-transcribing Whisper reference audio across multiple chunks.
