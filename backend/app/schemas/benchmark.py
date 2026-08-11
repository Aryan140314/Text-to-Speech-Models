"""
Pydantic Schemas for Multi-Model Benchmarking
"""

from typing import List, Optional
from pydantic import BaseModel

class BenchmarkResultItem(BaseModel):
    model_id: str
    model_name: str
    word_count: int
    char_count: int
    chunks: int
    device: str
    gen_time_sec: float
    audio_duration_sec: float
    rtf: float
    vram_used_mb: float = 0.0

class BenchmarkRunRequest(BaseModel):
    text: Optional[str] = None
    voice_path: Optional[str] = None
    model_ids: Optional[List[str]] = None

class BenchmarkResponse(BaseModel):
    timestamp: str
    results: List[BenchmarkResultItem]
