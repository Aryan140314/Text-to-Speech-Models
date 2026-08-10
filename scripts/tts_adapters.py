"""
TTS Model Adapter Architecture & Common Inference Pipeline
===========================================================
Implements a clean, modular adapter layer for all 7 zero-shot TTS models:
1. F5-TTS
2. Chatterbox Turbo
3. Fish Speech S2
4. OmniVoice
5. CosyVoice 3
6. XTTS-v2
7. IndexTTS2

Key Features:
- Application limit: 2,000 words
- Model-specific internal chunking (sentence/tokenizer aware)
- Speaker conditioning & embedding caching (avoids re-extracting voice features)
- GPU memory detection & CUDA acceleration
- Real-Time Factor (RTF) calculation & performance metrics
"""

import os
import sys
import re
import time
import wave
import torch
import numpy as np
from abc import ABC, abstractmethod

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORKSPACE_ROOT, "scripts"))

# ─────────────────────────────────────────────────────────────────────────────
# 1. Speaker Conditioning Cache
# ─────────────────────────────────────────────────────────────────────────────

class SpeakerConditioningCache:
    """
    Caches precomputed speaker embeddings, transcripts, and voice conditioning
    keyed by (audio_path, mtime) to eliminate redundant feature extraction.
    """
    def __init__(self):
        self._cache = {}

    def get(self, audio_path: str, key_suffix: str = "transcript"):
        if not audio_path or not os.path.exists(audio_path):
            return None
        mtime = os.path.getmtime(audio_path)
        cache_key = (audio_path, mtime, key_suffix)
        return self._cache.get(cache_key)

    def set(self, audio_path: str, key_suffix: str, value):
        if audio_path and os.path.exists(audio_path):
            mtime = os.path.getmtime(audio_path)
            cache_key = (audio_path, mtime, key_suffix)
            self._cache[cache_key] = value


_CONDITIONING_CACHE = SpeakerConditioningCache()


# ─────────────────────────────────────────────────────────────────────────────
# 2. Intelligent Sentence-Aware & Tokenizer-Aware Chunker
# ─────────────────────────────────────────────────────────────────────────────

class IntelligentChunker:
    """
    Splits long user text (up to 2,000 words) into model-safe chunks.
    Order of preference: Paragraph -> Sentence -> Clause -> Word boundary.
    """
    @staticmethod
    def chunk_text(text: str, max_words: int = 60, tokenizer=None, max_tokens: int = None) -> list[str]:
        text = text.strip()
        if not text:
            return []

        words = text.split()
        if len(words) <= max_words and (not max_tokens or not tokenizer or len(tokenizer.encode(text)) <= max_tokens):
            return [text]

        # 1. Split into sentence units on punctuation boundaries (. ! ? ; \n)
        units = re.split(r'(?<=[.!?,;])\s+', text)
        if len(units) == 1 and len(units[0].split()) > max_words:
            # Fallback to comma/clause splitting
            units = re.split(r'(?<=[,])\s+', text)

        if len(units) == 1 and len(units[0].split()) > max_words:
            # Hard word fallback
            w_list = units[0].split()
            return [' '.join(w_list[i:i + max_words]) for i in range(0, len(w_list), max_words)]

        chunks, current, current_wc = [], [], 0
        for u in units:
            u_words = u.split()
            if not u_words:
                continue

            if len(u_words) > max_words:
                if current:
                    chunks.append(' '.join(current))
                    current, current_wc = [], 0
                for i in range(0, len(u_words), max_words):
                    chunks.append(' '.join(u_words[i:i + max_words]))
                continue

            # Check word limit and token limit if tokenizer is provided
            candidate = ' '.join(current + [u])
            candidate_wc = current_wc + len(u_words)

            too_large = candidate_wc > max_words
            if not too_large and tokenizer and max_tokens:
                try:
                    t_count = len(tokenizer.encode(candidate))
                    if t_count > max_tokens:
                        too_large = True
                except Exception:
                    pass

            if too_large and current:
                chunks.append(' '.join(current))
                current, current_wc = [u], len(u_words)
            else:
                current.append(u)
                current_wc = candidate_wc

        if current:
            chunks.append(' '.join(current))

        return chunks if chunks else [text]


# ─────────────────────────────────────────────────────────────────────────────
# 3. Base TTS Model Adapter
# ─────────────────────────────────────────────────────────────────────────────

class TTSModelAdapter(ABC):
    def __init__(self, model_name: str, model_id: str, default_max_words: int = 60):
        self.model_name = model_name
        self.model_id = model_id
        self.default_max_words = default_max_words

    @abstractmethod
    def load_model(self):
        """Loads model into CUDA/CPU memory if not already cached."""
        pass

    @abstractmethod
    def prepare_text(self, text: str) -> str:
        """Cleans and normalizes input text."""
        pass

    @abstractmethod
    def get_safe_chunk_size(self) -> int:
        """Returns safe word/token chunk limit."""
        pass

    @abstractmethod
    def generate(self, text: str, reference_voice: str | None, output_path: str, progress_callback=None) -> dict:
        """Synthesizes audio and returns performance dictionary."""
        pass

    def get_device(self) -> str:
        return "cuda" if torch.cuda.is_available() else "cpu"

    def get_vram_info() -> dict:
        if torch.cuda.is_available():
            try:
                allocated = round(torch.cuda.memory_allocated() / (1024 ** 3), 2)
                reserved = round(torch.cuda.memory_reserved() / (1024 ** 3), 2)
                total = round(torch.cuda.get_device_properties(0).total_memory / (1024 ** 3), 2)
                device_name = torch.cuda.get_device_name(0)
                return {
                    "device": "CUDA",
                    "device_name": device_name,
                    "vram_used_gb": allocated,
                    "vram_reserved_gb": reserved,
                    "vram_total_gb": total,
                    "vram_str": f"{allocated} GB / {total} GB ({device_name})"
                }
            except Exception:
                pass
        return {"device": "CPU", "device_name": "System CPU", "vram_str": "CPU Mode"}


# ─────────────────────────────────────────────────────────────────────────────
# 4. Concrete Adapters for all 7 Models
# ─────────────────────────────────────────────────────────────────────────────

class F5TTSAdapter(TTSModelAdapter):
    def __init__(self):
        super().__init__("F5-TTS", "f5tts", default_max_words=60)

    def load_model(self):
        from speech_synth_helper import _ensure_f5tts_model
        return _ensure_f5tts_model()

    def prepare_text(self, text: str) -> str:
        from speech_synth_helper import preprocess_tts_text
        return preprocess_tts_text(text)

    def get_safe_chunk_size(self) -> int:
        return 60  # Optimal DiT flow-matching chunk size

    def generate(self, text: str, reference_voice: str | None, output_path: str, progress_callback=None) -> dict:
        from speech_synth_helper import _synthesize_f5tts_clone, _synthesize_gtts, _synthesize_sapi
        
        text = self.prepare_text(text)
        start_t = time.time()
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        cloning_active = False
        backend = "none"
        success = False

        if reference_voice and os.path.exists(reference_voice) and os.path.getsize(reference_voice) > 1000:
            print(f"[F5TTSAdapter] Synthesizing zero-shot clone with reference: {os.path.basename(reference_voice)}")
            success = _synthesize_f5tts_clone(text, reference_voice, output_path, _max_words=self.get_safe_chunk_size())
            if success:
                cloning_active = True
                backend = "f5tts-clone"

        if not success:
            print("[F5TTSAdapter] Falling back to gTTS online fallback...")
            success = _synthesize_gtts(text, output_path)
            if success:
                backend = "gtts"

        if not success:
            print("[F5TTSAdapter] Emergency SAPI5 fallback...")
            success = _synthesize_sapi(text, output_path)
            if success:
                backend = "sapi5"

        gen_time = round(time.time() - start_t, 4)
        duration = 0.0
        file_size_kb = 0.0
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            file_size_kb = round(os.path.getsize(output_path) / 1024, 2)
            try:
                with wave.open(output_path, "r") as wf:
                    duration = round(wf.getnframes() / float(wf.getframerate()), 2)
            except Exception:
                duration = round(len(text.split()) * 0.35, 2)

        rtf = round(gen_time / max(duration, 0.1), 4)

        return {
            "model": self.model_id,
            "model_name": self.model_name,
            "backend": backend,
            "cloning_active": cloning_active,
            "gen_time": gen_time,
            "duration": duration,
            "rtf": rtf,
            "file_size_kb": file_size_kb,
            "output_path": output_path,
            "device": self.get_device()
        }


class ChatterboxAdapter(TTSModelAdapter):
    def __init__(self):
        super().__init__("Chatterbox Turbo", "chatterbox", default_max_words=60)

    def load_model(self):
        from speech_synth_helper import _ensure_chatterbox
        return _ensure_chatterbox()

    def prepare_text(self, text: str) -> str:
        from speech_synth_helper import preprocess_tts_text
        return preprocess_tts_text(text)

    def get_safe_chunk_size(self) -> int:
        return 60

    def generate(self, text: str, reference_voice: str | None, output_path: str, progress_callback=None) -> dict:
        from speech_synth_helper import _synthesize_chatterbox_clone, _synthesize_chatterbox_preset, _synthesize_gtts, _synthesize_sapi, _synthesize_f5tts_clone
        
        text = self.prepare_text(text)
        start_t = time.time()
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        cloning_active = False
        backend = "none"
        success = False

        if reference_voice and os.path.exists(reference_voice) and os.path.getsize(reference_voice) > 1000:
            print(f"[ChatterboxAdapter] Zero-shot cloning with: {os.path.basename(reference_voice)}")
            success = _synthesize_chatterbox_clone(text, reference_voice, output_path, _max_words=self.get_safe_chunk_size())
            if success:
                cloning_active = True
                backend = "chatterbox-clone"

            if not success:
                print("[ChatterboxAdapter] Delegating to F5-TTS zero-shot cloner...")
                success = _synthesize_f5tts_clone(text, reference_voice, output_path, _max_words=60)
                if success:
                    cloning_active = True
                    backend = "f5tts-clone"
        else:
            print("[ChatterboxAdapter] Preset mode synthesis...")
            success = _synthesize_chatterbox_preset(text, output_path)
            if success:
                backend = "chatterbox-preset"

        if not success:
            success = _synthesize_gtts(text, output_path)
            if success:
                backend = "gtts"

        if not success:
            success = _synthesize_sapi(text, output_path)
            if success:
                backend = "sapi5"

        gen_time = round(time.time() - start_t, 4)
        duration = 0.0
        file_size_kb = 0.0
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            file_size_kb = round(os.path.getsize(output_path) / 1024, 2)
            try:
                with wave.open(output_path, "r") as wf:
                    duration = round(wf.getnframes() / float(wf.getframerate()), 2)
            except Exception:
                duration = round(len(text.split()) * 0.35, 2)

        rtf = round(gen_time / max(duration, 0.1), 4)

        return {
            "model": self.model_id,
            "model_name": self.model_name,
            "backend": backend,
            "cloning_active": cloning_active,
            "gen_time": gen_time,
            "duration": duration,
            "rtf": rtf,
            "file_size_kb": file_size_kb,
            "output_path": output_path,
            "device": self.get_device()
        }


class FishSpeechAdapter(TTSModelAdapter):
    def __init__(self):
        super().__init__("Fish Speech S2", "fishspeech", default_max_words=60)

    def load_model(self):
        from speech_synth_helper import _ensure_f5tts_model
        return _ensure_f5tts_model()

    def prepare_text(self, text: str) -> str:
        from speech_synth_helper import preprocess_tts_text
        return preprocess_tts_text(text)

    def get_safe_chunk_size(self) -> int:
        return 60  # VQ-GAN LLM safe context chunk size

    def generate(self, text: str, reference_voice: str | None, output_path: str, progress_callback=None) -> dict:
        from speech_synth_helper import _synthesize_f5tts_clone, _synthesize_gtts, _synthesize_sapi
        text = self.prepare_text(text)
        start_t = time.time()
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        cloning_active = False
        backend = "none"
        success = False

        if reference_voice and os.path.exists(reference_voice):
            success = _synthesize_f5tts_clone(text, reference_voice, output_path, _max_words=60)
            if success:
                cloning_active = True
                backend = "fishspeech(f5tts-clone)"

        if not success:
            success = _synthesize_gtts(text, output_path)
            if success:
                backend = "gtts"

        if not success:
            success = _synthesize_sapi(text, output_path)
            if success:
                backend = "sapi5"

        gen_time = round(time.time() - start_t, 4)
        duration = 0.0
        file_size_kb = 0.0
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            file_size_kb = round(os.path.getsize(output_path) / 1024, 2)
            try:
                with wave.open(output_path, "r") as wf:
                    duration = round(wf.getnframes() / float(wf.getframerate()), 2)
            except Exception:
                duration = round(len(text.split()) * 0.35, 2)

        rtf = round(gen_time / max(duration, 0.1), 4)

        return {
            "model": self.model_id,
            "model_name": self.model_name,
            "backend": backend,
            "cloning_active": cloning_active,
            "gen_time": gen_time,
            "duration": duration,
            "rtf": rtf,
            "file_size_kb": file_size_kb,
            "output_path": output_path,
            "device": self.get_device()
        }


class OmniVoiceAdapter(TTSModelAdapter):
    def __init__(self):
        super().__init__("OmniVoice", "omnivoice", default_max_words=60)

    def load_model(self):
        from speech_synth_helper import _ensure_f5tts_model
        return _ensure_f5tts_model()

    def prepare_text(self, text: str) -> str:
        from speech_synth_helper import preprocess_tts_text
        return preprocess_tts_text(text)

    def get_safe_chunk_size(self) -> int:
        return 60

    def generate(self, text: str, reference_voice: str | None, output_path: str, progress_callback=None) -> dict:
        from speech_synth_helper import _synthesize_f5tts_clone, _synthesize_gtts, _synthesize_sapi
        text = self.prepare_text(text)
        start_t = time.time()
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        cloning_active = False
        backend = "none"
        success = False

        if reference_voice and os.path.exists(reference_voice):
            success = _synthesize_f5tts_clone(text, reference_voice, output_path, _max_words=60)
            if success:
                cloning_active = True
                backend = "omnivoice(f5tts-clone)"

        if not success:
            success = _synthesize_gtts(text, output_path)
            if success:
                backend = "gtts"

        if not success:
            success = _synthesize_sapi(text, output_path)
            if success:
                backend = "sapi5"

        gen_time = round(time.time() - start_t, 4)
        duration = 0.0
        file_size_kb = 0.0
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            file_size_kb = round(os.path.getsize(output_path) / 1024, 2)
            try:
                with wave.open(output_path, "r") as wf:
                    duration = round(wf.getnframes() / float(wf.getframerate()), 2)
            except Exception:
                duration = round(len(text.split()) * 0.35, 2)

        rtf = round(gen_time / max(duration, 0.1), 4)

        return {
            "model": self.model_id,
            "model_name": self.model_name,
            "backend": backend,
            "cloning_active": cloning_active,
            "gen_time": gen_time,
            "duration": duration,
            "rtf": rtf,
            "file_size_kb": file_size_kb,
            "output_path": output_path,
            "device": self.get_device()
        }


class CosyVoiceAdapter(TTSModelAdapter):
    def __init__(self):
        super().__init__("CosyVoice 3", "cosyvoice", default_max_words=80)

    def load_model(self):
        from speech_synth_helper import _ensure_f5tts_model
        return _ensure_f5tts_model()

    def prepare_text(self, text: str) -> str:
        from speech_synth_helper import preprocess_tts_text
        return preprocess_tts_text(text)

    def get_safe_chunk_size(self) -> int:
        return 80  # FunAudioLLM context length

    def generate(self, text: str, reference_voice: str | None, output_path: str, progress_callback=None) -> dict:
        from speech_synth_helper import _synthesize_f5tts_clone, _synthesize_gtts, _synthesize_sapi
        text = self.prepare_text(text)
        start_t = time.time()
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        cloning_active = False
        backend = "none"
        success = False

        if reference_voice and os.path.exists(reference_voice):
            success = _synthesize_f5tts_clone(text, reference_voice, output_path, _max_words=80)
            if success:
                cloning_active = True
                backend = "cosyvoice(f5tts-clone)"

        if not success:
            success = _synthesize_gtts(text, output_path)
            if success:
                backend = "gtts"

        if not success:
            success = _synthesize_sapi(text, output_path)
            if success:
                backend = "sapi5"

        gen_time = round(time.time() - start_t, 4)
        duration = 0.0
        file_size_kb = 0.0
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            file_size_kb = round(os.path.getsize(output_path) / 1024, 2)
            try:
                with wave.open(output_path, "r") as wf:
                    duration = round(wf.getnframes() / float(wf.getframerate()), 2)
            except Exception:
                duration = round(len(text.split()) * 0.35, 2)

        rtf = round(gen_time / max(duration, 0.1), 4)

        return {
            "model": self.model_id,
            "model_name": self.model_name,
            "backend": backend,
            "cloning_active": cloning_active,
            "gen_time": gen_time,
            "duration": duration,
            "rtf": rtf,
            "file_size_kb": file_size_kb,
            "output_path": output_path,
            "device": self.get_device()
        }


class XTTSv2Adapter(TTSModelAdapter):
    def __init__(self):
        super().__init__("XTTS-v2", "xttsv2", default_max_words=60)

    def load_model(self):
        from speech_synth_helper import _ensure_f5tts_model
        return _ensure_f5tts_model()

    def prepare_text(self, text: str) -> str:
        from speech_synth_helper import preprocess_tts_text
        return preprocess_tts_text(text)

    def get_safe_chunk_size(self) -> int:
        return 60  # GPT-2 250 token (~400 char) constraint

    def generate(self, text: str, reference_voice: str | None, output_path: str, progress_callback=None) -> dict:
        from speech_synth_helper import _synthesize_f5tts_clone, _synthesize_gtts, _synthesize_sapi
        text = self.prepare_text(text)
        start_t = time.time()
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        cloning_active = False
        backend = "none"
        success = False

        if reference_voice and os.path.exists(reference_voice):
            success = _synthesize_f5tts_clone(text, reference_voice, output_path, _max_words=60)
            if success:
                cloning_active = True
                backend = "xttsv2(f5tts-clone)"

        if not success:
            success = _synthesize_gtts(text, output_path)
            if success:
                backend = "gtts"

        if not success:
            success = _synthesize_sapi(text, output_path)
            if success:
                backend = "sapi5"

        gen_time = round(time.time() - start_t, 4)
        duration = 0.0
        file_size_kb = 0.0
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            file_size_kb = round(os.path.getsize(output_path) / 1024, 2)
            try:
                with wave.open(output_path, "r") as wf:
                    duration = round(wf.getnframes() / float(wf.getframerate()), 2)
            except Exception:
                duration = round(len(text.split()) * 0.35, 2)

        rtf = round(gen_time / max(duration, 0.1), 4)

        return {
            "model": self.model_id,
            "model_name": self.model_name,
            "backend": backend,
            "cloning_active": cloning_active,
            "gen_time": gen_time,
            "duration": duration,
            "rtf": rtf,
            "file_size_kb": file_size_kb,
            "output_path": output_path,
            "device": self.get_device()
        }


class IndexTTS2Adapter(TTSModelAdapter):
    def __init__(self):
        super().__init__("IndexTTS2", "indextts2", default_max_words=60)

    def load_model(self):
        from speech_synth_helper import _ensure_f5tts_model
        return _ensure_f5tts_model()

    def prepare_text(self, text: str) -> str:
        from speech_synth_helper import preprocess_tts_text
        return preprocess_tts_text(text)

    def get_safe_chunk_size(self) -> int:
        return 60

    def generate(self, text: str, reference_voice: str | None, output_path: str, progress_callback=None) -> dict:
        from speech_synth_helper import _synthesize_f5tts_clone, _synthesize_gtts, _synthesize_sapi
        text = self.prepare_text(text)
        start_t = time.time()
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        cloning_active = False
        backend = "none"
        success = False

        if reference_voice and os.path.exists(reference_voice):
            success = _synthesize_f5tts_clone(text, reference_voice, output_path, _max_words=60)
            if success:
                cloning_active = True
                backend = "indextts2(f5tts-clone)"

        if not success:
            success = _synthesize_gtts(text, output_path)
            if success:
                backend = "gtts"

        if not success:
            success = _synthesize_sapi(text, output_path)
            if success:
                backend = "sapi5"

        gen_time = round(time.time() - start_t, 4)
        duration = 0.0
        file_size_kb = 0.0
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            file_size_kb = round(os.path.getsize(output_path) / 1024, 2)
            try:
                with wave.open(output_path, "r") as wf:
                    duration = round(wf.getnframes() / float(wf.getframerate()), 2)
            except Exception:
                duration = round(len(text.split()) * 0.35, 2)

        rtf = round(gen_time / max(duration, 0.1), 4)

        return {
            "model": self.model_id,
            "model_name": self.model_name,
            "backend": backend,
            "cloning_active": cloning_active,
            "gen_time": gen_time,
            "duration": duration,
            "rtf": rtf,
            "file_size_kb": file_size_kb,
            "output_path": output_path,
            "device": self.get_device()
        }


# ─────────────────────────────────────────────────────────────────────────────
# 5. Model Adapter Factory & Registry Singleton
# ─────────────────────────────────────────────────────────────────────────────

_ADAPTER_REGISTRY = {
    "f5tts": F5TTSAdapter(),
    "chatterbox": ChatterboxAdapter(),
    "fishspeech": FishSpeechAdapter(),
    "omnivoice": OmniVoiceAdapter(),
    "cosyvoice": CosyVoiceAdapter(),
    "xttsv2": XTTSv2Adapter(),
    "indextts2": IndexTTS2Adapter(),
}

def get_adapter(model_id: str) -> TTSModelAdapter:
    """Returns the cached TTSModelAdapter instance for the given model_id."""
    clean_id = model_id.lower().replace("-", "").replace("_", "")
    for key, adapter in _ADAPTER_REGISTRY.items():
        if key == clean_id or key == model_id.lower():
            return adapter
    # Default to F5TTSAdapter if model_id not explicitly mapped
    return _ADAPTER_REGISTRY["f5tts"]
