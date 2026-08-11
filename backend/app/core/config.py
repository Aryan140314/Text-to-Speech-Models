"""
TTS Studio — Core Application Configuration
"""

import os
from pydantic import BaseModel
from backend.app.core.paths import paths

class AppConfig(BaseModel):
    app_name: str = "TTS Studio"
    version: str = "1.0.0"
    max_words: int = 2000
    default_device: str = "auto"
    host: str = "127.0.0.1"
    port: int = 8000
    models_config_path: str = os.path.join(paths.configs_dir, "models_config.json")
    pronunciation_map_path: str = os.path.join(paths.configs_dir, "pronunciation_map.json")

config = AppConfig()
