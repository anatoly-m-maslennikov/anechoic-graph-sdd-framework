"""Own native Workbench and lifecycle operations for one Project."""

from __future__ import annotations

from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import (
    LIFECYCLE_TOOLS, bind_native_runtime, execute_native_lifecycle,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    read_structure,
)

from .native_query_runtime import NativeQueryRuntime


class NativeQueryOwner(NativeQueryRuntime):
    def lifecycle(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name not in LIFECYCLE_TOOLS:
            raise ValueError("The native Atom Lifecycle Tool is unavailable")
        with self._interface_lock, bind_native_runtime(self.selection):
            store = self._owner()
            assert self._capture is not None
            previous = self._capture if self._projection_selection == self.selection else None
            if self._manifest_needs_reload(previous):
                return {
                    "outcome": "blocked",
                    "errors": [{
                        "code": "project_manifest_reload_required",
                        "message": f"Project Manifest differs from startup pin {self.selection.manifest_ref}. "
                                   "Restart MCP to load the current Manifest.",
                    }],
                }
            outcome = execute_native_lifecycle(
                self.selection, name, arguments, self._capture, read_structure,
                previous_capture=previous,
                ticket_labels=self._inputs.ticket_labels,
                validate_project_spec=self._inputs.validate_project_spec,
            )
            if outcome.get("effects"):
                try:
                    self._refresh_after_write(store, outcome["effects"])
                except Exception:
                    outcome["outcome"] = "failed"
                    outcome.setdefault("errors", []).append({
                        "code": "projection_refresh_failed",
                        "message": "Workbench could not refresh after the Atom Lifecycle effect. Restart required.",
                    })
            return outcome
