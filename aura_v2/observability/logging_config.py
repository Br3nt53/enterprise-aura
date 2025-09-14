import json
import logging
import os
import sys
from datetime import datetime


def configure_logging():
    level = os.getenv("AURA_LOG_LEVEL", "INFO").upper()
    handler = logging.StreamHandler(sys.stdout)

    class JsonFormatter(logging.Formatter):
        def format(self, record):
            base = {
                "ts": datetime.utcnow().isoformat() + "Z",
                "lvl": record.levelname,
                "msg": record.getMessage(),
                "logger": record.name,
            }
            if record.exc_info:
                base["exc"] = self.formatException(record.exc_info)
            return json.dumps(base)

    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]
