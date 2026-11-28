"""Capture and validate generation requests for managed Workers."""


class GenerationWorkerCapture:
    def _capture_generation(
        self,
        directory,
        reuse,
        paths,
        *,
        explicit,
        reconciliation,
        strict,
        recover_coverage,
        force_model=False,
    ):
        from ORCHESTRATOR_beta_C68.generation.worker import generation_worker as gw

        replay = self.thread is not None and not (explicit or strict)
        options, epoch = self._generation_options(
            reuse,
            paths,
            explicit,
            reconciliation,
            strict,
            replay,
            recover_coverage,
        )
        if (
            self.startup_capture
            and not options.get("incremental")
            and not reconciliation
        ):
            reuse = None
        timeout = gw.operation_timeout(45)
        run_id = self.active.run_id if self.active else None
        queued = None
        if replay and epoch is not None:
            queued = self.watcher.foreground_events()
        result = self._run_capture_worker(
            directory,
            reuse,
            paths,
            force_model,
            options,
            (queued, epoch, timeout, run_id),
        )
        self._check_capture_fence(epoch, replay, timeout, run_id)
        return result, reuse, options

    def _run_capture_worker(
        self, directory, reuse, paths, force_model, options, state
    ):
        from ORCHESTRATOR_beta_C68.generation.worker import generation_worker as gw

        queued, epoch, timeout, run_id = state
        try:
            return self._run_worker(
                directory, reuse, paths, force_model=force_model, **options
            )
        except gw.WorkerAborted:
            raise
        except gw.GENERATION_ERRORS as error:
            self._check_failed_capture(queued, epoch, timeout, run_id, error)
            raise

    def _check_capture_fence(self, epoch, replay, timeout, run_id):
        from ORCHESTRATOR_beta_C68.generation.worker import generation_worker as gw

        if self.stopping.is_set():
            raise gw.WorkerAborted("Worker aborted")
        if epoch is not None:
            fence = (
                self.watcher.replay_fence
                if replay
                else self.watcher.capture_fence
            )
            if fence(epoch, timeout=timeout, run_id=run_id) is not True:
                error = gw.ForegroundCoverageLost if replay else ValueError
                raise error(gw.FOREGROUND_FENCE_MESSAGE)

    def _check_failed_capture(self, queued, epoch, timeout, run_id, error):
        from ORCHESTRATOR_beta_C68.generation.worker import generation_worker as gw

        if queued is not None and not self.stopping.is_set():
            if (
                self.watcher.replay_fence(
                    epoch, timeout=timeout, run_id=run_id
                )
                is not True
            ):
                raise gw.ForegroundCoverageLost(
                    gw.FOREGROUND_FENCE_MESSAGE
                ) from error
            if self.watcher.foreground_events() != queued:
                raise gw.ForegroundInputsChanged(
                    gw.FOREGROUND_FENCE_MESSAGE
                ) from error

    def _generation_options(
        self,
        reuse,
        paths,
        explicit,
        reconciliation,
        strict,
        replay,
        recover_coverage,
    ):
        from ORCHESTRATOR_beta_C68.generation.worker import generation_worker as gw

        if recover_coverage:
            return self._recovery_options(reuse)
        options, epoch = (
            ({}, None)
            if reconciliation and not self.skip_archives
            else self._capture_options(reuse, paths, explicit=explicit)
        )
        if strict:
            epoch = None
            if options:
                options["watcher_guarded"] = False
                options.pop("incremental", None)
        elif (
            replay
            and epoch is None
            and (paths is not None or self.watcher.capture_epoch() is None)
        ):
            raise gw.ForegroundCoverageLost(gw.FOREGROUND_FENCE_MESSAGE)
        if not explicit and (
            self.graph_queued or self.graph_thread is not None
        ):
            options["defer_graph"] = True
        elif (
            replay
            and epoch is not None
            and paths is None
            and options.get("foreground")
            and self.watcher.watch_code
        ):
            options["replay_graph"] = True
        return options, epoch

    def _recovery_options(self, reuse):
        from ORCHESTRATOR_beta_C68.generation.worker import generation_worker as gw

        epoch = self.watcher.capture_epoch(trace=True)
        if epoch is None:
            raise gw.ForegroundCoverageLost(gw.FOREGROUND_FENCE_MESSAGE)
        return {
            "foreground": True,
            "watcher_guarded": True,
            "defer_graph": True,
            "incremental": not self.skip_archives
            and gw.compatible_checkpoint(reuse),
        }, epoch

    def _run_worker(
        self, directory, reuse, paths, *, force_model=False, **options
    ):
        from ORCHESTRATOR_beta_C68.generation.worker import generation_worker as gw

        result = self._warm_candidate(reuse, paths)
        if result is not None:
            return result
        request = gw.worker_request(
            self.binding, self.database_socket, self.instance_id, reuse, paths
        )
        request["batch_full"] = True
        request["model_source"] = {
            "accepted_model": gw.read_accepted_model(
                self.database_socket, self.instance_id
            ),
            "spec_database": {
                "socket": str(self.database_socket),
                "instance_id": self.instance_id,
            },
        }
        if force_model:
            request["model_source"]["force_rebuild"] = True
        request.update(options)
        stdout = self._communicate_worker(directory, request)
        result = gw.parse_worker_result(
            stdout,
            reuse,
            paths,
            request.get("structure"),
            foreground=options.get("foreground", False),
        )
        self.worker_mode = "cold"
        return result

    def _warm_candidate(self, reuse, paths):
        from ORCHESTRATOR_beta_C68.generation.worker import generation_worker as gw

        if (
            self.worker_socket
            and paths is not None
            and len(paths) <= gw.MAX_WARM_DELTA_PATHS
        ):
            try:
                result = self._run_warm_worker(reuse, paths)
            except Exception:
                self._flow_effect("worker_request", outcome="failed")
                raise
            self._flow_effect(
                "worker_request",
                outcome="succeeded" if result is not None else "unavailable",
            )
            if result is not None:
                self.worker_mode = "warm"
                return result
        return None

    def _archive_snapshot(self, endpoints, checkpoint=None, deferred=None):
        from ORCHESTRATOR_beta_C68.generation.worker import generation_worker as gw

        epoch = self.watcher.capture_epoch(archive=True, trace=True)
        roots = self.watcher.archive_roots()
        if epoch is None:
            raise gw.ArchiveCoverageLost(
                "Archive watcher coverage is unavailable"
            )
        temporary = gw.tempfile.TemporaryDirectory(prefix="anechoic-archive-")
        try:
            request = {
                "binding": self.binding,
                "reuse": checkpoint,
                "watcher_guarded": True,
                "archive": {"roots": roots, "endpoints": endpoints},
            }
            if deferred is not None:
                request["archive"]["seed"] = {
                    key: deferred[key]
                    for key in ("snapshot", "carrier_hashes")
                }
                request["batch_full"] = True
            result = self._run_archive_worker(
                str(gw.Path(temporary.name).resolve()), request
            )
            stable = self.watcher.capture_fence(
                epoch,
                archive=True,
                timeout=None,
                run_id=(self.archive_run.run_id if self.archive_run else None),
            )
            if stable is None:
                raise gw.ArchiveCoverageLost(gw._ARCHIVE_FENCE_MESSAGE)
            if not stable or roots != self.watcher.archive_roots():
                raise gw.ArchiveInputsChanged(
                    "Archived Atom paths changed during capture"
                )
            if "batch_artifact" in result:
                result["_archive_temp"] = temporary
                temporary = None
            return endpoints, result
        finally:
            if temporary is not None:
                temporary.cleanup()

    def _run_archive_worker(self, directory, request):
        from ORCHESTRATOR_beta_C68.generation.worker import generation_worker as gw

        checkpoint = request["reuse"]
        if checkpoint is not None:
            incremental = {
                key: value
                for key, value in request.items()
                if key != "batch_full"
            }
            incremental["incremental"] = True
            incremental["archive"] = {
                key: value
                for key, value in request["archive"].items()
                if key != "seed"
            }
            stdout = self._communicate_worker(
                directory, incremental, archive=True
            )
            decoded = gw.json.loads(stdout)
            if decoded != {"incompatible": True}:
                result = gw.parse_worker_data(decoded, checkpoint, None)
                if (
                    "paths" not in result
                    and result.get("unchanged") is not True
                ):
                    raise ValueError(
                        "Worker returned invalid incremental Archive result"
                    )
                return result
        result = gw.parse_archive_result(
            self._communicate_worker(
                directory, request | {"reuse": None}, archive=True
            )
        )
        return result | {"replace": True} if checkpoint is not None else result
