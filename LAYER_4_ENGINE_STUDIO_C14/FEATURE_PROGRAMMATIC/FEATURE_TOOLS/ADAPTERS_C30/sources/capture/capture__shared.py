"""Entry points for this Adapter package."""

from .indexed_lifecycle_capture import (
    capture_indexed_lifecycle as capture_indexed_lifecycle,
)
from .native_capture_changes import (
    _issue as _issue,
)
from .native_capture_types import (
    NativeCapture as NativeCapture,
    _preserve_capture_data as _preserve_capture_data,
)
