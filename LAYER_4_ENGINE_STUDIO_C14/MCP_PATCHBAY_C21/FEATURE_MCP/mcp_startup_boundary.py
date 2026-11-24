"""Safe, transport-local process and diagnostic boundaries."""
from concurrent.futures import CancelledError
from datetime import datetime, timezone
import json
import logging
import os
import sys
from time import monotonic


logger = logging.getLogger("anechoic.mcp.transport")
_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")


class _Stderr(logging.Handler):
    def emit(self, record):
        if sys.stderr is not None:
            sys.stderr.write(self.format(record) + "\n")
            sys.stderr.flush()


logger.addHandler(_Stderr())
logger.setLevel(logging.DEBUG)
logger.propagate = False


def runtime_log_level():
    level = os.environ.get("ANECHOIC_LOG_LEVEL", "INFO")
    if level not in _LEVELS:
        raise ValueError("Invalid ANECHOIC_LOG_LEVEL")
    return level


class _HttpFormatter(logging.Formatter):
    def format(self, record):
        level = record.levelname
        outcome = "failed" if level == "ERROR" else "degraded" if level == "WARNING" else "observed"
        return _render(level, "http_server_" + record.funcName.lstrip("_"), "http_server", outcome, {})


def http_log_config():
    return {"version": 1, "disable_existing_loggers": False, "formatters": {"safe": {"()": _HttpFormatter}},
            "handlers": {"default": {"class": "logging.StreamHandler", "formatter": "safe",
                                     "stream": "ext://sys.stderr"}},
            "loggers": {"uvicorn": {"handlers": ["default"], "propagate": False}}}


class ExplicitStartupFailure(Exception):
    """A declared failure that blocks a transport service from starting."""

    def __init__(self, code):
        self.code = code
        super().__init__(code)


def warning(code):
    """Log fixed transport codes without exposing request or exception data."""
    return _emit("WARNING", code, "transport", "degraded")


def _emit(severity, code, operation, outcome, *, elapsed_ms=None, threshold=None):
    try:
        if _LEVELS.index(severity) < _LEVELS.index(threshold or runtime_log_level()):
            return None
        details = {} if elapsed_ms is None else {"elapsed_ms": round(elapsed_ms, 3)}
        getattr(logger, severity.lower())("%s", _render(severity, code, operation, outcome, details))
    except CancelledError:
        raise
    except Exception:
        return "technical diagnostic emission failed"
    return None


def _render(severity, code, operation, outcome, details):
    record = {"timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
              "severity": severity, "event": code, "component": "C21", "operation": operation,
              "outcome": outcome, "details": details}
    return json.dumps(record, separators=(",", ":"))


def run_startup(callback, *, operation):
    try:
        runtime_log_level()
    except ValueError:
        _emit("WARNING", "invalid_log_level", operation, "failed", threshold="INFO")
        return 2
    started = monotonic()
    _emit("INFO", operation + "_started", operation, "started")
    try:
        return callback()
    except CancelledError:
        raise
    except Exception as error:
        blocked = isinstance(error, ExplicitStartupFailure)
        severity = "WARNING" if isinstance(error, ValueError) and not blocked else "ERROR"
        _emit(severity, operation + ("_blocked" if blocked else "_failed"), operation,
              "failed", elapsed_ms=(monotonic() - started) * 1_000)
        try:
            sys.stderr.write("anechoic: " + ("runtime failure" if isinstance(error, ExplicitStartupFailure) else "operation failed") + "\n")
            sys.stderr.flush()
        except Exception:
            pass
        return 2
