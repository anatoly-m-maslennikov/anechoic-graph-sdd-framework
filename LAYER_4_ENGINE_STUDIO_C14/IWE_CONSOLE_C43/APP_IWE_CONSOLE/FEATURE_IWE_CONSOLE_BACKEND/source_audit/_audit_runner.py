"""Run and publish queued Atom audits."""

from . import audit_worker as runtime


class AuditRunner:
    def _run(self) -> None:
        try:
            while True:
                with self._condition:
                    self._condition.wait_for(
                        lambda: (
                            self._stopped or self._pending_snapshot is not None
                        )
                    )
                    if self._stopped:
                        return
                    snapshot, paths, generation = (
                        self._pending_snapshot,
                        self._pending_paths,
                        self._generation,
                    )
                    self._pending_snapshot = None
                    self._pending_paths = runtime._EMPTY
                    self._active_paths = paths
                self._audit(snapshot, paths, generation)
                with self._condition:
                    self._active_paths = runtime._EMPTY
                    self._condition.notify_all()
        except Exception as error:
            with self._condition:
                self._error = error
                self._active_paths = runtime._EMPTY
                self._pending_paths = runtime._EMPTY
                self._pending_snapshot = None
                self._awaiting_submit = False
                self._condition.notify_all()
            print(
                f"Workbench ERROR atom_audit {type(error).__name__}: {error}",
                file=runtime.sys.stderr,
                flush=True,
            )

    def _audit(self, snapshot, paths, generation):
        started = runtime.time.monotonic()
        read_seconds = compute_seconds = 0.0
        selected = (
            sorted(
                path.relative_to(snapshot.root).as_posix()
                for path in snapshot.source_paths
            )
            if paths is None
            else sorted(paths)
        )
        issues = {table: [] for table in runtime.TABLES}
        for offset in range(0, len(selected), 500):
            if not self._current(generation, full=paths is None):
                break
            batch = set(selected[offset : offset + 500])
            phase = runtime.time.monotonic()
            rows = self._store.audit_content_rows(batch)
            read_seconds += runtime.time.monotonic() - phase
            phase = runtime.time.monotonic()
            for table, records in snapshot.collect(rows, batch).items():
                issues[table].extend(records)
            compute_seconds += runtime.time.monotonic() - phase
        if self._current(generation, full=paths is None):
            phase = runtime.time.monotonic()
            published = self._store.publish_audit(
                issues,
                paths,
                self._publication(generation, full=paths is None),
            )
            publish_seconds = runtime.time.monotonic() - phase
            if published:
                elapsed_ms = (runtime.time.monotonic() - started) * 1000
                with self._condition:
                    self._last_audit_ms = elapsed_ms
                print(
                    f"Workbench INFO atom_audit paths={len(selected)} "
                    f"mode={'full' if paths is None else 'delta'} "
                    f"read_ms={read_seconds * 1000:.1f} "
                    f"compute_ms={compute_seconds * 1000:.1f} "
                    f"publish_wait_and_commit_ms={publish_seconds * 1000:.1f} "
                    f"elapsed_ms={elapsed_ms:.1f}",
                    flush=True,
                )
