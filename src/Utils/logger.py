
import sys
sys.path.append("")

import os
import logging
from logging.handlers import TimedRotatingFileHandler
from src.Utils.utils import read_config

def create_logger(config_path:str = "config.yaml"):
    config = read_config(path = config_path)['logging']
    logfile = config['logfile']
    log_dir = os.path.dirname(logfile)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)


    when = config['when']
    backupCount = config['backupCount']
    logger = logging.getLogger()
    # Set the logging level
    logger.setLevel(logging.DEBUG)
    # Set levels for other libraries

    libraries_config = config.get('libraries', {})
    for lib, level in libraries_config.items():
        logging.getLogger(lib).setLevel(getattr(logging, level))

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    rotate_handler = TimedRotatingFileHandler(filename=logfile, when=when, backupCount=backupCount)
    rotate_handler.setLevel(logging.DEBUG)
    rotate_handler.suffix = "%Y%m%d"
        
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] - Message: %(message)s')
    rotate_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.addHandler(rotate_handler)
    return logger
