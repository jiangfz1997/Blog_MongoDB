import logging
import os
import sys
from logging import handlers
from pythonjsonlogger.json import JsonFormatter


class Logger:
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critic': logging.CRITICAL
    }

    def __init__(self, filename='./logs/app.log', level='info', when='D', backCount=3):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        self.logger = logging.getLogger(filename)
        self.logger.setLevel(self.level_relations.get(level, logging.INFO))

        if self.logger.handlers:
            return

        # print log to console
        console_fmt = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s'
        )
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(console_fmt)
        self.logger.addHandler(sh)

        # save log to json format for ELK collecting
        json_fmt = JsonFormatter(
            '{"time": "%(asctime)s", "level": "%(levelname)s", "file": "%(filename)s", "line": "%(lineno)d", '
            '"msg": "%(message)s"} '
        )
        th = handlers.TimedRotatingFileHandler(
            filename=filename, when=when, backupCount=backCount, encoding='utf-8'
        )
        th.setFormatter(json_fmt)
        self.logger.addHandler(th)
