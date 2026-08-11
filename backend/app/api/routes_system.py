"""
API Routes for System Diagnostics & Health Inspection
"""

from fastapi import APIRouter
from backend.app.schemas.system import HardwareInfoResponse, HealthCheckResponse
from backend.app.services.hardware_service import hardware_service

router = APIRouter(prefix="/api", tags=["System"])

@router.get("/health", response_model=HealthCheckResponse)
def get_health():
    hw = hardware_service.inspect_hardware()
    return HealthCheckResponse(
        status="ok",
        app="TTS Studio Backend",
        version="1.0.0",
        device=hw["recommended_device"]
    )

@router.get("/system/hardware", response_model=HardwareInfoResponse)
def get_hardware_info():
    hw = hardware_service.inspect_hardware()
    return HardwareInfoResponse(**hw)
