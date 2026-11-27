"""Bounded, best-effort observations for one generation run."""

import hashlib
import json
import threading
import time
import uuid

from .jobs import UnixConnection
from .watcher_diagnostics import emit_record

_UNIT = {
    "path": (
        "LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68"
        "__shared.py"
    ),
    "name": "GenerationJobs._generate",
}


class Flow:
    def __init__(self, instance_id, socket_path):
        self.instance_id, self.socket_path = instance_id, socket_path
        self.run_id = uuid.uuid4().hex
        self.events = []
        self.lock = threading.Lock()
        self.omitted = 0
        self.closed = False
        self.causes = []
        self.joiners = []

    def add(
        self,
        kind,
        name,
        *,
        causes=None,
        target=None,
        outcome=None,
        detail=None,
        at=None,
    ):
        with self.lock:
            if self.closed:
                return None
            if len(self.events) >= (
                400
                if kind in {"input", "trigger"}
                else 511
                if kind == "effect"
                else 512
            ):
                self.omitted += 1
                return None
            index = len(self.events)
            if kind == "trigger":
                detail = {**(detail or {}), "unit": _UNIT}
            self.events.append(
                {
                    "kind": kind,
                    "name": name,
                    "at": time.time() if at is None else at,
                    "causes": list(self.causes if causes is None else causes),
                    "target": target,
                    "outcome": outcome,
                    "detail": detail or {},
                }
            )
            return index

    def input(self, name, *, target=None, detail=None, at=None, trigger=True):
        index = self.add(
            "input", name, causes=[], target=target, detail=detail, at=at
        )
        if index is not None:
            if not trigger:
                self.joiners.append(index)
                return index
            trigger_index = self.add(
                "trigger",
                name,
                causes=[index],
                target=target,
                detail=detail,
                at=at,
            )
            if trigger_index is not None:
                self.causes.append(trigger_index)
        return index

    def finish(self, outcome):
        detail = {
            key: outcome[key]
            for key in ("code", "delta_path_count", "kind")
            if key in outcome
            and isinstance(outcome[key], (str, int, float, bool))
        }
        for key in ("code", "kind"):
            if key in detail and (
                not isinstance(detail[key], str) or len(detail[key]) > 80
            ):
                del detail[key]
        generation = outcome.get("generation")
        if (
            isinstance(generation, str)
            and 1 <= len(generation) <= 128
            and all(c in "0123456789abcdef" for c in generation)
        ):
            detail["generation"] = generation
        if not self.causes:
            detail["unattributed"] = True
        effects = [
            index
            for index, event in enumerate(self.events)
            if event["kind"] == "effect"
        ]
        self.add(
            "output",
            "generation_result",
            causes=sorted(self.causes + self.joiners + effects),
            outcome=outcome.get("state"),
            detail=detail,
        )
        with self.lock:
            if self.omitted and self.events:
                self.events[-1]["detail"]["omitted_events"] = self.omitted
            self.closed = True
            payload = {
                "instance_id": self.instance_id,
                "run_id": self.run_id,
                "component": "C68",
                "action": "generate",
                "events": self.events,
            }
        self._publish(payload)

    def _publish(self, payload):
        try:
            body = json.dumps(payload, separators=(",", ":")).encode()
            if len(body) > 1024 * 1024:
                raise ValueError("Flow payload exceeds limit")
            connection = UnixConnection(self.socket_path)
            connection.timeout = 0.5
            try:
                connection.request(
                    "POST",
                    "/flow/events",
                    body,
                    {"Content-Type": "application/json"},
                )
                response = connection.getresponse()
                if not 200 <= response.status < 300:
                    raise RuntimeError("HTTP status " + str(response.status))
            finally:
                connection.close()
        except Exception:
            emit_record(
                "WARNING",
                "flow_publish_failed",
                "publish_flow",
                "degraded",
                self.run_id,
            )


def safe_target(target):
    if target is None or target in {"all", "atoms", "relations", "views"}:
        return target
    return "sha256:" + hashlib.sha256(target.encode()).hexdigest()
