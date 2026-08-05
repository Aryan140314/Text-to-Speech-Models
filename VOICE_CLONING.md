# Zero-Shot Voice Cloning & Custom Speaker Setup

## 1. Preparing Target Voice Samples

Zero-shot voice cloning enables generating audio in any target voice using just a short reference audio file without fine-tuning model parameters.

### Guidelines
- **Duration**: 4 to 8 seconds is optimal.
- **Audio Cleanliness**: Ensure zero background noise, reverb, or secondary voices.
- **Save Location**: Save your custom voice to `voices/my_voice.wav`.

---

## 2. Running Voice Cloning Inference

### Single Model Cloning
To run voice cloning on a specific model using your custom voice:

```cmd
python models/kokoro/test.py --text "Cloning my voice using Kokoro 82M." --ref voices/my_voice.wav --output outputs/kokoro/my_cloned_voice.wav
```

### Batch Benchmark Cloning
Replace `voices/reference.wav` or set `my_voice.wav` in `configs/benchmark_config.yaml` and re-run:
```cmd
python run_all_models.py
```
