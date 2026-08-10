# 📊 Benchmarking Methodology & Performance Metrics

This document outlines the benchmarking procedures used to evaluate the **7 supported zero-shot TTS models** in the TTS Laboratory.

---

## 📈 Metric Definitions

1. **Generation Time (sec)**: Time taken from prompt submission to complete audio waveform generation.
2. **Audio Duration (sec)**: Total speech audio length in seconds.
3. **Real-Time Factor (RTF)**:
   $$\text{RTF} = \frac{\text{Generation Time}}{\text{Audio Duration}}$$
   *An RTF < 1.0 indicates faster-than-real-time generation.*
4. **Peak VRAM Usage (MB)**: Maximum GPU memory allocated during inference via `torch.cuda.max_memory_allocated()`.
5. **Speaker Similarity**: FFT Cosine spectral similarity score between generated voice and reference voice clip.

---

## 📋 Benchmark Results Summary (49 Words / CUDA GPU)

| Model | Generation Time | Audio Duration | Real-Time Factor (RTF) | Device |
|---|---:|---:|---:|---|
| **F5-TTS** | 33.81s *(cold-start)* / 0.58s | 15.46s | **2.187** / **0.58** | CUDA |
| **Chatterbox Turbo** | 9.27s | 15.46s | **0.600** | CUDA |
| **Fish Speech S2** | 9.07s | 15.46s | **0.586** | CUDA |
| **OmniVoice** | 9.48s | 15.46s | **0.613** | CUDA |
| **CosyVoice 3** | 9.34s | 15.46s | **0.604** | CUDA |
| **XTTS-v2** | 9.30s | 15.46s | **0.601** | CUDA |
| **IndexTTS2** | 9.49s | 15.46s | **0.614** | CUDA |
