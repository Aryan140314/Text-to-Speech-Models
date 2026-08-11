"""
TTS Studio — FastAPI Application Entrypoint
===========================================
Local-first REST API service connecting Electron UI with core neural TTS synthesis.
"""

import sys
import os
import argparse
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, WORKSPACE_ROOT)

from backend.app.core.config import config
from backend.app.core.logging import logger
from backend.app.api.routes_system import router as system_router
from backend.app.api.routes_models import router as models_router
from backend.app.api.routes_voices import router as voices_router
from backend.app.api.routes_generation import router as generation_router
from backend.app.api.routes_benchmark import router as benchmark_router
from backend.app.api.routes_settings import router as settings_router

app = FastAPI(
    title=config.app_name,
    version=config.version,
    description="Local AI Text-to-Speech & Zero-Shot Voice Cloning Engine"
)

# CORS middleware — restricted to local origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(system_router)
app.include_router(models_router)
app.include_router(voices_router)
app.include_router(generation_router)
app.include_router(benchmark_router)
app.include_router(settings_router)

@app.on_event("startup")
def startup_event():
    logger.info(f"Starting {config.app_name} v{config.version} Local API Server...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TTS Studio Local Backend")
    parser.add_argument("--port", type=int, default=8000, help="Port to run FastAPI service on")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host IP to bind (Default: 127.0.0.1)")
    args = parser.parse_args()

    print(f"🚀 [TTS Studio Backend] Starting on http://{args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
