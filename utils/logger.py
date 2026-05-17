from __future__ import annotations

import logging
from pathlib import Path


LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
LOG_LEVEL = "INFO"


def setup_logging(log_dir: Path = Path("logs"), level: str = LOG_LEVEL) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    handlers: list[logging.Handler] = [
        logging.StreamHandler(),
        logging.FileHandler(log_dir / "daily-news.log", encoding="utf-8"),
    ]
    logging.basicConfig(level=numeric_level, format=LOG_FORMAT, handlers=handlers, force=True)
