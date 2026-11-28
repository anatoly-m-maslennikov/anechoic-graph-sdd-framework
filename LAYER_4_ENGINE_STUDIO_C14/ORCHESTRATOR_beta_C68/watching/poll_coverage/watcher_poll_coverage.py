"""Track polling proof and archive watcher coverage."""

from ORCHESTRATOR_beta_C68.watching import watcher_poll as poll


class PollingProof:
    def __init__(self, root=None):
        self.condition = poll.Condition()
        self.sampling_lock = poll.Lock()
        self.closed = False
        self._revisions = [0, 0]
        self._losses = [0, 0]
        self._polls = ({}, {})
        self._archive_roots = [None, None]
        self._archive_sample = None
        self._diagnostics = poll.FenceDiagnostics(root)

    def archive_roots(self):
        with self.condition:
            roots = self._archive_roots[1]
            if roots is None:
                roots = self._archive_roots[0]
            return tuple(path for path, _, _ in roots or ())

    def ready(self, observer, *, archive):
        return (
            not self.closed
            and observer is not None
            and observer.is_alive()
            and bool(observer.emitters)
            and all(
                emitter.is_alive()
                and self._polls[archive].get(
                    emitter.watch.path, emitter.baseline_clean
                )
                for emitter in observer.emitters
            )
        )

    def epoch(self, observer, *, archive, trace=False, dispatched=False):
        with self.condition:
            if self.ready(observer, archive=archive):
                if dispatched and any(
                    self._polls[archive].get(emitter.watch.path)
                    != emitter._snapshot_started
                    for emitter in observer.emitters
                ):
                    return None
                if trace:
                    self._diagnostics.start(archive)
                return (
                    observer,
                    self._revisions[archive],
                    self._losses[archive],
                )
        return None

    def fence(
        self, observer, epoch, *, archive, timeout, run_id=None, replay=False
    ):
        started = poll.monotonic_ns()
        deadline = None if timeout is None else poll.monotonic() + timeout
        with self.condition:
            stable, reason = self._wait_fence(
                observer, epoch, archive, started, deadline, replay
            )
            record = (
                None
                if stable is True
                else self._diagnostics.failure(
                    archive,
                    run_id,
                    reason,
                    started,
                    epoch,
                    self._revisions[archive],
                    self._losses[archive],
                )
            )
        poll.report_fence_failure(record)
        return stable

    def _wait_fence(self, observer, epoch, archive, started, deadline, replay):
        if epoch is None or observer is not epoch[0]:
            return (
                None,
                "baseline_unavailable"
                if epoch is None
                else "observer_replaced",
            )
        _, revision, losses = epoch
        while (
            self.ready(observer, archive=archive)
            and losses == self._losses[archive]
        ):
            if not replay and self._revisions[archive] != revision:
                return False, "source_changed"
            if all(
                self._polls[archive].get(emitter.watch.path, 0) >= started
                for emitter in observer.emitters
            ):
                return True, None
            remaining = (
                0.25 if deadline is None else deadline - poll.monotonic()
            )
            if remaining <= 0:
                return None, "poll_timeout"
            self.condition.wait(min(remaining, 0.25))
        if losses != self._losses[archive]:
            return None, "coverage_lost"
        if self.closed or observer is None or not observer.is_alive():
            return None, "observer_stopped"
        return None, "emitter_unavailable"

    def complete(self, event, on_recovery=None):
        with self.condition:
            previous = self._polls[event.archive].get(event.src_path)
            self._polls[event.archive][event.src_path] = (
                event.started if event.clean else 0
            )
            if not event.clean:
                self._losses[event.archive] += 1
                if event.issue is not None:
                    kind, path, errno, fields = event.issue
                    self._diagnostics.observe(
                        event.archive,
                        "loss",
                        kind,
                        path,
                        errno=errno,
                        stat_fields=fields,
                    )
            elif (
                event.roots is not None
                and self._archive_roots[event.archive] != event.roots
            ):
                self._archive_roots[event.archive] = event.roots
                self._revisions[event.archive] += 1
                self._diagnostics.observe(
                    event.archive,
                    "change",
                    "archive_roots_changed",
                    event.src_path,
                )
            if previous == 0 and event.clean and on_recovery is not None:
                on_recovery()
            self.condition.notify_all()

    def observer_issue(self, archive, path, errno):
        with self.condition:
            self._diagnostics.observe(
                archive, "loss", "snapshot_failed", path, errno=errno
            )

    def remember_archive_sample(self, source, started, snapshot):
        with self.condition:
            if not self.closed:
                self._archive_sample = (source, started, snapshot)

    def sampled_archive_carriers(self, since, carriers):
        with self.condition:
            if self._archive_sample is None:
                return None
            source, started, snapshot = self._archive_sample
            if started < since or self._polls[True].get(source, 0) < started:
                return None
            try:
                return all(
                    poll.stat.S_ISREG(snapshot.stat_info(path).st_mode)
                    for path in carriers
                )
            except KeyError:
                return False

    def change(self, foreground, archive, event, paths):
        with self.condition:
            self._revisions[0] += foreground
            self._revisions[1] += archive
            for lane, changed in enumerate((foreground, archive)):
                if changed:
                    self._diagnostics.observe(
                        lane,
                        "change",
                        event.event_type,
                        paths[0],
                        destination=paths[1] if len(paths) > 1 else None,
                        stat_fields=getattr(event, "stat_fields", ()),
                    )
            self.condition.notify_all()

    def close(self):
        with self.condition:
            self.closed = True
            self._archive_sample = None
            self.condition.notify_all()


class ArchiveCoverage:
    def __init__(self, root, control_root, proof, deferred):
        self.root = root
        self.control = control_root
        self.installed = self.control / "000_ANECHOIC_framework"
        self.proof = proof
        self.deferred = deferred

    def snapshot_roots(self, snapshot):
        if not self.deferred:
            return None
        roots = []
        for name in snapshot.paths:
            if poll.os.path.basename(
                name
            ) != "09_archived" or not snapshot.isdir(name):
                continue
            path = poll.Path(name)
            if path == self.root_for(path):
                roots.append(
                    (
                        path.relative_to(self.root).as_posix(),
                        *snapshot.inode(name),
                    )
                )
        return tuple(sorted(roots))

    def root_for(self, path):
        if not path.is_relative_to(self.control):
            return None
        parts = path.relative_to(self.control).parts
        if "09_archived" in parts and not path.is_relative_to(self.installed):
            return self.control.joinpath(
                *parts[: parts.index("09_archived") + 1]
            )
        return None

    def skip_foreground_directory(self, directory):
        if not self.deferred:
            return False
        path = poll.Path(directory)
        return path == self.root_for(path) or path == self.installed

    def skip_installed(self, directory):
        return poll.Path(directory) == self.installed

    def entries(self, directory):
        path = poll.Path(directory)
        if self.proof.closed or path.is_relative_to(self.installed):
            return
        archived = self.root_for(path)
        with poll.os.scandir(directory) as entries:
            for entry in entries:
                if archived is not None or entry.is_dir(follow_symlinks=False):
                    yield entry

    def source_change(self, event, paths):
        foreground = archive = False
        tree_change = event.is_directory and event.event_type != "modified"
        for path in paths:
            if self.deferred and path.is_relative_to(self.installed):
                continue
            archived = self.root_for(path)
            if self.deferred and archived is not None:
                archive = True
                foreground |= archived == path and (
                    tree_change or not event.is_directory
                )
            elif path.is_relative_to(self.control):
                foreground = True
                archive |= tree_change
            elif path.parent == self.root and path.suffix.casefold() == ".md":
                foreground = True
            elif path == self.root and tree_change:
                foreground = archive = True
        if foreground or archive:
            self.proof.change(foreground, archive, event, paths)
        return foreground
