# src/utils/logging_setup.py
"""Configure application-wide logging."""

import os
import logging
import logging.handlers
from typing import Optional


def setup_logging(log_dir: Optional[str] = None, log_level: int = logging.INFO) -> None:
    """Configure application-wide logging.

    Args:
        log_dir: Directory to store log files, defaults to ~/.moinsy/logs
        log_level: Logging level, defaults to INFO
    """
    if log_dir is None:
        home_dir = os.path.expanduser('~')
        log_dir = os.path.join(home_dir, '.moinsy', 'logs')

    os.makedirs(log_dir, exist_ok=True)

    # Create log file path
    log_file = os.path.join(log_dir, 'moinsy.log')

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create file handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding='utf-8'
    )

    # Create console handler
    console_handler = logging.StreamHandler()

    # Define formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Apply formatter to handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    logging.info(f"Logging initialized at level {logging.getLevelName(log_level)}")
    logging.info(f"Log file: {log_file}")