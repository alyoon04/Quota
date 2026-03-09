import json
import logging
import sys
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    _SKIP = frozenset({
        "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
        "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
        "created", "msecs", "relativeCreated", "thread", "threadName",
        "processName", "process", "message", "taskName", "asctime",
    })

    def format(self, record):
        obj = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            obj["exc"] = self.formatException(record.exc_info)
        for k, v in record.__dict__.items():
            if k not in self._SKIP:
                obj[k] = v
        return json.dumps(obj)


def setup_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers = [handler]
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
