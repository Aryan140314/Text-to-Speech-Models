"""
Pydantic Schemas for Voice Profiles
"""

from typing import List, Optional
from pydantic import BaseModel

class VoiceInfo(BaseModel):
    id: str
    name: str
    genre: str = "General"
    file_path: str
    duration_sec: float = 0.0
    sample_rate: int = 22050
    file_size_kb: float = 0.0

class VoiceListResponse(BaseModel):
    voices: List[VoiceInfo]
    default_voice_id: str = ""

class VoiceCleanRequest(BaseModel):
    voice_id: str
    strength: float = 0.75

class VoiceCleanResponse(BaseModel):
    status: str
    cleaned_path: str
    message: str
