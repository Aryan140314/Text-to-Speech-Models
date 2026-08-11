"""
TTS Studio — Centralized System Path Resolver
=============================================
Resolves user data paths to %LOCALAPPDATA%\\TTS-Studio for production,
with fallback to local repository root for portable development mode.
"""

import os
import sys
import platform

APP_NAME = "TTS-Studio"

# Determine workspace repository root
DEV_WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_base_data_dir() -> str:
    """
    Returns base writable user data directory.
    Production: %LOCALAPPDATA%\\TTS-Studio (Windows) or ~/.local/share/TTS-Studio
    Development: Workspace root folder if portable dev flag set.
    """
    if os.environ.get("TTS_PORTABLE_DEV", "0") == "1":
        return DEV_WORKSPACE_ROOT

    system = platform.system()
    if system == "Windows":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            base_dir = os.path.join(local_app_data, APP_NAME)
        else:
            base_dir = os.path.expanduser(f"~\\AppData\\Local\\{APP_NAME}")
    elif system == "Darwin":
        base_dir = os.path.expanduser(f"~/Library/Application Support/{APP_NAME}")
    else:
        base_dir = os.path.expanduser(f"~/.local/share/{APP_NAME}")

    os.makedirs(base_dir, exist_ok=True)
    return base_dir


class PathManager:
    def __init__(self):
        self.base_dir = get_base_data_dir()
        
        # Core directory tree
        self.models_dir = self._init_dir("models")
        self.voices_dir = self._init_dir("voices")
        self.outputs_dir = self._init_dir("outputs")
        self.cache_dir = self._init_dir("cache")
        self.logs_dir = self._init_dir("logs")
        self.temp_dir = self._init_dir("temp")
        self.configs_dir = self._init_dir("configs")

        # Redirect Hugging Face cache to app cache dir
        os.environ["HF_HOME"] = os.path.join(self.cache_dir, "huggingface")
        os.makedirs(os.environ["HF_HOME"], exist_ok=True)

    def _init_dir(self, subfolder: str) -> str:
        # Check if local dev workspace folder has existing data
        dev_sub = os.path.join(DEV_WORKSPACE_ROOT, subfolder)
        if os.path.exists(dev_sub) and os.environ.get("TTS_PORTABLE_DEV", "1") == "1":
            return dev_sub

        target_path = os.path.join(self.base_dir, subfolder)
        os.makedirs(target_path, exist_ok=True)
        return target_path

    def get_model_output_dir(self, model_id: str) -> str:
        path = os.path.join(self.outputs_dir, model_id)
        os.makedirs(path, exist_ok=True)
        return path


# Singleton PathManager instance
paths = PathManager()
