"""Configure safe logging at the private Backend HTTP boundary."""

from datetime import datetime, timezone
import json
import logging
import os


def runtime_log_level(default="INFO"):
    level = os.environ.get("ANECHOIC_LOG_LEVEL", default)
    if level not in ("DEBUG", "INFO", "WARNING", "ERROR"):
        raise ValueError("Invalid ANECHOIC_LOG_LEVEL")
    return level


class _HttpFormatter(logging.Formatter):
    def format(self, record):
        level = record.levelname
        outcome = "failed" if level == "ERROR" else "degraded" if level == "WARNING" else "observed"
        return json.dumps({
            "timestamp": datetime.fromtimestamp(record.created, timezone.utc).isoformat(timespec="milliseconds"),
            "severity": level, "event": "http_server_" + record.funcName.lstrip("_"),
            "component": "C70", "operation": "http_server", "outcome": outcome, "details": {},
        }, separators=(",", ":"))


def http_log_config():
    return {"version": 1, "disable_existing_loggers": False, "formatters": {"safe": {"()": _HttpFormatter}},
            "handlers": {"default": {"class": "logging.StreamHandler", "formatter": "safe",
                                     "stream": "ext://sys.stderr"}},
            "loggers": {"uvicorn": {"handlers": ["default"], "propagate": False}}}
