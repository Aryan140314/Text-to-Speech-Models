"""
Speech Synthesis Engine — Zero-Shot Voice Cloning + Neural TTS
=================================================================
Two operating modes depending on whether a reference voice is provided:

  CLONING MODE  (reference_voice provided)
  ─────────────────────────────────────────
  1. Chatterbox TTS  — diffusion-based zero-shot cloner (pip install chatterbox-tts)
  2. F5-TTS          — flow-matching zero-shot cloner    (pip install f5-tts)
  3. Kokoro-82M      — preset voice fallback (no cloning, but natural quality)
  4. gTTS            — online Google TTS fallback
  5. SAPI5           — last resort

  PRESET MODE  (no reference_voice)
  ─────────────────────────────────────────
  1. Kokoro-82M      — best quality preset neural voice
  2. gTTS            — online Google TTS
  3. SAPI5           — last resort

Handles Windows COM thread init (CoInitialize) for Streamlit threads.
"""

import os
import wave
import time

# ---------------------------------------------------------------------------
# Configure pydub and system environment to use bundled ffmpeg (imageio-ffmpeg)
# ---------------------------------------------------------------------------
try:
    import imageio_ffmpeg
    import shutil

    _FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()
    _FFMPEG_DIR = os.path.dirname(_FFMPEG_BIN)
    _FFMPEG_EXE = os.path.join(_FFMPEG_DIR, "ffmpeg.exe")

    if not os.path.exists(_FFMPEG_EXE):
        try:
            shutil.copy(_FFMPEG_BIN, _FFMPEG_EXE)
        except Exception:
            pass

    # Add to system PATH first so pydub and transformers can find it
    if _FFMPEG_DIR not in os.environ["PATH"]:
        os.environ["PATH"] = _FFMPEG_DIR + os.pathsep + os.environ["PATH"]

    # Configure pydub
    from pydub import AudioSegment
    AudioSegment.converter = _FFMPEG_BIN
    AudioSegment.ffprobe = _FFMPEG_BIN
except Exception:
    _FFMPEG_BIN = "ffmpeg"

# ─────────────────────────────────────────────────────────────────────────────
# Backend availability checks
# ─────────────────────────────────────────────────────────────────────────────


def _chatterbox_available() -> bool:
    try:
        import chatterbox  # noqa: F401

        return True
    except ImportError:
        return False


def _f5tts_available() -> bool:
    try:
        import f5_tts  # noqa: F401

        return True
    except ImportError:
        try:
            from f5tts.infer.utils_infer import infer_process  # noqa: F401

            return True
        except ImportError:
            return False


def _kokoro_available() -> bool:
    try:
        import kokoro  # noqa: F401
        import soundfile  # noqa: F401

        return True
    except ImportError:
        return False


def _gtts_available() -> bool:
    try:
        from gtts import gTTS  # noqa: F401

        return True
    except ImportError:
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Kokoro voice presets — one distinct character per model slot
# ─────────────────────────────────────────────────────────────────────────────

_KOKORO_VOICE_MAP = {
    "chatterbox": "af_heart",  # Warm expressive American female
    "fishspeech": "am_michael",  # Deep clear American male
    "omnivoice": "af_bella",  # Confident articulate female
    "cosyvoice": "bf_emma",  # Smooth British female
    "xttsv2": "am_adam",  # Authoritative American male
    "f5tts": "af_nicole",  # Energetic young American female
    "indextts2": "bm_george",  # Distinguished British male
    "kokoro": "af_sky",  # Bright natural American female
    "elevenlabs": "af_heart",  # Natural emotional female
}

# ─────────────────────────────────────────────────────────────────────────────
# Cached model instances (avoid reloading on every call)
# ─────────────────────────────────────────────────────────────────────────────

_chatterbox_model = None
_chatterbox_lock = None

_kokoro_pipeline = None
_kokoro_lock = None


# ─────────────────────────────────────────────────────────────────────────────
# Backend 1 (Cloning): Chatterbox TTS — diffusion zero-shot cloner
# ─────────────────────────────────────────────────────────────────────────────


def _ensure_chatterbox():
    global _chatterbox_model, _chatterbox_lock
    if _chatterbox_lock is None:
        import threading

        _chatterbox_lock = threading.Lock()
    with _chatterbox_lock:
        if _chatterbox_model is None:
            import torch
            from chatterbox.tts import ChatterboxTTS

            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"[>>] Loading Chatterbox TTS on {device}...")
            _chatterbox_model = ChatterboxTTS.from_pretrained(device=device)
    return _chatterbox_model


def _synthesize_chatterbox_clone(
    text: str, reference_wav: str, output_path: str
) -> bool:
    """Zero-shot voice cloning with Chatterbox TTS."""
    try:
        import torch
        import torchaudio

        model = _ensure_chatterbox()
        print(
            f"[>>] Chatterbox cloning with reference: {os.path.basename(reference_wav)}"
        )
        wav = model.generate(text, audio_prompt_path=reference_wav)
        torchaudio.save(output_path, wav, model.sr)
        return os.path.exists(output_path) and os.path.getsize(output_path) > 1000
    except Exception as e:
        print(f"[!] Chatterbox cloning failed: {e}")
        return False


def _synthesize_chatterbox_preset(text: str, output_path: str) -> bool:
    """Chatterbox TTS without a reference voice (default voice)."""
    try:
        import torch
        import torchaudio

        model = _ensure_chatterbox()
        wav = model.generate(text)
        torchaudio.save(output_path, wav, model.sr)
        return os.path.exists(output_path) and os.path.getsize(output_path) > 1000
    except Exception as e:
        print(f"[!] Chatterbox preset failed: {e}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Backend 2 (Cloning): F5-TTS — flow-matching zero-shot cloner
# ─────────────────────────────────────────────────────────────────────────────

_f5tts_model = None
_f5tts_lock = None


def _ensure_f5tts_model():
    global _f5tts_model, _f5tts_lock
    if _f5tts_lock is None:
        import threading

        _f5tts_lock = threading.Lock()
    with _f5tts_lock:
        if _f5tts_model is None:
            from f5_tts.api import F5TTS
            import torch

            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"[>>] Loading F5-TTS model on {device}...")
            _f5tts_model = F5TTS(device=device)
    return _f5tts_model


def _synthesize_f5tts_clone(text: str, reference_wav: str, output_path: str) -> bool:
    """Zero-shot voice cloning with F5-TTS Python API."""
    try:
        import numpy as np
        import soundfile as sf

        model = _ensure_f5tts_model()
        print(f"[>>] F5-TTS cloning reference: {os.path.basename(reference_wav)}")

        wav, sr, _ = model.infer(
            ref_file=reference_wav,
            ref_text="",  # auto-transcribe reference
            gen_text=text,
            show_info=lambda x: None,
        )

        # wav is a numpy array from F5-TTS
        if isinstance(wav, list):
            import numpy as np

            wav = np.concatenate(wav)

        sf.write(output_path, wav, sr)
        return os.path.exists(output_path) and os.path.getsize(output_path) > 1000

    except Exception as e:
        print(f"[!] F5-TTS cloning failed: {e}")
        import traceback

        traceback.print_exc()
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Backend 3: Kokoro-82M — best quality preset voices (no cloning)
# ─────────────────────────────────────────────────────────────────────────────


def _ensure_kokoro_pipeline(lang: str = "a"):
    global _kokoro_pipeline, _kokoro_lock
    if _kokoro_lock is None:
        import threading

        _kokoro_lock = threading.Lock()
    with _kokoro_lock:
        if _kokoro_pipeline is None:
            from kokoro import KPipeline

            _kokoro_pipeline = KPipeline(lang_code=lang)
    return _kokoro_pipeline


def _synthesize_kokoro(text: str, voice_id: str, output_path: str) -> bool:
    """Kokoro-82M preset neural voice synthesis."""
    try:
        import soundfile as sf
        import numpy as np

        pipeline = _ensure_kokoro_pipeline(lang="a")
        audio_segments = []
        for _, _, audio in pipeline(
            text, voice=voice_id, speed=1.0, split_pattern=r"\n+"
        ):
            if audio is not None and len(audio) > 0:
                audio_segments.append(audio)
        if not audio_segments:
            return False
        combined = np.concatenate(audio_segments, axis=0)
        sf.write(output_path, combined, 24000)
        return os.path.exists(output_path) and os.path.getsize(output_path) > 1000
    except Exception as e:
        print(f"[!] Kokoro synthesis failed: {e}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Backend 4: gTTS — Google online TTS (natural, no cloning)
# ─────────────────────────────────────────────────────────────────────────────


def _synthesize_gtts(text: str, output_path: str) -> bool:
    try:
        from gtts import gTTS
        from pydub import AudioSegment

        mp3_path = output_path.replace(".wav", "_tmp.mp3")
        gTTS(text=text, lang="en", slow=False).save(mp3_path)
        AudioSegment.converter = _FFMPEG_BIN
        AudioSegment.from_mp3(mp3_path).export(output_path, format="wav")
        os.remove(mp3_path)
        return os.path.exists(output_path) and os.path.getsize(output_path) > 1000
    except Exception as e:
        print(f"[!] gTTS failed: {e}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Backend 5: Windows SAPI5 — robotic last-resort emergency fallback
# ─────────────────────────────────────────────────────────────────────────────


def _synthesize_sapi(text: str, output_path: str) -> bool:
    try:
        import win32com.client

        co_initialized = False
        try:
            import pythoncom

            pythoncom.CoInitialize()
            co_initialized = True
        except Exception:
            pass
        try:
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            stream = win32com.client.Dispatch("SAPI.SpFileStream")
            stream.Open(output_path, 3, False)
            speaker.AudioOutputStream = stream
            speaker.Speak(text)
            stream.Close()
        finally:
            if co_initialized:
                try:
                    import pythoncom

                    pythoncom.CoUninitialize()
                except Exception:
                    pass
        return os.path.exists(output_path) and os.path.getsize(output_path) > 0
    except Exception as e:
        print(f"[!] SAPI5 failed: {e}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────


def synthesize_human_speech(
    text: str, model_id: str, reference_voice: str = None, output_path: str = None
) -> dict:
    """
    Generate natural, human-quality speech with optional zero-shot voice cloning.

    CLONING MODE  — when reference_voice is a valid .wav file:
        1. Chatterbox TTS  (diffusion zero-shot cloner)
        2. F5-TTS          (flow-matching zero-shot cloner)
        3. Kokoro-82M      (preset fallback — no cloning)
        4. gTTS            (online fallback)
        5. SAPI5           (last resort)

    PRESET MODE  — when no reference_voice:
        1. Kokoro-82M      (best quality preset neural voice)
        2. gTTS            (online Google TTS)
        3. SAPI5           (last resort)

    Args:
        text:            Text to synthesize
        model_id:        TTS model slot ID (maps to Kokoro voice character)
        reference_voice: Path to reference .wav for zero-shot cloning
        output_path:     Where to write the output .wav file

    Returns:
        dict: model, backend, cloning_active, gen_time, duration, file_size_kb, output_path
    """
    start_t = time.time()

    if output_path is None:
        output_path = f"outputs/{model_id}/{model_id}_output.wav"

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    voice_id = _KOKORO_VOICE_MAP.get(model_id, "af_heart")

    # Validate reference voice
    has_reference = (
        reference_voice is not None
        and os.path.exists(reference_voice)
        and os.path.getsize(reference_voice) > 1000
    )

    cloning_active = False
    backend_used = "none"
    success = False

    if has_reference:
        # ── CLONING MODE ──────────────────────────────────────────────────
        print(f"[>>] CLONING MODE — reference: {os.path.basename(reference_voice)}")

        # 1. Chatterbox TTS
        if not success and _chatterbox_available():
            print(f"[>>] Trying Chatterbox TTS zero-shot cloning...")
            success = _synthesize_chatterbox_clone(text, reference_voice, output_path)
            if success:
                backend_used = "chatterbox-clone"
                cloning_active = True
                print(f"[OK] Chatterbox cloning succeeded — speaking in YOUR voice")

        # 2. F5-TTS
        if not success and _f5tts_available():
            print(f"[>>] Trying F5-TTS zero-shot cloning...")
            success = _synthesize_f5tts_clone(text, reference_voice, output_path)
            if success:
                backend_used = "f5tts-clone"
                cloning_active = True
                print(f"[OK] F5-TTS cloning succeeded — speaking in YOUR voice")

        # 3. Kokoro fallback (preset, no cloning)
        if not success and _kokoro_available():
            print(f"[!!] Cloning backends unavailable — falling back to Kokoro preset")
            success = _synthesize_kokoro(text, voice_id, output_path)
            if success:
                backend_used = "kokoro-preset"
                cloning_active = False
                print(f"[OK] Kokoro preset synthesis succeeded (voice: {voice_id})")

    else:
        # ── PRESET MODE ───────────────────────────────────────────────────
        print(f"[>>] PRESET MODE — voice: {voice_id}")

        # 1. Kokoro-82M
        if not success and _kokoro_available():
            success = _synthesize_kokoro(text, voice_id, output_path)
            if success:
                backend_used = "kokoro"
                print(f"[OK] Kokoro preset succeeded (voice: {voice_id})")

        # 2. Chatterbox default (no reference)
        if not success and _chatterbox_available():
            print(f"[>>] Trying Chatterbox default voice...")
            success = _synthesize_chatterbox_preset(text, output_path)
            if success:
                backend_used = "chatterbox"
                print(f"[OK] Chatterbox default voice succeeded")

    # ── Universal fallbacks ────────────────────────────────────────────────
    if not success and _gtts_available():
        print(f"[>>] Falling back to gTTS (online Google TTS)...")
        success = _synthesize_gtts(text, output_path)
        if success:
            backend_used = "gtts"

    if not success:
        print(f"[>>] All backends failed — emergency SAPI5 fallback")
        success = _synthesize_sapi(text, output_path)
        if success:
            backend_used = "sapi5"

    gen_time = round(time.time() - start_t, 4)

    # Audio stats
    duration = 0.0
    file_size_kb = 0.0
    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        file_size_kb = round(os.path.getsize(output_path) / 1024, 2)
        try:
            with wave.open(output_path, "r") as wf:
                duration = round(wf.getnframes() / float(wf.getframerate()), 2)
        except Exception:
            duration = round(len(text.split()) * 0.35, 2)

    mode = "CLONING" if cloning_active else "PRESET"
    print(f"[+] [{mode}] Speech Generated: {output_path}")
    print(
        f"    Backend: {backend_used} | Model: {model_id} | Gen: {gen_time}s | Duration: {duration}s | Size: {file_size_kb} KB"
    )

    return {
        "model": model_id,
        "backend": backend_used,
        "cloning_active": cloning_active,
        "gen_time": gen_time,
        "duration": duration,
        "file_size_kb": file_size_kb,
        "output_path": output_path,
    }
