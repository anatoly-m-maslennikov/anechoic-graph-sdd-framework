"""Lifecycle request handling."""


class LifecycleExecution:
    def _run_lifecycle(self, job, base_generation, structure_sha256, facts):
        from ORCHESTRATOR_beta_C68.lifecycle import lifecycle as lc

        request = {
            "binding": self.binding,
            "name": job.name,
            "base_generation": base_generation,
            "structure_sha256": structure_sha256,
            "arguments": job.arguments,
            **facts,
        }
        if facts and self.worker_socket is not None:
            try:
                outcome = lc.run_lifecycle(
                    self.worker_socket,
                    self.worker_load_seconds,
                    request,
                    self._register_warm_capture,
                    lc.operation_timeout(lc.LIFECYCLE_DEADLINE_SECONDS),
                )
            finally:
                with self.lock:
                    self.warm_capture = None
        else:
            outcome = self._run_cold_lifecycle(request)
        try:
            if not isinstance(outcome, dict):
                raise ValueError
            return lc._LifecycleReply.model_validate(outcome)
        except ValueError, lc.ValidationError:
            raise ValueError(
                "Lifecycle worker returned an invalid outcome"
            ) from None

    def _run_cold_lifecycle(self, request):
        from ORCHESTRATOR_beta_C68.lifecycle import lifecycle as lc

        if self.skip_archives:
            raise RuntimeError(
                "archive_disabled: Lifecycle requires archived Atom history"
            )
        process = self._start_lifecycle_process()
        try:
            stdout, stderr = process.communicate(
                lc.json.dumps(request),
                timeout=lc.operation_timeout(lc.LIFECYCLE_DEADLINE_SECONDS),
            )
        except lc.subprocess.TimeoutExpired:
            try:
                lc.os.killpg(process.pid, lc.signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.communicate()
            raise RuntimeError("Lifecycle worker deadline exceeded") from None
        finally:
            with self.lock:
                self.process = None
        if process.returncode:
            raise RuntimeError("Lifecycle worker failed: " + stderr[-2048:])
        return lc.json.loads(stdout)

    def _start_lifecycle_process(self):
        from ORCHESTRATOR_beta_C68.lifecycle import lifecycle as lc

        env = {
            key: value
            for key, value in lc.os.environ.items()
            if key != "PYTHONHOME"
        }
        env["PYTHONPATH"] = str(lc.ENGINE)
        env["ANECHOIC_BETA_WORKER_PARENT_PID"] = str(lc.os.getpid())
        with self.lock:
            if self.stopping.is_set():
                raise RuntimeError("Orchestrator is stopping")
            process = lc.subprocess.Popen(
                [
                    lc.sys.executable,
                    "-B",
                    "-P",
                    "-m",
                    "WORKERS_beta_C69.lifecycle_worker",
                ],
                stdin=lc.subprocess.PIPE,
                stdout=lc.subprocess.PIPE,
                stderr=lc.subprocess.PIPE,
                text=True,
                cwd=lc.ENGINE,
                env=env,
                start_new_session=True,
            )
            self.process = process
        return process

    def _execute_lifecycle(self, job):
        from ORCHESTRATOR_beta_C68.lifecycle import lifecycle as lc

        if self.unconfirmed_lifecycle_write:
            return self._blocked_lifecycle()
        try:
            base, structure, facts = self._lifecycle_inputs(job)
        except lc.ArchiveHistoryPending as error:
            return {
                "lifecycle": {
                    "outcome": "failed",
                    "errors": [
                        {"code": "archive_pending", "message": str(error)}
                    ],
                },
                "write_state": "known",
                "projection": {"state": "ready"},
            }
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            lc.http.client.HTTPException,
        ) as error:
            return {
                "lifecycle": {"outcome": "failed"},
                "write_state": "known",
                "projection": self._projection_failure(error),
            }
        lock = self.watcher.managed_write
        if not lock.acquire(blocking=False):
            raise lc.LifecycleCoveragePending()
        try:
            if not self._begin_lifecycle_write(job):
                return None
            return self._write_lifecycle(job, base, structure, facts)
        finally:
            lock.release()

    @staticmethod
    def _blocked_lifecycle():
        return {
            "lifecycle": {
                "outcome": "blocked",
                "errors": [
                    {
                        "code": "write_blocked",
                        "message": (
                            "Lifecycle requires admission of the preceding "
                            "write"
                        ),
                    }
                ],
            },
            "write_state": "known",
            "projection": {"state": "blocked"},
        }

    def _write_lifecycle(self, job, base, structure, facts):
        from ORCHESTRATOR_beta_C68.lifecycle import lifecycle as lc

        try:
            canonical = lc.json.dumps(
                structure, sort_keys=True, separators=(",", ":")
            ).encode()
            archive_epoch = self.watcher.capture_epoch(archive=True)
            reply = self._run_lifecycle(
                job, base, lc.sha256(canonical).hexdigest(), facts
            )
        except lc.WarmLifecycleUnavailable as error:
            return {
                "lifecycle": {"outcome": "failed"},
                "write_state": "known",
                "projection": self._projection_failure(error),
            }
        except (OSError, ValueError, TypeError, RuntimeError) as error:
            self.unconfirmed_lifecycle_write = True
            return {
                "lifecycle": None,
                "write_state": "unknown",
                "projection": self._projection_failure(error),
            }
        lifecycle = reply.lifecycle.model_dump(exclude_unset=True)
        projection = {"state": "ready", "generation": base}
        if reply.projection_error is not None:
            projection = self._projection_failure(reply.projection_error)
        elif reply.delta is not None:
            projection = self._admit_lifecycle_delta(reply.delta, base)
            if projection["state"] == "ready":
                self._acknowledge_lifecycle(
                    lifecycle.get("effects", []), archive_epoch
                )
        self._track_lifecycle_uncertainty(lifecycle, projection)
        return {
            "lifecycle": lifecycle,
            "write_state": "known",
            "projection": projection,
        }

    def _track_lifecycle_uncertainty(self, lifecycle, projection):
        uncertain = any(
            error.get("code") == "effect_uncertain"
            for error in lifecycle.get("errors", [])
        )
        if projection["state"] != "ready" and (
            uncertain or lifecycle.get("effects")
        ):
            self.unconfirmed_lifecycle_write = True

    def _admit_lifecycle_delta(self, delta, base):
        from ORCHESTRATOR_beta_C68.lifecycle import lifecycle as lc

        self.flow_context = {"lifecycle": True}
        self._start_flow(None, (), False)
        outcome = {"state": "failed", "code": "projection_refresh_failed"}
        try:
            if (
                not isinstance(delta, dict)
                or "paths" not in delta
                or delta.get("base_generation") != base
            ):
                raise ValueError("Invalid lifecycle delta")
            admitted = lc.admit_generation(
                self.database_socket, self.instance_id, None, delta, None
            )
            self.live_generation = self.generation_reuse.base_generation = (
                admitted["generation"]
            )
            self._flow_effect("generation_admission", outcome="succeeded")
            outcome = {
                "state": "succeeded",
                **admitted,
                "delta_path_count": len(delta["paths"]),
            }
            return {"state": "ready", "generation": admitted["generation"]}
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            RuntimeError,
            lc.http.client.HTTPException,
        ) as error:
            self._flow_effect("generation_admission", outcome="failed")
            return self._projection_failure(error)
        finally:
            self.flow.finish(outcome)
            self.flow = None
