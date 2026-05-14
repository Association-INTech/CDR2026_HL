from __future__ import annotations

import logging
from pathlib import Path

_LOGGING_CONFIGURED = False


def setup_logging(log_filename: str = "py_trees.log") -> Path:
    """Configure application logging to write both to console and to a file."""
    global _LOGGING_CONFIGURED

    log_dir = Path(__file__).resolve().parents[1] / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    if _LOGGING_CONFIGURED:
        return log_dir

    log_file = log_dir / log_filename
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(),
        ],
        force=True,
    )
    
    logging.getLogger("hokuyo").setLevel(logging.WARNING)
    
    _LOGGING_CONFIGURED = True
    return log_dir