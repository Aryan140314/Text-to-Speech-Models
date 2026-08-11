"""
Pydantic Schemas for Speech Generation Jobs
"""

from typing import Optional
from pydantic import BaseModel, Field

class GenerationRequest(BaseModel):
    text: str = Field(..., max_length=2000, description="English text prompt to synthesize (Max 2,000 words)")
    model_id: str = "f5tts"
    voice_path: Optional[str] = None
    speed: float = 1.0
    pitch: float = 0.0

class GenerationStatusResponse(BaseModel):
    task_id: str
    status: str  # queued, processing, completed, failed
    progress_percent: int = 0
    message: str = ""
    model_id: str = ""
    gen_time_sec: float = 0.0
    duration_sec: float = 0.0
    rtf: float = 0.0
    file_size_kb: float = 0.0
    output_wav_path: Optional[str] = None
    device: str = "cuda"
