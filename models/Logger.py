import logging
from logging import handlers

# Logger class to log to console instead of print, no need log file


class Logger:
    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger
