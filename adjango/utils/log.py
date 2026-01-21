import logging
import platform
from logging.handlers import TimedRotatingFileHandler


class WindowsSafeTimedRotatingFileHandler(TimedRotatingFileHandler):
    """TimedRotatingFileHandler with Windows support - closes file before rotation."""

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None  # type: ignore[assignment]
        try:
            super().doRollover()
        except OSError:
            if platform.system() == 'Windows':
                pass
            else:
                raise


def get_global_logger() -> logging.Logger:
    """Return a logger configured with the global name."""
    return logging.getLogger('global')
