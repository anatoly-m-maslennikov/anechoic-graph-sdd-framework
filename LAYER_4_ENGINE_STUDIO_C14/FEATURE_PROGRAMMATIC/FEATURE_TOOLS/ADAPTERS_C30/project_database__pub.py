"Project database location and migration from the former Workbench location."

from pathlib import Path
import os
import shutil
import tempfile

PROJECT_DATABASE = Path(".anechoic_runtime/db/project.duckdb")
LEGACY_DATABASE = Path(".anechoic_runtime/workbench/projection.duckdb")


def console_state_path(root: Path) -> Path:
    """Select one state directory without moving or creating it."""
    runtime = root / ".anechoic_runtime"
    current = runtime / "iwe_console"
    legacy = runtime / "workbench"
    if any(
        path.is_symlink() or (path.exists() and not path.is_dir())
        for path in (runtime, current, legacy)
    ):
        raise ValueError(
            "IWE Console state must use Project runtime directories directly"
        )
    if legacy.exists():
        if current.exists():
            raise ValueError(
                "Both IWE Console and Workbench state directories exist"
            )
        return legacy
    return current


def migrate_project_database(root: Path) -> Path:
    target = root / PROJECT_DATABASE
    legacy = console_state_path(root) / LEGACY_DATABASE.name
    if target.resolve() != target or legacy.resolve() != legacy:
        raise ValueError(
            (
                "Project database paths must use the Project runtime "
                "directory directly"
            )
        )
    if target.exists() or not legacy.exists():
        return target
    import duckdb

    target.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(legacy)) as connection:
        connection.execute("CHECKPOINT")
        descriptor, temporary = tempfile.mkstemp(
            prefix=".project-migration-", dir=target.parent
        )
        try:
            with (
                os.fdopen(descriptor, "wb") as output,
                legacy.open("rb") as source,
            ):
                shutil.copyfileobj(source, output)
                output.flush()
                os.fsync(output.fileno())
            try:
                os.link(temporary, target)
            except FileExistsError:
                pass
        finally:
            os.unlink(temporary)
    return target
