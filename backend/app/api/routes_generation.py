"""
API Routes for Speech Synthesis Jobs & Status Polling
"""

from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from backend.app.schemas.generation import GenerationRequest, GenerationStatusResponse
from backend.app.services.generation_service import generation_service
import os

router = APIRouter(prefix="/api/generation", tags=["Generation"])

@router.post("", response_model=GenerationStatusResponse)
def create_generation_job(req: GenerationRequest):
    words = len(req.text.strip().split()) if req.text.strip() else 0
    if words > 2000:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum limit: 2,000 words. Current input: {words} words. Please reduce text before generating audio."
        )

    task_id = generation_service.submit_generation_job(req)
    status = generation_service.get_job_status(task_id)
    return status

@router.get("/{task_id}/status", response_model=GenerationStatusResponse)
def get_job_status(task_id: str):
    status = generation_service.get_job_status(task_id)
    if not status:
        raise HTTPException(status_code=4404, detail="Task ID not found")
    return status

@router.get("/audio/file")
def get_audio_file(path: str):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(path, media_type="audio/wav")
