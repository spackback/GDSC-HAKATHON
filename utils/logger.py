"""
Logger configuration for Cherry AI Assistant
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Dict, Any

def setup_logging(config: Dict[str, Any] = None) -> logging.Logger:
    """Setup logging configuration for Cherry"""

    if config is None:
        # Default configuration
        config = {
            'LOG_LEVEL': 'INFO',
            'LOG_FILE': 'data/logs/cherry.log',
            'MAX_LOG_FILES': 5,
            'LOGS_DIR': Path('data/logs')
        }

    # Create logs directory
    log_dir = Path(config.get('LOGS_DIR', 'data/logs'))
    log_dir.mkdir(parents=True, exist_ok=True)

    # Configure logging
    log_level = getattr(logging, config.get('LOG_LEVEL', 'INFO').upper())

    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler with rotation
    log_file = log_dir / 'cherry.log'
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=config.get('MAX_LOG_FILES', 5)
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Create Cherry logger
    cherry_logger = logging.getLogger('cherry')
    cherry_logger.info("Logging system initialized")

    return cherry_logger
