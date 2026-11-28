"""Route watcher events and track ticket file versions."""


class WatcherEventRouting:
    def _index_existing_tickets(self, roots):
        for root in roots:
            for directory, folders, files in self._walk(
                root, followlinks=False
            ):
                if self._proof.closed:
                    return
                if self.defer_archives and "09_archived" in folders:
                    folders.remove("09_archived")
                for name in files:
                    path = self._event_path(directory) / name
                    self._index_ticket(path)

    def _index_ticket(self, path):
        if not self._ticket_path(path):
            return
        version = self._ticket_version(path)
        if version is None:
            return
        with self._ticket_lock:
            if path not in self._ticket_versions:
                self._remember_ticket(path, version)
                if self.defer_archives:
                    self._seeded_tickets.add(path)

    def _visible_entries(self, directory):
        if self._proof.closed:
            return
        with self._scandir(directory) as entries:
            for entry in entries:
                path = self._event_path(entry.path)
                if (
                    not self.watch_code
                    or not entry.is_dir(follow_symlinks=False)
                    or path.is_relative_to(self.control_root)
                    or self.control_root.is_relative_to(path)
                    or self._code_directory(path)
                ):
                    yield entry

    def _event_code(self, event, path):
        code = False
        if (
            event.is_directory
            and self.watch_code
            and path.is_relative_to(self.root)
        ):
            code = self._code_directory(path) or any(
                known.is_relative_to(path) for known in self.known_code
            )
        elif self.watch_code and not event.is_directory:
            current_code = self._code_path(path) and path.exists()
            code = current_code or path in self.known_code
            if current_code:
                self.known_code.add(path)
            else:
                self.known_code.discard(path)
        return code

    def _ticket_change(self, kind, paths):
        with self._ticket_lock:
            try:
                current = {path: self._ticket_version(path) for path in paths}
                if (
                    len(paths) == 1
                    and kind in {"created", "modified"}
                    and (version := current[paths[0]])
                ):
                    previous = self._ticket_inodes.get(version[:2])
                    if (
                        previous is not None
                        and previous != paths[0]
                        and self._ticket_version(previous) is None
                    ):
                        current[previous] = None
                        paths = [previous, paths[0]]
                        kind = "moved"
            except OSError:
                return kind, paths
            if all(
                path not in self._seeded_tickets
                and path in self._ticket_versions
                and self._ticket_versions[path] == version
                for path, version in current.items()
            ):
                return None
            for path, version in current.items():
                self._remember_ticket(path, version)
            return kind, paths

    @staticmethod
    def _ticket_version(path):
        try:
            info = path.lstat()
        except FileNotFoundError:
            return None
        return (
            info.st_dev,
            info.st_ino,
            info.st_mode,
            info.st_size,
            info.st_mtime_ns,
            info.st_ctime_ns,
        )

    def _event_relevance(self, event, paths, foreground):
        relevant = foreground
        for path in paths:
            markdown = (
                not event.is_directory
                and path.suffix.casefold() == ".md"
                and (
                    path.is_relative_to(self.control_root)
                    or path.parent == self.root
                )
            )
            code = self._event_code(event, path)
            if code and self._archives.root_for(path) is None:
                foreground = True
            boundary = event.is_directory and (
                path == self.control_root
                or path == self._archives.root_for(path)
            )
            relevant |= markdown or code or boundary
        return foreground, relevant
