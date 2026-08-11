"""
API Routes for Benchmarking
"""

from fastapi import APIRouter
import time
from backend.app.schemas.benchmark import BenchmarkRunRequest, BenchmarkResponse
from backend.app.services.benchmark_service import benchmark_service

router = APIRouter(prefix="/api/benchmark", tags=["Benchmark"])

@router.post("/run", response_model=BenchmarkResponse)
def run_benchmark(req: BenchmarkRunRequest = None):
    text = req.text if req else None
    ref = req.voice_path if req else None
    m_ids = req.model_ids if req else None

    results = benchmark_service.run_benchmark(text, ref, m_ids)
    return BenchmarkResponse(
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        results=results
    )
