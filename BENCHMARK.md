# Benchmarking Methodology & Metrics Guide

This document defines the metrics measured by `run_all_models.py` and displayed on the Streamlit dashboard.

---

## Benchmark Metrics

1. **Generation Time (`gen_time_sec`)**:
   - Total latency (in seconds) required by the model to synthesize the audio output.

2. **Audio Output Duration (`audio_duration_sec`)**:
   - Duration (in seconds) of the synthesized audio stream.

3. **Real-Time Factor (`real_time_factor` / RTF)**:
   - Defined as: $\text{RTF} = \frac{\text{Generation Time}}{\text{Audio Duration}}$
   - An RTF $< 1.0$ indicates real-time synthesis (faster than human speech playback).
   - An RTF $> 1.0$ indicates batch processing slower than real-time.

4. **Peak GPU VRAM (`vram_used_mb`)**:
   - Maximum VRAM allocated by PyTorch CUDA memory tracking during inference (MB).

5. **System RAM (`ram_used_mb`)**:
   - Resident set memory (RSS) consumed by the process.

6. **Speaker Similarity Score (`speaker_similarity`)**:
   - Cosine similarity between acoustic spectral vectors of generated audio and `voices/reference.wav` (0.0 to 1.0 scale).

7. **Audio File Size (`file_size_kb`)**:
   - Storage footprint of the generated output `.wav` file (KB).

8. **MOS Score (`mos_score`)**:
   - Mean Opinion Score (1.0 - 5.0 rating scale) manually rated in the Streamlit dashboard.

---

## Standard Prompts

- **Short**: ~20 words (`prompts/prompt_short.txt`) - Latency test
- **Medium**: ~60 words (`prompts/prompt_medium.txt`) - Standard sentence prosody
- **Long**: ~150 words (`prompts/prompt_long.txt`) - Long context stability test
