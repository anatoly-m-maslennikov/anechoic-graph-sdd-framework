"""Serialized lifecycle worker invocation for the managed generation lane."""

import http.client
from hashlib import sha256 as sha256
import json as json
import os as os
from pathlib import Path
import signal as signal
import subprocess as subprocess
import sys as sys
from time import monotonic
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError as ValidationError,
)

from ORCHESTRATOR_beta_C68.lifecycle.lifecycle_requests import LifecycleRequests
from ORCHESTRATOR_beta_C68.lifecycle.lifecycle_execution import LifecycleExecution
from ORCHESTRATOR_beta_C68.generation.generation import admit_generation as admit_generation
from ORCHESTRATOR_beta_C68.generation.generation import read_structure as read_structure
from ORCHESTRATOR_beta_C68.jobs import (
    ENGINE as ENGINE,
    FIELDS as FIELDS,
    LifecycleCoveragePending,
    _LifecycleJob as _LifecycleJob,
    operation_timeout as operation_timeout,
)
from ORCHESTRATOR_beta_C68.lifecycle.lifecycle_queries import (
    archive_versions_available,
    lifecycle_context as lifecycle_context,
    needs_exact_archive as needs_exact_archive,
    requires_project_capture as requires_project_capture,
    ticket_allocation as ticket_allocation,
)
from ORCHESTRATOR_beta_C68.generation.worker.warm_worker import WarmLifecycleUnavailable as WarmLifecycleUnavailable
from ORCHESTRATOR_beta_C68.generation.worker.warm_worker import run_lifecycle as run_lifecycle

LIFECYCLE_DEADLINE_SECONDS = 300
LIFECYCLE_WAIT_SECONDS = 610
LIFECYCLE_TOOLS = frozenset(
    {
        "atom_lifecycle_create_draft",
        "atom_lifecycle_update",
        "atom_lifecycle_promote_draft",
        "atom_lifecycle_change_status",
        "atom_lifecycle_archive",
        "atom_lifecycle_direct_update",
        "atom_lifecycle_create_asset",
    }
)


class ArchiveHistoryPending(ValueError):
    "The operation requires more than the admitted Archive version checkpoint."


class _NativeLifecycle(BaseModel):
    model_config = ConfigDict(
        strict=True, extra="allow", hide_input_in_errors=True
    )
    outcome: str
    effects: list[Any] = Field(default_factory=list)
    warnings: list[Any] = Field(default_factory=list)
    errors: list[Any] = Field(default_factory=list)
    requested_input: dict[str, dict[str, Any]] = Field(default_factory=dict)


class _LifecycleReply(BaseModel):
    model_config = ConfigDict(
        strict=True, extra="forbid", hide_input_in_errors=True
    )
    lifecycle: _NativeLifecycle
    delta: dict[str, Any] | None
    projection_error: str | None


def _new_component_task(job):
    args = job.arguments
    if job.name != "atom_lifecycle_create_draft" or set(args) != {"newAtom"}:
        return False
    values = args["newAtom"]
    if not isinstance(values, dict) or values.get("template") not in (
        "task",
        "epic",
    ):
        return False
    container = values.get("container")
    return isinstance(container, dict) and set(container) == {"component"}


class LifecycleJobs(LifecycleRequests, LifecycleExecution):
    unconfirmed_lifecycle_write = False

    def _archive_versions_available(self):
        try:
            return archive_versions_available(
                self.database_socket, self.instance_id
            )
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            http.client.HTTPException,
        ):
            return False

    def _require_lifecycle_coverage(self, *, dispatched=False):
        "Check the queue after the epoch so newly restored coverage cannot bypass recovery."
        managed = self.thread is not None or self.watcher.observer is not None
        if managed and (
            self.watcher.capture_epoch(dispatched=dispatched) is None
            or not self.watcher.queue.empty()
        ):
            raise LifecycleCoveragePending()

    def _begin_lifecycle_write(self, job):
        with self.lock:
            deadline = job.deadline
            if (
                self.stopping.is_set()
                or self.lifecycle_job is not job
                or (deadline is not None and monotonic() >= deadline)
            ):
                return False
            self._require_lifecycle_coverage(dispatched=True)
            job.started = True
            return True

    def _acknowledge_lifecycle(self, effects, archive_epoch):
        if self.deferred_archive is not None:
            root = Path(self.binding["root"])
            self.archive_dirty |= any(
                self._is_archive_path(root / effect["target"])
                for effect in effects
            )
        self.watcher.acknowledge(effects, archive_epoch=archive_epoch)

    @staticmethod
    def _projection_failure(error):
        return {
            "state": "failed",
            "error": {
                "code": "projection_refresh_failed",
                "message": str(error)[-2048:],
            },
        }
