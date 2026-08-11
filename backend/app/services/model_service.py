"""
TTS Model Manager Service
Handles model capabilities, loading, unloading, and active model state.
"""

import json
import os
from backend.app.core.config import config
from backend.app.services.hardware_service import hardware_service

class ModelService:
    def __init__(self):
        self.active_model_id = "f5tts"
        self.loaded_models = set()

    def get_all_models((self) -> list:
        models_data = []
        if os.path.exists(config.models_config_path):
            try:
                with open(config.models_config_path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                    for m_id, m_info in raw.items():
                        models_data.append({
                            "id": m_id,
                            "name": m_info.get("name", m_id),
                            "architecture": m_info.get("architecture", "Neural TTS"),
                            "supports_cloning": m_info.get("supports_cloning", True),
                            "default_sample_rate": m_info.get("default_sample_rate", 24000),
                            "vram_required_gb": 4.0,
                            "installed": True,
                            "loaded": (m_id in self.loaded_models),
                            "device": "cuda" if hardware_service.inspect_hardware()["cuda"]["available"] else "cpu"
                        })
            except Exception as e:
                print(f"[!] Error reading models_config.json: {e}")

        if not models_data:
            # Fallback model list
            defaults = [
                ("f5tts", "F5-TTS", "Non-Autoregressive Flow Matching"),
                ("chatterbox", "Chatterbox Turbo", "Zero-Shot Diffusion"),
                ("fishspeech", "Fish Speech S2", "44.1kHz VQ-GAN Codec"),
                ("omnivoice", "OmniVoice", "Expressive Audio LM"),
                ("cosyvoice", "CosyVoice 3", "FunAudioLLM Engine"),
                ("xttsv2", "XTTS-v2", "Coqui Multilingual"),
                ("indextts2", "IndexTTS2", "Acoustic Retrieval"),
            ]
            for m_id, name, arch in defaults:
                models_data.append({
                    "id": m_id,
                    "name": name,
                    "architecture": arch,
                    "supports_cloning": True,
                    "default_sample_rate": 24000,
                    "vram_required_gb": 4.0,
                    "installed": True,
                    "loaded": (m_id in self.loaded_models),
                    "device": "cuda" if hardware_service.inspect_hardware()["cuda"]["available"] else "cpu"
                })

        return models_data

    def load_model(self, model_id: str, device: str = "cuda") -> dict:
        from backend.tts.adapters.tts_adapters import get_adapter
        adapter = get_adapter(model_id)
        adapter.load_model()
        self.active_model_id = model_id
        self.loaded_models.add(model_id)
        return {
            "model_id": model_id,
            "status": "success",
            "message": f"Model {adapter.model_name} loaded successfully on {adapter.get_device()}",
            "device": adapter.get_device()
        }

model_service = ModelService()
