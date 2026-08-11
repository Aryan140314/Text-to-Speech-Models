"""
TTS Studio — Structured Logging Setup
"""

import os
import sys
import logging
from backend.app.core.paths import paths

def setup_logging():
    log_file = os.path.join(paths.logs_dir, "backend.log")
    
    logger = logging.getLogger("tts_studio")
    logger.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s", "%Y-%m-%d %H:%M:%S")
    
    # Console Handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    
    # File Handler
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(ch)
        logger.addHandler(fh)
        
    return logger

logger = setup_logging()
