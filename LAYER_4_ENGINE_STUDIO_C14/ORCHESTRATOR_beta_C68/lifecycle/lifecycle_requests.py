"""Lifecycle request handling."""


class LifecycleRequests:
    def lifecycle(self, request):
        invalid = self._validate_request(request)
        if invalid is not None:
            return invalid
        archive_versions = (
            self.deferred_archive is not None
            and self._archive_versions_available()
        )
        job = self._enqueue_request(request, archive_versions)
        if isinstance(job, tuple):
            return job
        return self._await_lifecycle(job)

    def _validate_request(self, request):
        from ORCHESTRATOR_beta_C68.lifecycle import lifecycle as lc

        if (
            not isinstance(request, dict)
            or set(request) != lc.FIELDS | {"name", "arguments"}
            or not isinstance(request["name"], str)
            or request["name"] not in lc.LIFECYCLE_TOOLS
            or not isinstance(request["arguments"], dict)
        ):
            return 400, {
                "error": {
                    "code": "invalid_request",
                    "message": "Invalid lifecycle fields",
                }
            }
        if request["instance_id"] != self.instance_id:
            return 409, {
                "error": {
                    "code": "instance_mismatch",
                    "message": "Instance does not match",
                }
            }
        if {
            key: request[key] for key in lc.FIELDS - {"instance_id"}
        } != self.binding:
            return 409, {
                "error": {
                    "code": "binding_mismatch",
                    "message": "Binding does not match",
                }
            }
        if self.skip_archives:
            return 409, {
                "error": {
                    "code": "archive_disabled",
                    "message": "Lifecycle requires archived Atom history",
                }
            }
        return None

    def _enqueue_request(self, request, archive_versions):
        from ORCHESTRATOR_beta_C68.lifecycle import lifecycle as lc

        with self.lock:
            if self.stopping.is_set():
                return 503, {
                    "error": {
                        "code": "orchestrator_stopping",
                        "message": "Orchestrator is stopping",
                    }
                }
            if self.startup_replay:
                return 409, {
                    "error": {
                        "code": "startup_replay_pending",
                        "message": "Project startup replay is pending",
                    }
                }
            if (
                self.startup_capture
                or self.deferred_archive is not None
                and not archive_versions
            ):
                return 409, {
                    "error": {
                        "code": "archive_pending",
                        "message": "Archived Atom history is incomplete",
                    }
                }
            if self.lifecycle_job is not None:
                return 409, {
                    "error": {
                        "code": "lifecycle_active",
                        "message": "Another lifecycle operation is active",
                    }
                }
            timeout = lc.operation_timeout(lc.LIFECYCLE_WAIT_SECONDS)
            job = self.lifecycle_job = lc._LifecycleJob(
                deadline=None if timeout is None else lc.monotonic() + timeout,
                name=request["name"],
                arguments=request["arguments"],
                archive_versions=archive_versions,
            )
            self.watcher.queue.put({})
            return job

    def _await_lifecycle(self, job):
        from ORCHESTRATOR_beta_C68.lifecycle import lifecycle as lc

        deadline = job.deadline
        job.event.wait(
            None if deadline is None else max(0, deadline - lc.monotonic())
        )
        with self.lock:
            if job.outcome is not None:
                return 200, {"result": job.outcome}
            if self.stopping.is_set():
                status, code, message = (
                    503,
                    "orchestrator_stopping",
                    "Orchestrator stopped",
                )
            else:
                status, code, message = (
                    504,
                    "lifecycle_deadline_exceeded",
                    "Lifecycle deadline exceeded",
                )
            if job.started:
                return status, {
                    "error": {
                        "code": "write_outcome_unknown",
                        "message": message + "; outcome is unknown",
                    }
                }
            if self.lifecycle_job is job:
                self.lifecycle_job = None
                if self.pending is not None:
                    self.watcher.queue.put({})
        return status, {
            "error": {
                "code": code,
                "message": message + "; no lifecycle write was attempted",
            }
        }

    def _lifecycle_inputs(self, job):
        from ORCHESTRATOR_beta_C68.lifecycle import lifecycle as lc

        if self.startup_replay:
            raise ValueError("Project startup replay is pending")
        archive_pending = self.deferred_archive is not None
        if (
            self.startup_capture
            or archive_pending
            and not job.archive_versions
        ):
            raise lc.ArchiveHistoryPending(
                "Archived Atom history is incomplete"
            )
        reuse = self.generation_reuse
        if reuse is None:
            raise ValueError(
                "An admitted generation is required for lifecycle writes"
            )
        self._require_lifecycle_coverage()
        reuse = reuse.model_dump(exclude_unset=True)
        base = reuse["base_generation"]
        if lc._new_component_task(job):
            return self._component_task_inputs(
                job, reuse, base, archive_pending
            )
        return self._context_inputs(job, reuse, base, archive_pending)

    def _component_task_inputs(self, job, reuse, base, archive_pending):
        from ORCHESTRATOR_beta_C68.lifecycle import lifecycle as lc

        structure = lc.read_structure(
            self.database_socket, self.instance_id, reuse
        )
        if structure is None:
            raise ValueError(
                "An admitted Structure is required for lifecycle writes"
            )
        if not isinstance(reuse.get("status_domains"), dict):
            if archive_pending:
                raise lc.ArchiveHistoryPending(
                    "Archived Atom history is incomplete"
                )
            return base, structure, {}
        number, labels = lc.ticket_allocation(
            self.database_socket,
            self.instance_id,
            base,
            self.binding["project_prefix"],
            archive_versions=job.archive_versions,
        )
        facts = {
            "max_number": number,
            "component_ids": list(structure["components"]),
            "manifest_ref": structure["project"]["ref"],
            "ticket_labels": labels,
            "endpoints": reuse["endpoints"],
        }
        return base, structure, {"indexed_task": facts}

    def _context_inputs(self, job, reuse, base, archive_pending):
        from ORCHESTRATOR_beta_C68.lifecycle import lifecycle as lc

        context = lc.lifecycle_context(
            self.database_socket,
            self.instance_id,
            base,
            self.binding["project_prefix"],
            job.name,
            job.arguments,
            archive_versions=job.archive_versions,
        )
        structure = context["structure"]
        full_capture = (
            lc.requires_project_capture(
                job, context, self.binding["control_root"]
            )
            or context.get("model") is None
            and not isinstance(reuse.get("status_domains"), dict)
        )
        if archive_pending and (
            full_capture or lc.needs_exact_archive(job, context)
        ):
            raise lc.ArchiveHistoryPending(
                "Archived Atom history is incomplete"
            )
        if full_capture:
            return base, structure, {}
        domains = (
            {"status_domains": reuse["status_domains"]}
            if "status_domains" in reuse
            else {}
        )
        return (
            base,
            structure,
            {
                "lifecycle_context": {
                    **context,
                    "endpoints": reuse["endpoints"],
                    **domains,
                }
            },
        )
