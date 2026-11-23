"""Source closure and native model preparation for image admission."""

from hashlib import sha256
import os
from pathlib import Path
import re
import signal
import stat
import subprocess
import sys
import tomllib

try:
    from .runtime_images_common import (
        DOCKER_ROOT, ENGINE_ROOT, RETIRED_ASSETS, _GENERATED_ASSETS, _REQUIRED,
        ImageError, _excluded_directory, _excluded_file, ready_predecessor,
    )
except ImportError:
    from MCP_PATCHBAY_C21.FEATURE_MCP.docker.runtime_images_common import (
        DOCKER_ROOT, ENGINE_ROOT, RETIRED_ASSETS, _GENERATED_ASSETS, _REQUIRED,
        ImageError, _excluded_directory, _excluded_file, ready_predecessor,
    )

_SOURCE_LAYERS = ("LAYER_1_META_ONTOLOGY_C9", "LAYER_2_META_METHODOLOGY_C58")

_BETA_ROOTS = {"KERNEL_MIXER_beta_C67", "ORCHESTRATOR_beta_C68",
               "WORKERS_beta_C69", "WORKBENCH_BACKEND_beta_C70"}
_BETA_REQUIRED = (
    "FEATURE_PROGRAMMATIC/FEATURE_MODEL/FEATURE_MODEL_VALIDATION/project_admission__pub.py",
    "FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30/native_snapshot_cli.py",
    "IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_IMPORT_GRAPH_C61/realization_graph_cli.py",
    "KERNEL_MIXER_beta_C67/DATABASE_SERVER_beta_C71/DATABASE_SERVER_beta_C71__shared.py",
    "ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__shared.py",
    "ORCHESTRATOR_beta_C68/warm_worker.py",
    "WORKERS_beta_C69/WORKERS_beta_C69__shared.py",
    "WORKERS_beta_C69/warm_worker.py",
    *("WORKBENCH_BACKEND_beta_C70/" + name for name in (
        "WORKBENCH_BACKEND_beta_C70__shared.py", "runtime.py",
        "project_admission.py", "shared_runtime.py", "shared_peer_owner.py", "warm_worker.py", "query_run.json")),
)
_REPLACED_COMPONENTS = {
    ENGINE_ROOT + "/KERNEL_MIXER_C59",
    ENGINE_ROOT + "/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND",
}


class ImageSource:
    @staticmethod
    def _input_error():
        return ImageError("IMAGE_INPUT_UNAVAILABLE",
                          "Framework image inputs are unavailable or changed; supply a readable --source-root build closure")

    def _root(self) -> Path:
        try:
            if self.source_root.is_symlink() or not self.source_root.is_dir():
                raise self._input_error()
            return self.source_root.resolve(strict=True)
        except (OSError, ValueError) as error:
            raise self._input_error() from error

    def _project_root(self) -> Path:
        try:
            if self.project_root.is_symlink() or not self.project_root.is_dir():
                raise self._input_error()
            return self.project_root.resolve(strict=True)
        except (OSError, ValueError) as error:
            raise self._input_error() from error

    def _build_predecessor(self) -> str | None:
        """Pin the selected Project's last ready image for this manager."""
        if self._previous_image_resolved:
            return self.previous_image
        root = self._project_root()
        state = root
        for part in (".anechoic_runtime", "runtime", "project_mcp"):
            state = state / part
            if not os.path.lexists(state):
                self._previous_image_resolved = True
                return None
            if state.is_symlink() or not state.is_dir():
                raise self._input_error()
        try:
            from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import select_runtime_project
            selection = select_runtime_project(root)
            if (selection.root != root or not selection.control_root.is_relative_to(root)
                    or selection.launcher_state != state / selection.instance_id):
                raise ValueError("invalid Project launcher state")
            if os.path.lexists(selection.launcher_state) and (
                selection.launcher_state.is_symlink() or not selection.launcher_state.is_dir()
            ):
                raise ValueError("invalid Project launcher state")
            image = ready_predecessor(selection)
            self.previous_image = image
            self._previous_image_resolved = True
            return image
        except Exception as error:
            raise self._input_error() from error

    def _refresh_model(self, root: Path) -> str:
        previous = self._build_predecessor()
        command = [sys.executable, "-B", str(self._file(root, DOCKER_ROOT + "/native_model_refresh.py")),
                   str(self._project_root()), str(self.timeout)]
        if previous is not None:
            command.append(previous)
        process = subprocess.Popen(command, cwd=root, env={**{k: v for k, v in os.environ.items() if k != "PYTHONHOME"}, "PYTHONPATH": str(root / ENGINE_ROOT)}, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, text=True, start_new_session=True)
        try:
            output, _ = process.communicate(timeout=self.timeout)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.communicate()
            raise
        fingerprint = output.strip()
        if process.returncode or re.fullmatch(r"[0-9a-f]{64}", fingerprint) is None:
            raise ImageError("IMAGE_INPUT_UNAVAILABLE", "Native Model refresh failed")
        return fingerprint

    def _build_parent(self) -> Path:
        temporary = self._project_root() / ".anechoic_tmp"
        parent = self.build_temp_root or temporary
        try:
            if (temporary.is_symlink() or not temporary.is_dir()
                    or parent.is_symlink() or not parent.is_dir()):
                raise OSError("unsafe private image temporary root")
            expected = temporary.resolve(strict=True)
            resolved = parent.resolve(strict=True)
            if (not parent.is_absolute() or ".." in parent.parts or resolved != parent
                    or not resolved.is_relative_to(expected)):
                raise OSError("unsafe private image temporary root")
            return resolved
        except (OSError, ValueError) as error:
            raise ImageError("BUILD_FAILED", "Private image build context is unavailable") from error

    def _file(self, root: Path, relative: str) -> Path:
        path = root
        for part in Path(relative).parts:
            path /= part
            if path.is_symlink():
                raise self._input_error()
        if not path.is_file():
            raise self._input_error()
        return path

    def _stack_input(self, root: Path) -> tuple[str, tuple[Path, ...], str | None]:
        if not os.path.lexists(root / "LAYER_5_FRAMEWORK_DELIVERY/project.toml"):
            return "current", (), None
        path = self._file(root, "LAYER_5_FRAMEWORK_DELIVERY/project.toml")
        try:
            flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
            with os.fdopen(os.open(path, flags), "rb") as stream:
                info = os.fstat(stream.fileno())
                if not stat.S_ISREG(info.st_mode) or info.st_size > 65536:
                    raise ValueError("Invalid selector input")
                raw = stream.read(65537)
            if len(raw) > 65536:
                raise ValueError("Invalid selector size")
            settings = tomllib.loads(raw.decode("utf-8"))
        except (OSError, ValueError) as error:
            raise ImageError("IMAGE_INPUT_UNAVAILABLE", "Invalid project.toml build selector") from error
        if settings not in ({"stack": "current"}, {"stack": "beta"}):
            raise ImageError("IMAGE_INPUT_UNAVAILABLE", 'project.toml must specify stack = "current" or "beta"')
        return settings["stack"], (path,), sha256(raw).hexdigest()

    def _source_layer_files(self, root, selected, unavailable):
        for layer in _SOURCE_LAYERS:
            source = root / layer
            if source.is_symlink() or not source.is_dir():
                raise self._input_error()
            count = 0
            for current, directories, names in os.walk(source, followlinks=False, onerror=unavailable):
                for name in directories:
                    path = Path(current) / name
                    if path.is_symlink() or not path.is_dir():
                        raise self._input_error()
                for name in names:
                    if _excluded_file(name):
                        continue
                    path = Path(current) / name
                    if path.is_symlink() or not path.is_file() or path.suffix != ".md":
                        raise self._input_error()
                    selected.add(path)
                    count += 1
            if not count:
                raise self._input_error()

    def _files(self, root: Path, stack_input=None) -> tuple[Path, ...]:
        stack, selector, _ = self._stack_input(root) if stack_input is None else stack_input
        required = tuple(self._file(root, relative) for relative in _REQUIRED) + selector
        if stack == "beta":
            required += tuple(self._file(root, ENGINE_ROOT + "/" + path) for path in _BETA_REQUIRED)
        engine = root / ENGINE_ROOT
        if engine.is_symlink() or not engine.is_dir():
            raise self._input_error()
        selected = set(required)

        def unavailable(_error):
            raise self._input_error()

        for current, directories, names in os.walk(engine, followlinks=False, onerror=unavailable):
            folder = Path(current)
            retained = []
            for name in sorted(directories):
                path = folder / name
                relative = path.relative_to(root).as_posix()
                if (_excluded_directory(name) or _excluded_file(name)
                        or (re.search(r"_beta_C[0-9]+\Z", name) and
                            (stack != "beta" or (folder == engine and name not in _BETA_ROOTS)))
                        or (stack == "beta" and relative in _REPLACED_COMPONENTS)):
                    continue
                if path.is_symlink() or not path.is_dir():
                    raise self._input_error()
                retained.append(name)
            directories[:] = retained
            for name in sorted(names):
                if _excluded_file(name):
                    continue
                path = folder / name
                relative = path.relative_to(root).as_posix()
                if relative in _GENERATED_ASSETS | RETIRED_ASSETS:
                    if path.is_symlink() or not path.is_file():
                        raise self._input_error()
                    continue
                if path.is_symlink() or not path.is_file():
                    raise self._input_error()
                selected.add(path)
        self._source_layer_files(root, selected, unavailable)
        return tuple(sorted(selected, key=lambda path: path.relative_to(root).as_posix()))

