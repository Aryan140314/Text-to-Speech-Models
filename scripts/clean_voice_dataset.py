#!/usr/bin/env python3
"""
clean_voice_dataset.py
======================
Production Voice Dataset Cleaning Utility
TTS Laboratory | Audio DSP Engineering Division

Removes background noise, music, and environmental sounds from voice recordings
while preserving the speaker's natural voice identity, timbre, and characteristics.

Supported input : .wav .mp3 .m4a .flac .ogg .aac .opus
Output mirror   : voices_clean/  (exact subfolder structure preserved)

Enhancement pipeline (best available backend auto-selected at runtime):
  Tier 1 - DeepFilterNet3  neural speech enhancement           (best quality)
  Tier 2 - noisereduce     two-pass statistical spectral reduction
  Tier 3 - spectral sub.   scipy STFT spectral subtraction     (always available)

Post-processing applied after every backend:
  * High-pass filter 80 Hz  -- removes low-frequency rumble and wind
  * Noise gate              -- suppresses silence between words
  * Peak normalization      -- consistent loudness across all files

Usage:
    python clean_voice_dataset.py
    python clean_voice_dataset.py --input D:/voices --output D:/voices_clean
    python clean_voice_dataset.py --strength 0.9 --format flac --overwrite
    python clean_voice_dataset.py --help
"""

from __future__ import annotations
import os
import sys
import time
import argparse
import warnings
import logging
import traceback
import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

warnings.filterwarnings("ignore")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")


# =============================================================================
# CONFIGURATION  --  edit these values before running
# =============================================================================

@dataclass
class Config:
    """
    All parameters in one place.
    Override any value here OR pass CLI arguments (python clean_voice_dataset.py --help).
    """

    # Directories
    input_dir:  str = r"D:\Saurav\TTS\voices"
    output_dir: str = r"D:\Saurav\TTS\voices_clean"
    log_file:   str = r"D:\Saurav\TTS\cleaning_log.txt"

    # Noise reduction aggressiveness: 0.0 = off, 1.0 = maximum aggressive
    # Recommended: 0.65-0.80 for most recordings.
    # Reduce to 0.50 if the output voice sounds metallic or over-processed.
    noise_reduction_strength: float = 0.75

    # Music / steady background suppression strength (used in 2nd noisereduce pass)
    # DeepFilterNet handles music automatically; this only applies to noisereduce backend.
    music_suppression_strength: float = 0.75

    # Output format: "wav" (16-bit PCM, universal) or "flac" (lossless, smaller)
    output_format: str = "wav"

    # Output sample rate in Hz. None = preserve the original file's sample rate.
    sample_rate: Optional[int] = None

    # False = skip files that already exist in output_dir (safe for re-runs)
    # True  = re-process and overwrite existing files
    overwrite_existing: bool = False

    # Long files are split into overlapping chunks to control RAM usage.
    chunk_duration_s: float = 30.0
    chunk_overlap_s:  float = 0.5

    # 1 = sequential (safest, lowest memory). Increase only on multi-core systems.
    max_workers: int = 1

    # High-pass filter: removes low-frequency rumble, table vibration, wind noise
    apply_high_pass:     bool  = True
    high_pass_cutoff_hz: float = 80.0

    # Noise gate: suppresses residual noise in silence between speech segments
    apply_noise_gate:        bool  = True
    noise_gate_threshold_db: float = -48.0  # gate opens when signal > this dBFS
    noise_gate_attack_ms:    float = 5.0    # fast attack (avoid cutting word starts)
    noise_gate_release_ms:   float = 120.0  # slow release (preserve natural pauses)

    # Peak normalize to consistent output level
    normalize_output:      bool  = True
    normalize_target_dbfs: float = -1.0    # just below full scale

    progress_display: bool = True

    # Supported input file extensions (add/remove as needed)
    supported_extensions: Tuple[str, ...] = (
        ".wav", ".mp3", ".m4a", ".flac",
        ".ogg", ".aac", ".opus",
    )


# Singleton configuration used throughout the script
CONFIG = Config()


# =============================================================================
# DEPENDENCY DETECTION
# =============================================================================

def _check_imports() -> Dict[str, bool]:
    """Probe all optional libraries. Returns an availability map."""
    avail: Dict[str, bool] = {}

    # Core (required)
    for pkg in ("numpy", "scipy", "soundfile", "librosa"):
        try:
            __import__(pkg)
            avail[pkg] = True
        except ImportError:
            avail[pkg] = False

    # Optional neural backend
    try:
        import noisereduce  # noqa: F401
        avail["noisereduce"] = True
    except ImportError:
        avail["noisereduce"] = False

    # Optional deep learning backend
    try:
        import torch  # noqa: F401
        from df import enhance, init_df  # noqa: F401
        avail["deepfilternet"] = True
    except (ImportError, Exception):
        avail["deepfilternet"] = False

    # Optional progress bar
    try:
        import tqdm  # noqa: F401
        avail["tqdm"] = True
    except ImportError:
        avail["tqdm"] = False

    return avail


AVAIL = _check_imports()

# Hard-fail on missing required core libraries
_MISSING = [p for p in ("numpy", "scipy", "soundfile", "librosa") if not AVAIL[p]]
if _MISSING:
    print(f"[ERROR] Missing required packages: {', '.join(_MISSING)}")
    print("        Install: pip install numpy scipy soundfile librosa")
    sys.exit(1)

import scipy.signal
import scipy.io.wavfile
import soundfile as sf
import librosa
import librosa.util

# DeepFilterNet model singleton (loaded once, reused for every file)
_df_model = None
_df_state = None


# =============================================================================
# LOGGING
# =============================================================================

def setup_logger(log_file: str) -> logging.Logger:
    """Dual logger: console (INFO+) and file (DEBUG+). Overwrites log each run."""
    os.makedirs(os.path.dirname(os.path.abspath(log_file)) or ".", exist_ok=True)
    logger = logging.getLogger("VoiceCleaner")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    # Console handler: clean minimal output
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(message)s"))

    # File handler: full diagnostic detail for every file
    fh = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))

    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger


# =============================================================================
# AUDIO I/O
# =============================================================================

def load_audio(path: Path, target_sr: Optional[int] = None) -> Tuple[np.ndarray, int]:
    """
    Load any supported audio file as float32 mono numpy array.

    Tries three loaders in order:
      1. librosa  -- handles all formats via soundfile + optional ffmpeg
      2. soundfile -- fast native reader for wav/flac/ogg
      3. pydub    -- mp3/m4a/aac/opus via system ffmpeg

    Returns:
        (audio, sample_rate) where audio is float32 mono in [-1.0, 1.0]
    """
    path_str = str(path)

    # Loader 1: librosa (most reliable, uses ffmpeg when available)
    try:
        audio, sr = librosa.load(path_str, sr=target_sr, mono=True)
        return audio.astype(np.float32), int(sr)
    except Exception:
        pass

    # Loader 2: soundfile (fast for wav/flac/ogg)
    try:
        audio, sr = sf.read(path_str, always_2d=False)
        if audio.ndim > 1:
            audio = audio.mean(axis=1)          # stereo to mono
        audio = audio.astype(np.float32)
        if target_sr and sr != target_sr:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=target_sr)
            sr = target_sr
        return audio, int(sr)
    except Exception:
        pass

    # Loader 3: pydub (mp3/m4a/aac/opus; uses imageio_ffmpeg if system ffmpeg is missing)
    try:
        from pydub import AudioSegment
        try:
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            AudioSegment.converter = ffmpeg_exe
        except Exception:
            pass

        seg = AudioSegment.from_file(path_str).set_channels(1)
        if target_sr:
            seg = seg.set_frame_rate(target_sr)
        sr = seg.frame_rate
        raw = np.array(seg.get_array_of_samples(), dtype=np.float32)
        divisor = {1: 128.0, 2: 32768.0, 3: 8388608.0, 4: 2147483648.0}
        raw /= divisor.get(seg.sample_width, 32768.0)
        return raw, int(sr)
    except Exception:
        pass

    # Loader 4: Direct imageio_ffmpeg subprocess conversion (for m4a/aac/opus)
    try:
        import imageio_ffmpeg
        import tempfile, subprocess
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_wav = tmp.name

        cmd = [
            ffmpeg_exe, "-y", "-i", path_str,
            "-ar", str(target_sr or 22050), "-ac", "1",
            "-f", "wav", tmp_wav
        ]
        subprocess.run(cmd, capture_output=True, check=True, timeout=30)
        audio, sr = sf.read(tmp_wav, always_2d=False)
        try:
            os.remove(tmp_wav)
        except Exception:
            pass
        return audio.astype(np.float32), int(sr)
    except Exception as exc:
        raise RuntimeError(f"All audio loaders failed for {path.name!r}: {exc}") from exc


def save_audio(audio: np.ndarray, sr: int, out_path: Path, fmt: str = "wav") -> None:
    """Save float32 mono audio to disk. Auto-creates parent directories."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    audio = np.clip(audio, -1.0, 1.0)

    if fmt.lower() == "flac":
        sf.write(str(out_path), audio, sr, subtype="PCM_16")
    else:
        # WAV 16-bit PCM -- broadest player/software compatibility
        scipy.io.wavfile.write(str(out_path), sr, (audio * 32767.0).astype(np.int16))


# =============================================================================
# POST-PROCESSING UTILITIES
# =============================================================================

def apply_high_pass_filter(
    audio: np.ndarray,
    sr: int,
    cutoff_hz: float = 80.0,
    order: int = 4,
) -> np.ndarray:
    """
    4th-order Butterworth high-pass filter.
    Removes: low-frequency rumble, table vibrations, HVAC drone, wind pops.
    Applied BEFORE the denoising backend for better noise profiling.
    """
    nyquist = sr / 2.0
    if cutoff_hz <= 0.0 or cutoff_hz >= nyquist:
        return audio
    b, a = scipy.signal.butter(
        N=order, Wn=min(cutoff_hz / nyquist, 0.99), btype="high"
    )
    return scipy.signal.filtfilt(b, a, audio).astype(np.float32)


def apply_noise_gate(
    audio: np.ndarray,
    sr: int,
    threshold_db: float = -48.0,
    attack_ms: float = 5.0,
    release_ms: float = 120.0,
) -> np.ndarray:
    """
    Frame-based noise gate with smooth cosine attack/release envelope.

    Opens when signal energy exceeds threshold_db (dBFS).
    Slow release (120 ms) preserves natural breathing, pauses, and micro-silences.
    Fast attack (5 ms) avoids cutting the beginning of words.
    """
    frame_len = max(256, int(sr * 0.02))    # 20 ms analysis window
    hop_len   = frame_len // 2

    try:
        frames = librosa.util.frame(audio, frame_length=frame_len, hop_length=hop_len)
    except Exception:
        return audio  # Audio too short to gate; return unchanged

    rms = np.sqrt(np.mean(frames ** 2, axis=0))
    threshold_linear = 10.0 ** (threshold_db / 20.0)
    gate_open = (rms > threshold_linear).astype(np.float32)

    att_frames = max(1, int(attack_ms  / 1000.0 * sr / hop_len))
    rel_frames = max(1, int(release_ms / 1000.0 * sr / hop_len))

    # Smooth the gate signal with attack/release time constants
    envelope = np.zeros_like(gate_open)
    level = 0.0
    for i, g in enumerate(gate_open):
        if g > level:
            level = min(1.0, level + 1.0 / att_frames)
        else:
            level = max(0.0, level - 1.0 / rel_frames)
        envelope[i] = level

    # Upsample frame-level envelope back to sample resolution
    frame_centers = np.arange(len(envelope)) * hop_len + frame_len // 2
    gain = np.interp(np.arange(len(audio)), frame_centers, envelope).astype(np.float32)

    return (audio * np.clip(gain, 0.0, 1.0)).astype(np.float32)


def peak_normalize(audio: np.ndarray, target_dbfs: float = -1.0) -> np.ndarray:
    """Normalize peak to target_dbfs dBFS. Skips silent audio."""
    peak = float(np.max(np.abs(audio)))
    if peak < 1e-8:
        return audio
    return (audio * (10.0 ** (target_dbfs / 20.0) / peak)).astype(np.float32)


def _safe(audio: np.ndarray) -> np.ndarray:
    """Replace NaN/Inf from aggressive DSP, then hard-clip to [-1, 1]."""
    return np.clip(
        np.nan_to_num(audio, nan=0.0, posinf=1.0, neginf=-1.0),
        -1.0, 1.0,
    ).astype(np.float32)


# =============================================================================
# ENHANCEMENT BACKENDS
# =============================================================================

def _load_deepfilternet(logger: Optional[logging.Logger] = None) -> bool:
    """
    Lazily initialize DeepFilterNet3 model singleton.
    Downloads ~120 MB to HuggingFace cache on first use.
    Returns True if model is ready, False otherwise.
    """
    global _df_model, _df_state, AVAIL
    if not AVAIL["deepfilternet"]:
        return False
    if _df_model is not None:
        return True
    try:
        from df import init_df
        _df_model, _df_state, _ = init_df()
        msg = "[OK] DeepFilterNet3 loaded -- neural speech enhancement active"
        (logger.info if logger else print)(msg)
        return True
    except Exception as exc:
        AVAIL["deepfilternet"] = False
        msg = f"[WARN] DeepFilterNet failed to load ({exc}); switching to noisereduce"
        (logger.warning if logger else print)(msg)
        return False


def _enhance_deepfilternet(
    audio: np.ndarray,
    sr: int,
    strength: float,
) -> np.ndarray:
    """
    DeepFilterNet3 neural speech enhancement.

    Handles all noise types in a single pass:
    stationary noise, non-stationary noise, music, TV audio, reverb, crowd.

    strength maps to atten_lim_db (maximum per-frequency attenuation):
      0.50 -->  25 dB  (conservative; safest for clean recordings)
      0.75 -->  37 dB  (recommended default)
      1.00 --> None    (unlimited; most aggressive, may risk artifacts)
    """
    import torch
    from df import enhance as df_enhance

    df_sr: int = _df_state.sr()    # DeepFilterNet3 operates at 48000 Hz

    # Resample to model's required rate
    if sr != df_sr:
        audio_in = librosa.resample(audio, orig_sr=sr, target_sr=df_sr)
    else:
        audio_in = audio.copy()

    atten_lim = None if strength >= 0.99 else float(max(5.0, strength * 50.0))

    # DeepFilterNet expects shape (n_channels, n_samples) -- (1, T) for mono
    audio_tensor = torch.from_numpy(audio_in).unsqueeze(0)

    with torch.no_grad():
        enhanced = df_enhance(
            _df_model, _df_state,
            audio_tensor,
            atten_lim_db=atten_lim,
        )

    result = enhanced.squeeze().numpy().astype(np.float32)

    # Resample back to the original rate
    if sr != df_sr:
        result = librosa.resample(result, orig_sr=df_sr, target_sr=sr)

    return _safe(result)


def _enhance_noisereduce(
    audio: np.ndarray,
    sr: int,
    noise_strength: float,
    music_strength: float,
) -> np.ndarray:
    """
    Two-pass noisereduce enhancement.

    Pass 1 (non-stationary):  catches varying noise -- music, TV, crowd, traffic.
    Pass 2 (stationary):      catches steady noise  -- hiss, hum, fan, electrical.

    Two separate passes allow different aggressiveness per noise class
    without risking voice damage from a single overly aggressive pass.
    """
    import noisereduce as nr

    # Pass 1: non-stationary (variable) background removal
    cleaned = _safe(nr.reduce_noise(
        y=audio, sr=sr,
        stationary=False,
        prop_decrease=noise_strength,
        n_std_thresh_stationary=1.5,
        freq_mask_smooth_hz=500,
        time_mask_smooth_ms=50,
    ))

    # Pass 2: stationary (constant) noise -- more conservative to protect voice
    stationary_strength = min(0.65, music_strength * 0.60)
    if stationary_strength > 0.10:
        cleaned = _safe(nr.reduce_noise(
            y=cleaned, sr=sr,
            stationary=True,
            prop_decrease=stationary_strength,
        ))

    return cleaned.astype(np.float32)


def _enhance_spectral_subtraction(
    audio: np.ndarray,
    sr: int,
    strength: float,
) -> np.ndarray:
    """
    STFT-based spectral subtraction (scipy only -- always available fallback).

    Estimates the noise floor from the first 250 ms of audio (pre-speech region).
    Applies a 5% spectral floor to prevent "musical noise" ring artifacts.
    """
    n_fft, hop = 2048, 512

    stft     = librosa.stft(audio, n_fft=n_fft, hop_length=hop)
    magnitude = np.abs(stft)
    phase     = np.angle(stft)

    # Noise profile from first ~250 ms (assumed noise floor / silence)
    noise_frames  = max(2, int(0.25 * sr / hop))
    noise_profile = np.mean(magnitude[:, :noise_frames], axis=1, keepdims=True)

    alpha     = 1.0 + strength * 3.0               # over-subtraction factor
    mag_clean = np.maximum(magnitude - alpha * noise_profile, 0.05 * magnitude)

    audio_clean = librosa.istft(
        mag_clean * np.exp(1j * phase),
        hop_length=hop, n_fft=n_fft, length=len(audio),
    )
    return _safe(audio_clean)


# =============================================================================
# MAIN CLEANING PIPELINE
# =============================================================================

def clean_audio(
    audio: np.ndarray,
    sr: int,
    config: Config,
    logger: Optional[logging.Logger] = None,
) -> np.ndarray:
    """
    Four-stage cleaning pipeline applied to one audio array.

    Stage 1 -- High-pass pre-filter   (removes rumble before denoising)
    Stage 2 -- Core enhancement       (best available backend auto-selected)
    Stage 3 -- Noise gate             (removes residual inter-word noise)
    Stage 4 -- Peak normalization     (consistent output level)

    Falls back gracefully through tiers if the primary backend fails on a file.
    In the worst case, returns the original audio (never crashes).
    """
    cleaned = audio.copy()

    # Stage 1: High-pass pre-filter
    if config.apply_high_pass:
        cleaned = apply_high_pass_filter(cleaned, sr, config.high_pass_cutoff_hz)

    # Stage 2: Core noise/music removal
    try:
        if AVAIL["deepfilternet"] and _load_deepfilternet(logger):
            cleaned = _enhance_deepfilternet(cleaned, sr, config.noise_reduction_strength)
        elif AVAIL["noisereduce"]:
            cleaned = _enhance_noisereduce(
                cleaned, sr,
                config.noise_reduction_strength,
                config.music_suppression_strength,
            )
        else:
            cleaned = _enhance_spectral_subtraction(cleaned, sr, config.noise_reduction_strength)
    except Exception as exc:
        if logger:
            logger.debug(f"Primary backend error -- trying fallback: {exc}")
        try:
            if AVAIL["noisereduce"]:
                cleaned = _enhance_noisereduce(
                    cleaned, sr,
                    config.noise_reduction_strength * 0.55,
                    config.music_suppression_strength * 0.55,
                )
            else:
                cleaned = _enhance_spectral_subtraction(
                    audio, sr, config.noise_reduction_strength * 0.5
                )
        except Exception:
            cleaned = audio.copy()    # Ultimate safety: return original untouched

    cleaned = _safe(cleaned)

    # Stage 3: Noise gate
    if config.apply_noise_gate:
        cleaned = apply_noise_gate(
            cleaned, sr,
            threshold_db=config.noise_gate_threshold_db,
            attack_ms=config.noise_gate_attack_ms,
            release_ms=config.noise_gate_release_ms,
        )

    # Stage 4: Peak normalization
    if config.normalize_output:
        cleaned = peak_normalize(cleaned, config.normalize_target_dbfs)

    return _safe(cleaned)


def clean_audio_chunked(
    audio: np.ndarray,
    sr: int,
    config: Config,
    logger: Optional[logging.Logger] = None,
) -> np.ndarray:
    """
    Process long audio files in overlapping chunks to limit RAM usage.

    Short files (< chunk_duration_s) are processed as a single chunk.
    Chunk boundaries are joined using cosine cross-fades to prevent
    audible clicks or discontinuities at seams.
    """
    chunk_s   = int(config.chunk_duration_s * sr)
    overlap_s = int(config.chunk_overlap_s  * sr)
    total     = len(audio)

    if total <= chunk_s:
        return clean_audio(audio, sr, config, logger)

    output = np.zeros(total, dtype=np.float32)
    weight = np.zeros(total, dtype=np.float32)
    step   = max(1, chunk_s - overlap_s)

    for start in range(0, total, step):
        end   = min(start + chunk_s, total)
        chunk = audio[start:end]
        cc    = clean_audio(chunk, sr, config, logger)
        n     = len(cc)

        # Cosine fade-in / fade-out for smooth stitching at chunk boundaries
        fl = min(overlap_s, n // 4, 4096)
        w  = np.ones(n, dtype=np.float32)
        if fl > 0:
            t  = np.linspace(0.0, 1.0, fl)
            fi = ((1.0 - np.cos(np.pi * t)) / 2.0).astype(np.float32)
            fo = ((1.0 + np.cos(np.pi * t)) / 2.0).astype(np.float32)
            cc[:fl]  *= fi
            cc[-fl:] *= fo
            w[:fl]   =  fi
            w[-fl:]  =  fo

        output[start:start + n] += cc
        weight[start:start + n] += w

    output /= np.maximum(weight, 1e-8)
    return _safe(output)


# =============================================================================
# FILE DISCOVERY
# =============================================================================

def scan_audio_files(input_dir: Path, extensions: Tuple[str, ...]) -> List[Path]:
    """Recursively scan for supported audio files. Returns a sorted list."""
    found: List[Path] = []
    for root, _dirs, files in os.walk(input_dir):
        for fname in files:
            if Path(fname).suffix.lower() in extensions:
                found.append(Path(root) / fname)
    return sorted(found)


def get_output_path(
    in_file:   Path,
    in_dir:    Path,
    out_dir:   Path,
    out_fmt:   str,
) -> Path:
    """
    Mirror input file path under out_dir with the target extension.
    voices/Documentary/speaker01.mp3  -->  voices_clean/Documentary/speaker01.wav
    """
    relative = in_file.relative_to(in_dir)
    return out_dir / relative.with_suffix(f".{out_fmt.lstrip('.')}")


# =============================================================================
# PER-FILE PROCESSOR
# =============================================================================

def process_file(
    in_path:  Path,
    out_path: Path,
    config:   Config,
    logger:   logging.Logger,
) -> Dict[str, Any]:
    """
    Load, clean, and save a single audio file.
    Never raises -- all exceptions are caught and recorded in the returned stats dict.

    Returns:
        {
            "file":        str path to input file,
            "status":      "success" | "skipped" | "failed",
            "duration_s":  float audio duration in seconds,
            "proc_time_s": float wall-clock processing time,
            "error":       str error message or None,
        }
    """
    stats: Dict[str, Any] = {
        "file": str(in_path),
        "status": "unknown",
        "duration_s": 0.0,
        "proc_time_s": 0.0,
        "error": None,
    }
    t0 = time.perf_counter()

    # Skip if output already exists and overwrite is disabled
    if not config.overwrite_existing and out_path.exists():
        stats["status"] = "skipped"
        logger.debug(f"SKIP   {in_path.name!r}  (output already exists)")
        return stats

    try:
        # Load
        audio, sr   = load_audio(in_path, target_sr=config.sample_rate)
        duration_s  = len(audio) / max(sr, 1)
        stats["duration_s"] = round(duration_s, 3)

        # Sanity: skip too-short or silent files
        if duration_s < 0.1:
            stats["status"] = "skipped"
            logger.debug(f"SKIP   {in_path.name!r}  (< 100 ms)")
            return stats
        if np.max(np.abs(audio)) < 1e-7:
            stats["status"] = "skipped"
            logger.debug(f"SKIP   {in_path.name!r}  (silent audio)")
            return stats

        # Clean
        cleaned = clean_audio_chunked(audio, sr, config, logger)

        # Save
        out_sr = config.sample_rate or sr
        save_audio(cleaned, out_sr, out_path, config.output_format)

        stats["status"]     = "success"
        stats["proc_time_s"] = round(time.perf_counter() - t0, 2)
        logger.debug(
            f"OK     {in_path.name!r}  {duration_s:.1f}s @ {out_sr} Hz"
            f"  [{stats['proc_time_s']}s proc]"
        )

    except Exception as exc:
        stats["status"]     = "failed"
        stats["error"]      = str(exc)
        stats["proc_time_s"] = round(time.perf_counter() - t0, 2)
        logger.warning(f"FAIL   {in_path.name!r}: {exc}")
        logger.debug(traceback.format_exc())

    return stats


# =============================================================================
# MAIN ORCHESTRATOR
# =============================================================================

def run_cleaning(config: Config) -> None:
    """
    Full pipeline:
      1.  Validate paths
      2.  Set up logging
      3.  Report backend and parameter configuration
      4.  Pre-load DeepFilterNet model (if available)
      5.  Recursively scan for all supported audio files
      6.  Process each file through the cleaning pipeline
      7.  Print and log the final statistics report
    """
    in_dir  = Path(config.input_dir)
    out_dir = Path(config.output_dir)
    logger  = setup_logger(config.log_file)

    sep = "-" * 70                                                      # horizontal rule
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    logger.info(sep)
    logger.info("  TTS Laboratory -- Voice Dataset Cleaning Utility")
    logger.info(f"  Started  : {now}")
    logger.info(sep)
    logger.info(f"  Input    : {in_dir}")
    logger.info(f"  Output   : {out_dir}")
    logger.info(f"  Log      : {config.log_file}")
    logger.info(f"  Format   : {config.output_format.upper()}")
    sr_label = "preserve original" if not config.sample_rate else f"{config.sample_rate} Hz"
    logger.info(f"  SR       : {sr_label}")
    logger.info(sep)

    if not in_dir.exists():
        logger.error(f"Input directory not found: {in_dir}")
        sys.exit(1)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Report active backend
    if AVAIL["deepfilternet"]:
        backend_label = "DeepFilterNet3  [neural -- best quality]"
    elif AVAIL["noisereduce"]:
        backend_label = "noisereduce     [statistical -- good quality]"
    else:
        backend_label = "spectral sub.   [scipy -- always available]"

    logger.info(f"  Backend  : {backend_label}")
    logger.info(f"  Noise    : {config.noise_reduction_strength:.0%}")
    logger.info(f"  Music    : {config.music_suppression_strength:.0%}")
    hpf = "ON" if config.apply_high_pass else "OFF"
    logger.info(f"  High-pass: {hpf} ({config.high_pass_cutoff_hz:.0f} Hz)")
    ng = "ON" if config.apply_noise_gate else "OFF"
    logger.info(f"  N-Gate   : {ng} ({config.noise_gate_threshold_db:.0f} dBFS)")
    nm = "ON" if config.normalize_output else "OFF"
    logger.info(f"  Normalize: {nm} ({config.normalize_target_dbfs:.0f} dBFS)")
    ow = "yes" if config.overwrite_existing else "no (skip existing)"
    logger.info(f"  Overwrite: {ow}")
    logger.info(sep)

    # Pre-load DeepFilterNet to avoid per-file loading overhead
    if AVAIL["deepfilternet"]:
        logger.info("[>>] Loading DeepFilterNet3 (downloads ~120 MB on first use)...")
        _load_deepfilternet(logger)

    # Scan
    logger.info("[>>] Scanning for audio files...")
    all_files = scan_audio_files(in_dir, config.supported_extensions)
    total     = len(all_files)
    logger.info(f"[>>] Found {total} audio file(s) across all subfolders")

    if total == 0:
        logger.info("[OK] Nothing to process. Exiting.")
        return

    # Counters
    cnt: Dict[str, Any] = {
        "success": 0, "skipped": 0, "failed": 0,
        "total_dur": 0.0, "total_proc": 0.0,
        "fails": [],
    }

    # Progress iterator
    if AVAIL["tqdm"] and config.progress_display:
        from tqdm import tqdm
        it = tqdm(all_files, desc="Cleaning", unit="file", ncols=80)
    else:
        it = all_files
        logger.info(f"[>>] Processing {total} files sequentially...")

    logger.info("")

    for in_p in it:
        out_p = get_output_path(in_p, in_dir, out_dir, config.output_format)
        fs    = process_file(in_p, out_p, config, logger)

        cnt["total_dur"]  += fs.get("duration_s",  0.0)
        cnt["total_proc"] += fs.get("proc_time_s", 0.0)

        if   fs["status"] == "success": cnt["success"] += 1
        elif fs["status"] == "skipped": cnt["skipped"] += 1
        else:
            cnt["failed"] += 1
            cnt["fails"].append(
                f"  [{in_p.parent.name}] {in_p.name}"
                f" -- {fs.get('error', 'unknown error')}"
            )

    # Final report
    audio_min   = cnt["total_dur"]  / 60.0
    elapsed_min = cnt["total_proc"] / 60.0
    rtf = cnt["total_proc"] / max(cnt["total_dur"], 0.001)

    logger.info("")
    logger.info(sep)
    logger.info("  CLEANING COMPLETE -- FINAL REPORT")
    logger.info(sep)
    logger.info(f"  Total files found    : {total}")
    logger.info(f"  Successfully cleaned : {cnt['success']}")
    logger.info(f"  Skipped (no change)  : {cnt['skipped']}")
    logger.info(f"  Failed               : {cnt['failed']}")
    logger.info(f"  Audio duration       : {audio_min:.1f} min")
    logger.info(f"  Processing time      : {elapsed_min:.1f} min")
    logger.info(f"  Real-Time Factor     : {rtf:.2f}x")
    logger.info(f"  Cleaned output at    : {out_dir}")
    logger.info(sep)

    if cnt["fails"]:
        logger.info("")
        logger.info("  FAILED FILES (see log for details):")
        for line in cnt["fails"]:
            logger.info(line)
        logger.info("")

    logger.info(f"  Full log: {config.log_file}")
    logger.info(sep)


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def _parse_args() -> Config:
    """Build a Config from CLI arguments, falling back to CONFIG defaults."""
    parser = argparse.ArgumentParser(
        prog="clean_voice_dataset.py",
        description="TTS Laboratory -- Voice Dataset Cleaning Utility",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--input",    default=CONFIG.input_dir,
                        help="Input directory containing voice recordings")
    parser.add_argument("--output",   default=CONFIG.output_dir,
                        help="Output directory (folder structure is preserved)")
    parser.add_argument("--log",      default=CONFIG.log_file,
                        help="Path for the cleaning log file")
    parser.add_argument("--format",   default=CONFIG.output_format,
                        choices=["wav", "flac"], help="Output audio format")
    parser.add_argument("--sr",       default=CONFIG.sample_rate, type=int,
                        metavar="HZ", help="Output sample rate (None = preserve original)")
    parser.add_argument("--strength", default=CONFIG.noise_reduction_strength,
                        type=float, metavar="0.0-1.0",
                        help="Noise reduction aggressiveness")
    parser.add_argument("--overwrite", action="store_true",
                        help="Re-process files already in the output directory")
    args = parser.parse_args()

    return Config(
        input_dir=args.input,
        output_dir=args.output,
        log_file=args.log,
        output_format=args.format,
        sample_rate=args.sr,
        noise_reduction_strength=args.strength,
        overwrite_existing=args.overwrite,
    )


if __name__ == "__main__":
    run_cleaning(_parse_args())
