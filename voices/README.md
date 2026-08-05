# 🎤 Zero-Shot Voice Cloning & Genre Folder Structure Guide

This directory contains the reference audio profiles used by the local speech synthesis engine (F5-TTS, Chatterbox, Kokoro) for dynamic zero-shot voice cloning.

---

## 📁 Directory Structure

Place your voice samples (`.wav` or `.m4a` files) either at the root level or categorized inside the corresponding genre folders below. The dashboard will automatically detect them, convert them if necessary, and display them in the dropdown selector under the naming format `[Genre] Voice Name`.

* 📂 **`voices/`** (Root level — e.g. for `my_voice.wav` primary reference)
  * 📁 **`Narration/`** — Standard narrative and descriptive reads.
  * 📁 **`Conversation/`** — Natural dialogue and interactive agent voices.
  * 📁 **`News/`** — formal, clear, newscaster-style delivery.
  * 📁 **`Education/`** — Explanations, teaching, and tutorial voices.
  * 📁 **`Audiobook/`** — Long-form descriptive narrative and voice-acting characters.
  * 📁 **`Podcast/`** — Relaxed, conversational, and direct-to-microphone talk.
  * 📁 **`Advertisement/`** — High impact, persuasive marketing and promo reads.
  * 📁 **`Storytelling/`** — Expressive, emotional narrative for audio dramas.
  * 📁 **`Presentation/`** — Professional business and keynote-style voices.
  * 📁 **`Documentary/`** — Informative, low-pitch storytelling reads.
  * 📁 **`Announcement/`** — Loud, clear, public address or notification tones.
  * 📁 **`Customer Support/`** — Warm, helpful, and friendly support agent voices.
  * 📁 **`Meditation/`** — Soft, slow, calming, whisper-like voices.
  * 📁 **`Motivational/`** — High energy, passionate, and inspiring delivery.
  * 📁 **`Poetry/`** — Rhythmic, cadence-focused artistic expressions.
  * 📁 **`Gaming/`** — Dynamic character lines and enthusiastic streaming commentary.
  * 📁 **`Social Media/`** — Fast-paced, punchy delivery optimized for YouTube Shorts, Reels, and TikToks.
  * 📁 **`Accessibility/`** — Clear, steady, easily understandable audio description voices.

---

## 🛠️ Reference Audio Specifications

To achieve high-quality voice cloning results, ensure your sample files follow these guidelines:

| Parameter | Recommended Specification | Acceptable Range |
| :--- | :--- | :--- |
| **File Format** | Uncompressed `.wav` (PCM 16-bit) | `.m4a` (auto-converted on-the-fly) |
| **Sample Rate** | **24,000 Hz** or **44,100 Hz** | 16,000 Hz minimum |
| **Channels** | **Mono** (1 channel) | Stereo (will be automatically mixed down) |
| **Duration** | **5 to 10 seconds** | 3 to 15 seconds max |
| **Background Noise**| Zero background noise (`< -50 dB`) | Clean indoor home recording |

---

## ⚡ Setup Workflow

1. Drop your reference files into any of the folders above.
2. Open the Streamlit dashboard (**http://localhost:8502**).
3. Select your model (e.g. F5-TTS) and pick your voice from the **🎤 Select Reference Voice to Clone** dropdown!