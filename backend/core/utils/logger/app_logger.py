import json
import logging
import sys
import traceback
from backend.config.config import settings

class JsonFormatter(logging.Formatter):
    """Форматтер для вывода логов в формате JSON."""
    def __init__(self, disable_caller: bool, disable_stacktrace: bool):
        super().__init__()
        self.disable_caller = disable_caller
        self.disable_stacktrace = disable_stacktrace

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "message": record.getMessage(),
        }

        if not self.disable_caller:
            log_data["caller"] = f"{record.filename}:{record.lineno}"

        if record.exc_info and not self.disable_stacktrace:
            log_data["stacktrace"] = "".join(traceback.format_exception(*record.exc_info))
            
        return json.dumps(log_data, ensure_ascii=False)


def setup_logger():
    """Настройка легкого логгера на основе переданного yml-конфига."""
    cfg = settings.logger

    log_level = cfg.level.upper() #getattr(logging, cfg.LEVEL.upper(), logging.INFO)

    if cfg.development:
        console_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    else:
        console_format = "[%(levelname)s] %(message)s"
        
    if not cfg.disable_caller and cfg.encoding == "console":
        console_format = "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"

    if cfg.encoding == "json":
        formatter = JsonFormatter(disable_caller=cfg.disable_caller, disable_stacktrace=cfg.disable_stacktrace)
    else:
        formatter = logging.Formatter(console_format, datefmt="%Y-%m-%d %H:%M:%S")

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = [handler]

    if cfg.disable_stacktrace and cfg.encoding == "console":
        logging.raiseExceptions = False