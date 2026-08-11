"""
API Routes for Model Management
"""

from fastapi import APIRouter, HTTPException
from backend.app.schemas.models import ModelListResponse, ModelLoadRequest, ModelLoadResponse
from backend.app.services.model_service import model_service

router = APIRouter(prefix="/api/models", tags=["Models"])

@router.get("", response_model=ModelListResponse)
def list_models():
    models = model_service.get_all_models()
    return ModelListResponse(
        models=models,
        active_model_id=model_service.active_model_id
    )

@router.post("/{model_id}/load", response_model=ModelLoadResponse)
def load_model(model_id: str, req: ModelLoadRequest = None):
    try:
        device = req.device if req else "cuda"
        res = model_service.load_model(model_id, device=device)
        return ModelLoadResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
