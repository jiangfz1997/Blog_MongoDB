# src/logger.py
import logging
import sys
from pathlib import Path
from logging import handlers
from pythonjsonlogger import jsonlogger

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_LOGFILE = LOG_DIR / "app.log"

LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

def setup_logging(filename: str | Path = DEFAULT_LOGFILE, level: str = 'info', when: str = 'D', backup_count: int = 7):

    root_name = "blogapp"
    root = logging.getLogger(root_name)
    if root.handlers:
        return root

    log_level = LEVELS.get(level, logging.DEBUG)
    root.setLevel(log_level)
    root.propagate = False

    # Console handler (stdout)
    console_fmt = logging.Formatter('[%(asctime)s] %(levelname)s [%(name)s] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(console_fmt)
    root.addHandler(sh)

    # File handler (JSON) - for ELK
    json_fmt = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(filename)s %(lineno)d %(message)s')
    th = handlers.TimedRotatingFileHandler(filename=str(filename), when=when, backupCount=backup_count, encoding='utf-8')
    th.setFormatter(json_fmt)
    root.addHandler(th)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    return root

def get_logger(name: str = None):

    root_name = "blogapp"
    if not logging.getLogger(root_name).handlers:
        setup_logging(level=logging.DEBUG)
    logger = logging.getLogger(name or root_name)
    return logger

logger = get_logger()
