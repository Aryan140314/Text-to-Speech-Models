# 🎙️ Voice-Over Quality, Pronunciation Control & ElevenLabs Strategy Report

This report outlines the strategy for achieving production-grade voice-overs for YouTube, Instagram, and TikTok shorts using local open-source models (Kokoro-82M & F5-TTS) and commercial baselines (ElevenLabs).

---

## 📈 1. Credit-Based Calculation Summary (ElevenLabs)

ElevenLabs billing is based on **character count** (1 character = 1 credit, including spaces and punctuation).

### 🧮 Conversion Metrics:
* **Average Word Length**: 5 characters (including spaces). 
* **1 Word** ≈ 5 credits.
* **10,000 Credits** ≈ 2,000 words.

### 🎥 Clip Generation Estimates:
Average speech rate for engaging social media content (Shorts/Reels/TikTok) is **130 to 150 Words Per Minute (WPM)**.

| Clip Duration | Avg. Word Count | Credit Cost Per Clip | Total Clips (per 10,000 Credits) |
| :--- | :---: | :---: | :---: |
| **15 Seconds** | 35 words | ~175 credits | **57 Clips** |
| **30 Seconds** | 70 words | ~350 credits | **28 Clips** |
| **60 Seconds** | 140 words | ~700 credits | **14 Clips** |

---

## 🎭 2. ElevenLabs & Open-Source Voice Mapping

To match ElevenLabs' expressive standards locally, we map the best commercial voices to open-source preset speakers or zero-shot clones.

### 🏆 Best ElevenLabs Voices for Social Media:
1. **Adam** (Deep, gravelly, motivational): Best for True Crime, Finance, and Gym Motivation.
2. **Antony** (Calm, articulate, smooth): Best for Video Essays and Documentary Shorts.
3. **Rachel** (Enthusiastic, bright, friendly): Best for Lifestyle, Vlogs, and TikTok storytelling.
4. **Marcus** (Resonant, authoritative, deep): Best for Tech, History, and Narrations.

### 🗺️ Local Open-Source Speaker Mapping:

| ElevenLabs Voice | Local Equivalent Model | Preset Name | Zero-Shot Clone Method |
| :--- | :--- | :---: | :--- |
| **Adam** | Kokoro-82M | `am_adam` | Clone via F5-TTS using a 10s clip of Adam |
| **Antony** | Kokoro-82M | `am_michael` | Clone via F5-TTS using a 10s clip of Antony |
| **Rachel** | Kokoro-82M | `af_bella` | Clone via F5-TTS using a 10s clip of Rachel |
| **Marcus** | Kokoro-82M | `bm_george` | Clone via F5-TTS using a 10s clip of Marcus |

---

## 🎙️ 3. Pronunciation, Emphasis & Pause Control in AI Voices

To match or exceed ElevenLabs' natural pacing, you must guide the neural models using specific formatting techniques.

### ⏸️ Controlling Pauses:
* **Short Pause (200ms)**: Insert a comma `,` or a hyphen `-`.
  * *Example*: "First, we initialize the model, then we benchmark it."
* **Medium Pause (500ms)**: Insert a period `.`, semicolon `;`, or colon `:`.
* **Long Pause (800ms - 1s)**: Use an ellipsis `...` or triple hyphens `---`.
  * *Example*: "The results were shocking... Chatterbox won."

### ⚡ Emphasizing Words:
Unlike custom SSML tags which are poorly supported by raw neural backends, you can influence the ALBERT text encoder in **Kokoro-82M** using formatting:
* **Capitalization**: Capitalizing a word increases attention weights.
  * *Example*: "This is a HUGE breakthrough."
* **Quotation Marks**: Adds sub-tonal emphasis and shifts pitch slightly.
  * *Example*: "He called it a 'revolution' in speech tech."

### 🔠 Acronyms, Numbers & Names:
* **Acronyms**: Spell them phonetically or with dashes so the model doesn't read them as words.
  * *Instead of*: "TTS" (might pronounce "tits") 
  * *Use*: "T-T-S" or "Tee-Tee-Ess".
* **Foreign or Complex Names**: Break them down into syllables.
  * *Instead of*: "Aryan"
  * *Use*: "Ah-ree-an".
  * *Instead of*: "ElevenLabs"
  * *Use*: "Eleven Labs" (adding a space prevents weird word concatenation).

---

## 📁 4. Custom Showcase References Setup

You can place your preferred voice profiles inside `voices/` to enable local Zero-Shot Voice Cloning. The dashboard will automatically detect them:

1. **`voices/deep_narrator.wav`**: Deep narrative voice mapped for YouTube Essays.
2. **`voices/tiktok_hype.wav`**: High-energy voice for TikTok/Shorts.
3. **`voices/assistant_calm.wav`**: Clean conversational tone for AI assistants.
