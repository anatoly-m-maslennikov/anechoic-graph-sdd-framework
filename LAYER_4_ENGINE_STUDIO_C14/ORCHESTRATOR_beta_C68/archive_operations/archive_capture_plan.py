"""Select the archive capture scope and track deferred changes."""

from ORCHESTRATOR_beta_C68.archive_operations import archive_jobs as jobs


class ArchiveCapturePlan:
    def _capture_options(self, reuse, paths, *, explicit=False):
        if self.skip_archives:
            epoch = (
                self.watcher.capture_epoch(trace=True)
                if self.thread is not None and not explicit
                else None
            )
            return {
                "foreground": True,
                "watcher_guarded": epoch is not None,
            }, epoch
        if explicit:
            return {}, None
        managed = self.thread is not None
        if paths is not None:
            epoch = self.watcher.capture_epoch(trace=True) if managed else None
            return (
                {"foreground": True} if self.deferred_archive else {}
            ), epoch
        if not (self.startup_capture or self.deferred_archive or managed):
            return {}, None
        has_archive = self.watcher.has_archive_roots()
        if has_archive and not (self.startup_capture or self.deferred_archive):
            return {}, None
        epoch = self.watcher.capture_epoch(trace=True)
        if self.startup_capture:
            options = {
                "watcher_guarded": epoch is not None,
                "foreground": True,
            }
            if epoch is not None and jobs.compatible_checkpoint(reuse):
                options["incremental"] = True
            return options, epoch
        foreground = (
            self.deferred_archive is not None
            or reuse is None
            or reuse.get("archive_pending") is True
        )
        return {
            "watcher_guarded": epoch is not None,
            "foreground": foreground,
        }, epoch

    def _restart_archive(self, reuse, result):
        if not {"unchanged", "paths", "compiler"} & result.keys():
            return None
        if reuse.get("checkpoint_scope") == "foreground":
            return {
                "roots": list(self.watcher.archive_roots()),
                "snapshot": {"atoms": [], "relations": []},
                "carrier_hashes": {},
                "endpoints": result.get("reuse", reuse)["endpoints"],
                "checkpoint_source": result.get("reuse", reuse),
            }
        checkpoint = jobs.archive_checkpoint(reuse)
        if "compiler" in result:
            checkpoint["endpoints"] = result["reuse"]["endpoints"]
        roots = self.watcher.archive_roots()
        if (
            not roots
            and not checkpoint["carrier_hashes"]
            and not reuse.get("archive_pending")
        ):
            return None
        return {
            "roots": list(roots),
            "snapshot": {"atoms": [], "relations": []},
            "carrier_hashes": {},
            "endpoints": checkpoint["endpoints"],
            "checkpoint": checkpoint,
        }

    def _needs_foreground(self, result):
        if "paths" not in result:
            return True
        return any(
            atom["status_group"] == "Archived"
            for atom in result["snapshot"]["atoms"]
        ) or any(
            str(jobs.Path(parent) / name)
            in self.deferred_archive["carrier_hashes"]
            for parent, name in result["paths"]
        )

    @staticmethod
    def _include_archive_pending(result, deferred):
        if deferred and (
            deferred["roots"]
            or deferred["snapshot"]["atoms"]
            or deferred["snapshot"].get("ingestion_issues")
            or "checkpoint" in deferred
            or "checkpoint_source" in deferred
        ):
            result["archive_pending"] = True
            if "archive_versions" in deferred:
                result["archive_versions"] = deferred.pop("archive_versions")

    def _is_archive_path(self, path):
        if not path:
            return False
        control = (
            jobs.Path(self.binding["root"]) / self.binding["control_root"]
        )
        location = jobs.Path(path)
        return (
            location.is_relative_to(control)
            and "09_archived" in location.relative_to(control).parts
        )

    def _partition_archive_changes(self, changes):
        if self.skip_archives:
            return [
                live
                for change in changes
                if (live := self._foreground_change(change)) is not None
            ]
        if self.deferred_archive is None:
            return changes
        live = []
        for change in changes:
            paths = [
                change[key]
                for key in ("old_path", "new_path")
                if change and change[key]
            ]
            deferred = [self._is_archive_path(path) for path in paths]
            if any(deferred):
                self.archive_dirty = True
            if not deferred or not all(deferred):
                live.append(change)
        return live

    def _foreground_change(self, change):
        paths = [change.get("old_path"), change.get("new_path")]
        archived = [self._is_archive_path(path) for path in paths]
        if not any(archived):
            return change
        if all(
            archived[index] or not path for index, path in enumerate(paths)
        ):
            return None
        index = 1 if archived[0] else 0
        return {
            **change,
            "old_path": paths[index],
            "new_path": None,
            "event_type": "created" if index else "deleted",
        }

    def _accept_live_generation(self, generation, result, deferred):
        self.live_generation = generation
        self.startup_capture = False
        full = "batch_artifact" in result or (
            "snapshot" in result and "paths" not in result
        )
        if deferred is not None or full:
            self._accept_deferred_archive(
                deferred if "archive_pending" in result else None
            )
            self.unconfirmed_lifecycle_write = False

    def _accept_deferred_archive(self, deferred):
        previous = self.deferred_archive
        self.deferred_archive = deferred
        if previous is None:
            self.archive_dirty |= (
                deferred is not None and self.archive_run is not None
            )
        elif deferred is not None:
            keys = (
                "roots",
                "endpoints",
                "checkpoint",
                "checkpoint_source",
                "snapshot",
                "carrier_hashes",
            )
            self.archive_dirty |= any(
                previous.get(key) != deferred.get(key) for key in keys
            )
