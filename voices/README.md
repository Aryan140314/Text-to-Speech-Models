# Zero-Shot Voice Cloning Guide & Recording Best Practices

To achieve optimal voice cloning fidelity with local TTS models (Kokoro, CosyVoice, Fish Speech, OmniVoice, Chatterbox Turbo, IndexTTS2), high-quality reference audio is essential.

---

## 1. Recommended Audio Specifications

| Parameter | Recommended Value | Alternative / Acceptable |
| :--- | :--- | :--- |
| **File Format** | Uncompressed `.wav` (PCM 16-bit) | `.flac` (avoid lossy MP3) |
| **Sample Rate** | **24,000 Hz (24 kHz)** or **44,100 Hz (44.1 kHz)** | 16,000 Hz (16 kHz minimum) |
| **Channels** | **Mono** (1 channel) | Stereo (will be auto-downmixed) |
| **Sample Duration** | **3 to 10 seconds** per reference file | Up to 15 seconds max |
| **Noise Floor** | `< -50 dB` (Silent background) | Clean indoor room |

---

## 2. Best Recording Practices

1. **Quiet Environment**:
   - Record in a carpeted, furnished room to minimize room reverberation (echo).
   - Turn off air conditioners, fans, computer fans, and computer monitors with high coil whine.

2. **Microphone Setup & Distance**:
   - Use a dedicated condenser or dynamic microphone (avoid laptop/webcam built-in microphones).
   - Position the mic **4 to 6 inches (10-15 cm)** from your mouth at a 45-degree angle to avoid plosive pops ("p", "b", "t").
   - Use a pop filter or foam windscreen.

3. **Vocal Pacing & Expression**:
   - Speak in your natural conversational tone with balanced cadence.
   - Avoid extreme whisper or shouting unless specifically cloning dramatic voices.
   - Ensure the reference prompt contains diverse phonemes (vowels and consonants).

4. **Trimming & Editing**:
   - Trim dead silence at the beginning and end (keep ~200ms padding).
   - Do NOT apply heavy background noise removal filters that artifact the human voice.
   - Normalize audio peak amplitude to **-3 dB to -1 dB**.

---

## 3. Reference Files Directory

- `voices/my_voice.wav`: Primary voice clone sample.
- `voices/reference.wav`: Baseline comparison speaker sample for benchmark similarity metric.
