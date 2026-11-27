"""Configure safe logging at the private Kernel HTTP boundary."""

from datetime import datetime, timezone
import json
import logging


class _HttpFormatter(logging.Formatter):
    def format(self, record):
        level = record.levelname
        outcome = (
            "failed"
            if level == "ERROR"
            else "degraded"
            if level == "WARNING"
            else "observed"
        )
        return json.dumps(
            {
                "timestamp": datetime.fromtimestamp(
                    record.created, timezone.utc
                ).isoformat(timespec="milliseconds"),
                "severity": level,
                "event": "http_server_" + record.funcName.lstrip("_"),
                "component": "C71",
                "operation": "http_server",
                "outcome": outcome,
                "details": {},
            },
            separators=(",", ":"),
        )


def http_log_config():
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"safe": {"()": _HttpFormatter}},
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": "safe",
                "stream": "ext://sys.stderr",
            }
        },
        "loggers": {"uvicorn": {"handlers": ["default"], "propagate": False}},
    }
