# System Setup & Configuration Guide

## Hardware Configuration (RTX 3060 6GB VRAM)

Consumer laptop GPUs with 6GB VRAM require optimized execution flags to prevent CUDA out-of-memory errors:

1. **PyTorch Memory Allocation**:
   Set `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` in your environment:
   ```cmd
   set PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
   ```

2. **Garbage Collection**:
   The `run_all_models.py` script automatically executes `torch.cuda.empty_cache()` after each benchmark run.

---

## Directory Configuration

- `benchmark/`: Contains generated CSV results (`benchmark_results.csv`).
- `models/`: Contains model specific code, requirements, and test runners.
- `outputs/`: Subfolders per model (`outputs/chatterbox`, `outputs/fishspeech`, etc.) store generated WAV files.
- `voices/`: Reference voice samples used for zero-shot speaker cloning.
- `prompts/`: Evaluation prompt text files (`short`, `medium`, `long`).
