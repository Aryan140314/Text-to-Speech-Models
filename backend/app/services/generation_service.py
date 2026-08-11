"""
Asynchronous Speech Generation Service
Executes TTS synthesis using TTSModelAdapter and tracks job progress & RTF.
"""

import os
import time
import uuid
import threading
from backend.app.core.paths import paths
from backend.app.schemas.generation import GenerationRequest, GenerationStatusResponse

class GenerationService:
    def __init__(self):
        self.jobs = {}
        self.lock = threading.Lock()

    def submit_generation_job(self, req: GenerationRequest) -> str:
        task_id = str(uuid.uuid4())
        
        with self.lock:
            self.jobs[task_id] = {
                "task_id": task_id,
                "status": "queued",
                "progress_percent": 0,
                "message": "Job submitted to queue",
                "model_id": req.model_id,
                "gen_time_sec": 0.0,
                "duration_sec": 0.0,
                "rtf": 0.0,
                "file_size_kb": 0.0,
                "output_wav_path": None,
                "device": "cuda"
            }

        # Start asynchronous synthesis worker thread
        t = threading.Thread(target=self._run_synthesis_worker, args=(task_id, req), daemon=True)
        t.start()
        return task_id

    def _run_synthesis_worker(self, task_id: str, req: GenerationRequest):
        try:
            self._update_job(task_id, status="processing", progress=15, message="Preparing text and chunking...")
            
            from backend.tts.adapters.tts_adapters import get_adapter
            adapter = get_adapter(req.model_id)

            self._update_job(task_id, progress=30, message=f"Loading model adapter: {adapter.model_name}...")
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            out_dir = paths.get_model_output_dir(req.model_id)
            out_filename = f"{req.model_id}_studio_{timestamp}.wav"
            out_path = os.path.join(out_dir, out_filename)

            self._update_job(task_id, progress=50, message="Executing neural model synthesis...")
            
            res = adapter.generate(
                text=req.text,
                reference_voice=req.voice_path,
                output_path=out_path
            )

            self._update_job(task_id, progress=90, message="Finalizing audio metrics...")
            
            with self.lock:
                self.jobs[task_id].update({
                    "status": "completed",
                    "progress_percent": 100,
                    "message": "Speech synthesis completed successfully!",
                    "gen_time_sec": res.get("gen_time", 0.0),
                    "duration_sec": res.get("duration", 0.0),
                    "rtf": res.get("rtf", 0.0),
                    "file_size_kb": res.get("file_size_kb", 0.0),
                    "output_wav_path": out_path,
                    "device": res.get("device", "cuda")
                })
        except Exception as e:
            print(f"[!] Synthesis worker error: {e}")
            with self.lock:
                self.jobs[task_id].update({
                    "status": "failed",
                    "progress_percent": 0,
                    "message": f"Synthesis error: {str(e)}"
                })

    def _update_job(self, task_id: str, status=None, progress=None, message=None):
        with self.lock:
            if task_id in self.jobs:
                if status: self.jobs[task_id]["status"] = status
                if progress is not None: self.jobs[task_id]["progress_percent"] = progress
                if message: self.jobs[task_id]["message"] = message

    def get_job_status(self, task_id: str) -> GenerationStatusResponse | None:
        with self.lock:
            data = self.jobs.get(task_id)
            if data:
                return GenerationStatusResponse(**data)
            return None

generation_service = GenerationService()
