"""
Hardware Detection & Inspection Service
Detects CPU, System RAM, NVIDIA CUDA GPU, VRAM, and PyTorch capability dynamically.
"""

import os
import psutil
import platform
import torch

class HardwareService:
    @staticmethod
    def inspect_hardware() -> dict:
        # System RAM & CPU
        ram_bytes = psutil.virtual_memory().total
        ram_used_bytes = psutil.virtual_memory().used
        ram_total_gb = round(ram_bytes / (1024 ** 3), 2)
        ram_used_gb = round(ram_used_bytes / (1024 ** 3), 2)
        cpu_name = platform.processor() or platform.machine() or "Generic CPU"

        # GPU & CUDA Inspection
        cuda_available = torch.cuda.is_available()
        cuda_version = torch.version.cuda if cuda_available else None
        pytorch_version = torch.__version__

        gpu_info = {
            "available": False,
            "vendor": "None",
            "name": "N/A",
            "vram_total_gb": 0.0,
            "vram_used_gb": 0.0,
            "vram_reserved_gb": 0.0,
        }

        recommended_device = "cpu"

        if cuda_available:
            try:
                device_count = torch.cuda.device_count()
                if device_count > 0:
                    device_name = torch.cuda.get_device_name(0)
                    total_vram = round(torch.cuda.get_device_properties(0).total_memory / (1024 ** 3), 2)
                    allocated_vram = round(torch.cuda.memory_allocated(0) / (1024 ** 3), 2)
                    reserved_vram = round(torch.cuda.memory_reserved(0) / (1024 ** 3), 2)

                    gpu_info = {
                        "available": True,
                        "vendor": "NVIDIA",
                        "name": device_name,
                        "vram_total_gb": total_vram,
                        "vram_used_gb": allocated_vram,
                        "vram_reserved_gb": reserved_vram,
                    }
                    recommended_device = "cuda"
            except Exception as e:
                print(f"[!] Warning detecting CUDA device: {e}")

        return {
            "cpu_name": cpu_name,
            "ram_total_gb": ram_total_gb,
            "ram_used_gb": ram_used_gb,
            "gpu": gpu_info,
            "cuda": {
                "available": cuda_available,
                "version": cuda_version,
                "pytorch_version": pytorch_version,
            },
            "recommended_device": recommended_device,
        }

hardware_service = HardwareService()
