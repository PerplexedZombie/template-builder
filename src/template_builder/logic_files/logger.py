# -*- coding: utf-8 -*-
"""Module for logging."""
import sys
from datetime import datetime
from pathlib import Path

from loguru import logger


def setup_logger(log_path: Path):
    """Create logger."""
    log_name: str = (f'template-builder__{datetime.strftime(datetime.now(), "%F")}'
                     '_run_log.log')
    log_file: str = log_path.joinpath(log_name).as_posix()
    logger.remove()
    logger.add(sys.stderr, level='INFO')
    logger.add(log_file, level='TRACE')
