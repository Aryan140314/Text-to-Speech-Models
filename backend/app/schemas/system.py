"""
Pydantic Schemas for System & Hardware Information
"""

from typing import Optional
from pydantic import BaseModel

class GPUInfo(BaseModel):
    available: bool = False
    vendor: str = "Unknown"
    name: str = "N/A"
    vram_total_gb: float = 0.0
    vram_used_gb: float = 0.0
    vram_reserved_gb: float = 0.0

class CUDAInfo(BaseModel):
    available: bool = False
    version: Optional[str] = None
    pytorch_version: str = ""

class HardwareInfoResponse(BaseModel):
    cpu_name: str = "System CPU"
    ram_total_gb: float = 0.0
    ram_used_gb: float = 0.0
    gpu: GPUInfo
    cuda: CUDAInfo
    recommended_device: str = "cpu"

class HealthCheckResponse(BaseModel):
    status: str = "ok"
    app: str = "TTS Studio Backend"
    version: str = "1.0.0"
    device: str = "cpu"
