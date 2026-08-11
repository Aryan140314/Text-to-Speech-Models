"""
Pydantic Schemas for TTS Models
"""

from typing import List, Optional
from pydantic import BaseModel

class ModelInfo(BaseModel):
    id: str
    name: str
    architecture: str
    supports_cloning: bool = True
    default_sample_rate: int = 24000
    vram_required_gb: float = 4.0
    installed: bool = True
    loaded: bool = False
    device: str = "cuda"

class ModelListResponse(BaseModel):
    models: List[ModelInfo]
    active_model_id: str = "f5tts"

class ModelLoadRequest(BaseModel):
    device: Optional[str] = "cuda"

class ModelLoadResponse(BaseModel):
    model_id: str
    status: str
    message: str
    device: str
