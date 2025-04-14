
import sys
sys.path.append("")

import os
import logging
from logging.handlers import TimedRotatingFileHandler
from src.Utils.utils import read_config

def create_logger(config_path: str = "config.yaml"):
    
    config = read_config(path=config_path)['logging']  # Assume this reads your config
    logfile = config['logfile']
    os.makedirs(os.path.dirname(logfile), exist_ok=True)

    logger = logging.getLogger('myapp')
    logger.setLevel(logging.DEBUG)
    logger.propagate = False  # Key fix to stop duplication

    if not logger.handlers:  # Only add handlers if none exist
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        rotate_handler = TimedRotatingFileHandler(
            filename=logfile, when=config['when'], backupCount=config['backupCount']
        )
        rotate_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] - Message: %(message)s'
        )
        console_handler.setFormatter(formatter)
        rotate_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.addHandler(rotate_handler)

    return logger