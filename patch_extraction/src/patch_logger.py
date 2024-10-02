# src/patch_logger.py

import logging
from pathlib import Path

def setup_logging(log_level: str = 'INFO', log_file: str = 'logs/patch_extraction.log') -> logging.Logger:
    Path("logs").mkdir(exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)
