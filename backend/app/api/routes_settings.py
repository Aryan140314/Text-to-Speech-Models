"""
API Routes for System & App Preferences
"""

from fastapi import APIRouter
from backend.app.core.config import config
from backend.app.core.paths import paths

router = APIRouter(prefix="/api/settings", tags=["Settings"])

@router.get("")
def get_settings():
    return {
        "max_words": config.max_words,
        "default_device": config.default_device,
        "models_dir": paths.models_dir,
        "voices_dir": paths.voices_dir,
        "outputs_dir": paths.outputs_dir,
        "cache_dir": paths.cache_dir,
        "logs_dir": paths.logs_dir
    }
