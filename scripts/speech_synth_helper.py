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
# Redirect HuggingFace cache to local virtual environment folder (.venv/hf_cache)
_scripts_dir = os.path.dirname(os.path.abspath(__file__))
_workspace_root = os.path.dirname(_scripts_dir)
os.environ["HF_HOME"] = os.path.abspath(os.path.join(_workspace_root, ".venv", "hf_cache"))

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
# Backend: Audio8-TTS-Preview-0.6b — DualAR multilingual zero-shot cloner
# ─────────────────────────────────────────────────────────────────────────────

_whisper_pipeline = None
_whisper_lock = None

def _transcribe_reference(audio_path: str) -> str:
    global _whisper_pipeline, _whisper_lock
    if _whisper_lock is None:
        import threading
        _whisper_lock = threading.Lock()
    with _whisper_lock:
        if _whisper_pipeline is None:
            from transformers import pipeline
            import torch
            device = 0 if torch.cuda.is_available() else -1
            print("[>>] Loading Whisper transcription pipeline...")
            _whisper_pipeline = pipeline(
                "automatic-speech-recognition",
                model="openai/whisper-large-v3-turbo",
                torch_dtype=torch.float16 if device == 0 else torch.float32,
                device=device
            )
    res = _whisper_pipeline(audio_path, chunk_length_s=30)
    return res["text"].strip()

_audio8_model = None
_audio8_processor = None
_audio8_lock = None

def _ensure_audio8():
    global _audio8_model, _audio8_processor, _audio8_lock
    if _audio8_lock is None:
        import threading
        _audio8_lock = threading.Lock()
    with _audio8_lock:
        if _audio8_model is None:
            import sys
            import torch
            from transformers import AutoConfig, AutoModel, AutoProcessor
            
            # Inject local audio8 path for importing configuration, modeling, and processing
            audio8_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio8")
            if audio8_path not in sys.path:
                sys.path.insert(0, audio8_path)
                
            from configuration_arktts import ArkttsConfig
            from modeling_arktts import ArkttsModel
            from processing_arktts import ArkttsProcessor
            
            # Register local classes to bypass dynamic import issues on Windows
            AutoConfig.register("arktts", ArkttsConfig)
            AutoModel.register(ArkttsConfig, ArkttsModel)
            AutoProcessor.register(ArkttsConfig, ArkttsProcessor)
            
            model_id = "Audio8/Audio8-TTS-Preview-0.6b"
            device = "cuda" if torch.cuda.is_available() else "cpu"
            dtype = torch.bfloat16 if device == "cuda" else torch.float32
            
            print(f"[>>] Loading Audio8-TTS model on {device}...")
            _audio8_processor = AutoProcessor.from_pretrained(model_id)
            _audio8_model = AutoModel.from_pretrained(
                model_id,
                torch_dtype=dtype
            ).eval().to(device)
    return _audio8_model, _audio8_processor

def _audio8_available() -> bool:
    return True

def _synthesize_audio8(text: str, reference_wav: str | None, output_path: str) -> bool:
    try:
        import torch
        import soundfile as sf
        
        model, processor = _ensure_audio8()
        device = next(model.parameters()).device
        
        if reference_wav and os.path.exists(reference_wav):
            print(f"[>>] Audio8 cloning with reference: {os.path.basename(reference_wav)}")
            ref_text = _transcribe_reference(reference_wav)
            print(f"[>>] Audio8 reference transcript: {ref_text}")
            
            inputs = processor(
                text=text,
                reference_text=ref_text,
                reference_audio=reference_wav,
                return_tensors="pt"
            ).to(device)
        else:
            print("[>>] Audio8 preset mode (no reference voice)")
            inputs = processor(
                text=text,
                return_tensors="pt"
            ).to(device)
            
        with torch.no_grad():
            output = model.generate(
                **inputs,
                max_new_tokens=1024,
                temperature=0.8,
                top_p=0.95,
                top_k=50,
                do_sample=True,
                return_dict_in_generate=True
            )
            waveforms, waveform_lengths = model.decode_audio(output.codes)
            
        audio = waveforms[0, : int(waveform_lengths[0])].float().cpu().numpy()
        sample_rate = model.config.codec_sample_rate if hasattr(model.config, "codec_sample_rate") else 44100
        sf.write(output_path, audio, sample_rate)
        return os.path.exists(output_path) and os.path.getsize(output_path) > 1000
    except Exception as e:
        print(f"[!] Audio8 synthesis failed: {e}")
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


def preprocess_tts_text(text: str) -> str:
    """
    Preprocess text to improve neural TTS pronunciation, pauses, and emphasis.
    """
    if not text:
        return text

    import re

    # 1. Custom pause tags: convert [pause], [break], <pause>, <break> to ellipses
    text = text.replace("[pause]", "...").replace("[break]", "...")
    text = text.replace("<pause>", "...").replace("<break>", "...")

    # 2. Convert markdown bolding (**word**) and italics (*word*) to capitalized (WORD) for neural stress
    def make_caps(match):
        return match.group(1).upper()
    text = re.sub(r"\*\*([^*]+)\*\*", make_caps, text)
    text = re.sub(r"\*([^*]+)\*", make_caps, text)

    # 3. Custom Pronunciation Dictionary for technical acronyms (prevents incorrect pronunciation)
    pronunciation_dict = {
        "TTS": "T-T-S",
        "VRAM": "V-RAM",
        "RTF": "R-T-F",
        "CPU": "C-P-U",
        "GPU": "G-P-U",
    }
    
    # Replace whole words only (case-sensitive)
    for word, phonetic in pronunciation_dict.items():
        pattern = r"\b" + re.escape(word) + r"\b"
        text = re.sub(pattern, phonetic, text)

    return text


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
    text = preprocess_tts_text(text)
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

        # 0. Audio8-TTS (If selected)
        if not success and model_id == "audio8":
            print(f"[>>] Trying Audio8-TTS zero-shot cloning...")
            success = _synthesize_audio8(text, reference_voice, output_path)
            if success:
                backend_used = "audio8-clone"
                cloning_active = True
                print(f"[OK] Audio8-TTS cloning succeeded — speaking in YOUR voice")

        # 1. Chatterbox TTS
        if not success and _chatterbox_available() and model_id != "audio8":
            print(f"[>>] Trying Chatterbox TTS zero-shot cloning...")
            success = _synthesize_chatterbox_clone(text, reference_voice, output_path)
            if success:
                backend_used = "chatterbox-clone"
                cloning_active = True
                print(f"[OK] Chatterbox cloning succeeded — speaking in YOUR voice")

        # 2. F5-TTS
        if not success and _f5tts_available() and model_id != "audio8":
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

        # 0. Audio8-TTS (If selected)
        if not success and model_id == "audio8":
            print(f"[>>] Trying Audio8-TTS preset mode...")
            success = _synthesize_audio8(text, None, output_path)
            if success:
                backend_used = "audio8-preset"
                print(f"[OK] Audio8-TTS preset synthesis succeeded")

        # 1. Kokoro-82M
        if not success and _kokoro_available() and model_id != "audio8":
            success = _synthesize_kokoro(text, voice_id, output_path)
            if success:
                backend_used = "kokoro"
                print(f"[OK] Kokoro preset succeeded (voice: {voice_id})")

        # 2. Chatterbox default (no reference)
        if not success and _chatterbox_available() and model_id != "audio8":
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
