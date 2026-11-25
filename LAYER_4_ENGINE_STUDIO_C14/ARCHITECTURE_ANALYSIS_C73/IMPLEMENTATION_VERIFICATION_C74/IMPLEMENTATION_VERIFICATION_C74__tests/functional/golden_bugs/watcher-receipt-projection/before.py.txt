"""Distinguish admitted lifecycle effects from independent watcher changes."""
from hashlib import file_digest
from pathlib import Path
import stat
from time import monotonic_ns


def _directory_identity(path):
    try:
        info = path.lstat()
        if stat.S_ISDIR(info.st_mode) and path.resolve() == path:
            return info.st_dev, info.st_ino
    except OSError:
        pass
    return None


class WriteReceipts:
    def __init__(self, root, archives, limit):
        self.root, self.archives, self.limit = root, archives, limit
        self.writes = {}
        self.pending = {}

    def acknowledge(self, effects, archive_epoch):
        directories, carriers = {}, []
        for effect in effects:
            if effect["state"] != "known":
                continue
            path = self.root / effect["target"]
            operation = effect["operation"]
            if path.suffix == ".md" and operation in {"create", "modify", "remove"}:
                self._remember(path, None if operation == "remove" else effect["evidence"])
                if operation != "remove":
                    carriers.append(path)
            elif (archive_epoch is not None and operation == "create" and effect.get("evidence") == "directory"
                  and path == self.archives.root_for(path) and (identity := _directory_identity(path))):
                directories[path] = identity
        for path, identity in directories.items():
            witnesses = tuple(str(carrier) for carrier in carriers if carrier.is_relative_to(path))
            if witnesses:
                self._remember(path, (archive_epoch, identity, witnesses, monotonic_ns()))
        while len(self.writes) > self.limit:
            del self.writes[next(iter(self.writes))]

    def _remember(self, path, witness):
        value = str(path)
        self.writes.pop(value, None)
        self.writes[value] = witness

    def filter(self, batch, archive_epoch):
        ready, pending = [], {}
        for change in (*self.pending.values(), *batch):
            handled = self._handled(change, archive_epoch) if change else False
            if handled is None:
                pending[change["old_path"]] = change
            elif not handled:
                ready.append(change)
        self.pending = pending
        return ready

    def _handled(self, change, archive_epoch):
        if change["is_directory"]:
            return self._handled_archive_creation(change, archive_epoch)
        return all(self._handled_file(path) for path in (change["old_path"], change["new_path"]) if path)

    def _handled_archive_creation(self, change, archive_epoch):
        """Require a completed archive sample so later carrier deletions are observable."""
        if change.get("event_type") != "created" or archive_epoch is None:
            return False
        path = change["old_path"]
        witness = self.writes.get(path)
        if not isinstance(witness, tuple):
            return False
        (observer, _, losses), identity, carriers, since = witness
        current, _, current_losses = archive_epoch
        if (current is not observer or current_losses != losses or _directory_identity(Path(path)) != identity
                or not all(self._handled_file(carrier) for carrier in carriers)):
            return False
        return self.archives.proof.sampled_archive_carriers(since, carriers)

    def _handled_file(self, value):
        if value not in self.writes:
            return False
        expected = self.writes[value]
        path = Path(value)
        try:
            if not path.is_relative_to(self.root) or path.resolve() != path:
                return False
            if not stat.S_ISREG(path.lstat().st_mode):
                return False
            with path.open("rb") as stream:
                return file_digest(stream, "sha256").hexdigest() == expected
        except FileNotFoundError:
            return expected is None
        except OSError:
            return False
