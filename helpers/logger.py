import logging
from colorlog import ColoredFormatter


class Logger(logging.Logger):
    def __init__(self, role: str, id: int):
        super().__init__(f"{role}-{id}")
        self.setLevel(logging.DEBUG)
        self.addHandler(self._get_console_handler())

    @staticmethod
    def _get_console_handler():
        formatter = ColoredFormatter(
            "%(log_color)s%(levelname)-8s%(reset)s %(bg_blue)s[%(name)s]%(reset)s %(message)s",
            datefmt=None,
            reset=True,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red",
            },
        )
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        return console_handler
