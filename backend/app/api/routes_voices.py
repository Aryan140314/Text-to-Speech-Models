"""
API Routes for Voice Library & DSP Dataset Cleaner
"""

from fastapi import APIRouter, HTTPException
from backend.app.schemas.voices import VoiceListResponse, VoiceCleanRequest, VoiceCleanResponse
from backend.app.services.voice_service import voice_service

router = APIRouter(prefix="/api/voices", tags=["Voices"])

@router.get("", response_model=VoiceListResponse)
def list_voices():
    voices = voice_service.get_all_voices()
    default_id = voices[0]["id"] if voices else ""
    return VoiceListResponse(
        voices=voices,
        default_voice_id=default_id
    )

@router.post("/clean", response_model=VoiceCleanResponse)
def clean_voice(req: VoiceCleanRequest):
    try:
        cleaned_path = voice_service.clean_voice(req.voice_id, strength=req.strength)
        return VoiceCleanResponse(
            status="success",
            cleaned_path=cleaned_path,
            message="Voice sample enhanced and noise-reduced successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
