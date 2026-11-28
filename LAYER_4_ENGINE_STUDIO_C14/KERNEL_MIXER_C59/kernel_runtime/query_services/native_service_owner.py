"""Own native Workbench and lifecycle operations for one Project."""

from __future__ import annotations

from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    ATOM_LIFECYCLE.NATIVE_LIFECYCLE.\
    NATIVE_LIFECYCLE__shared import (
    LIFECYCLE_TOOLS,
    execute_native_lifecycle,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.RUNTIME_SUPPORT.\
    RUNTIME_SUPPORT__shared import (
    bind_native_runtime,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    structure.structure__shared import (
        read_structure,
    )  # fmt: skip

from ...atom_document import atom_document
from ...errors import WorkbenchUnavailableError
from .native_query_runtime import NativeQueryRuntime


class NativeQueryOwner(NativeQueryRuntime):
    def atom_document(self, ref_id: str) -> dict[str, Any]:
        with self._interface_lock:
            store = self._owner()
            if (
                self._capture is None
                or self._projection_selection != self.selection
                or self._manifest_needs_reload(self._capture)
            ):
                raise WorkbenchUnavailableError(
                    "Project capture is unavailable"
                )
            return atom_document(self._root, store, self._capture, ref_id)

    def lifecycle(
        self, name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        if name not in LIFECYCLE_TOOLS:
            raise ValueError("The native Atom Lifecycle Tool is unavailable")
        with self._interface_lock, bind_native_runtime(self.selection):
            store = self._owner()
            assert self._capture is not None
            previous = (
                self._capture
                if self._projection_selection == self.selection
                else None
            )
            if self._manifest_needs_reload(previous):
                return {
                    "outcome": "blocked",
                    "errors": [
                        {
                            "code": "project_manifest_reload_required",
                            "message": (
                                "Project Manifest differs from startup pin "
                                f"{self.selection.manifest_ref}. "
                                "Restart MCP to load the current Manifest."
                            ),
                        }
                    ],
                }
            outcome = execute_native_lifecycle(
                self.selection,
                name,
                arguments,
                self._capture,
                read_structure,
                previous_capture=previous,
                ticket_labels=self._inputs.ticket_labels,
                validate_project_spec=self._inputs.validate_project_spec,
            )
            self._refresh_lifecycle_outcome(store, outcome)
            return outcome

    def _refresh_lifecycle_outcome(self, store, outcome):
        if outcome.get("effects"):
            try:
                self._refresh_after_write(store, outcome["effects"])
            except Exception:
                outcome["outcome"] = "failed"
                outcome.setdefault("errors", []).append(
                    {
                        "code": "projection_refresh_failed",
                        "message": (
                            "Workbench could not refresh after the Atom "
                            "Lifecycle effect. Restart required."
                        ),
                    }
                )
