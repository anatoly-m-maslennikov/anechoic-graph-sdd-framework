"""Safe, transport-local process and diagnostic boundaries."""
from concurrent.futures import CancelledError
import logging
import sys


logger = logging.getLogger("anechoic.mcp.transport")


class ExplicitStartupFailure(Exception):
    """A declared failure that blocks a transport service from starting."""

    def __init__(self, code):
        self.code = code
        super().__init__(code)


def warning(code):
    """Log fixed transport codes without exposing request or exception data."""
    try:
        logger.warning("%s", code)
    except CancelledError:
        raise
    except Exception:
        return "technical diagnostic emission failed"
    return None


def run_startup(callback, *, operation):
    try:
        return callback()
    except CancelledError:
        raise
    except Exception as error:
        warning(operation + ("_blocked" if isinstance(error, ExplicitStartupFailure) else "_failed"))
        try:
            sys.stderr.write("anechoic: " + ("runtime failure" if isinstance(error, ExplicitStartupFailure) else "operation failed") + "\n")
            sys.stderr.flush()
        except Exception:
            pass
        return 2
