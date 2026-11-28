"""Golden contract for Project MCP image identity and admission."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import shutil
import tempfile
from unittest.mock import patch


APP = Path(__file__).resolve().parents[4]
DOCKER = APP / "docker"

from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image.image__shared import (  # noqa: E402
    TOOL_REGISTRY,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared import (  # noqa: E402
    ImageManager,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image_runtime.image_runtime__shared import (  # noqa: E402
    LICENSE_INPUTS,
)  # noqa: E402


IMAGE_ID = "sha256:" + "a" * 64
FRAMEWORK_VERSION = "0.4.4.9"


class ImageFixture:
    def setUp(self) -> None:
        parent = APP.parents[2] / ".anechoic_tmp/CA-P-2791/CA-P-2818/images"
        parent.mkdir(parents=True, exist_ok=True)
        self.fixture_root = Path(tempfile.mkdtemp(dir=parent))
        self.addCleanup(shutil.rmtree, self.fixture_root, ignore_errors=True)
        model = patch.object(
            ImageManager, "_refresh_model", return_value="a" * 64
        )
        model.start()
        self.addCleanup(model.stop)
        self.tools = patch(
            (
                "MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared._compile_t"
                "ool_registry"
            ),
            return_value=b'{"schema_version":1}\n',
        )
        self.tools.start()
        self.addCleanup(self.tools.stop)

    def manager(self, source_root: Path, executor) -> ImageManager:
        tagged, sources, inspections = set(), {}, {}

        def tagging_executor(argv, **kwargs):
            command = tuple(argv)
            if command[:3] == ("docker", "image", "tag"):
                tagged.add(command[-1])
                sources[command[-1]] = command[-2]
                return subprocess.CompletedProcess(argv, 0, "", "")
            if command[:3] == ("docker", "image", "inspect") and command[
                -1
            ].startswith("anechoic-runtime:"):
                tag = command[-1]
                if tag not in tagged:
                    return subprocess.CompletedProcess(argv, 1, "", "")
                payload = json.loads(inspections[sources[tag]])
                payload[0]["RepoTags"] = sorted(
                    set(payload[0].get("RepoTags", [])) | {tag}
                )
                return subprocess.CompletedProcess(
                    argv, 0, json.dumps(payload), ""
                )
            if command[:3] == ("docker", "image", "ls") and command[
                -1
            ].startswith("anechoic-runtime:"):
                return subprocess.CompletedProcess(argv, 0, "", "")
            result = executor(argv, **kwargs)
            if (
                command[:3] == ("docker", "image", "inspect")
                and result.returncode == 0
            ):
                inspections[command[-1]] = result.stdout
            return result

        return ImageManager(
            source_root,
            executor=tagging_executor,
            timeout=7,
            uid=1000,
            gid=1000,
            platform="linux/amd64",
            project_root=APP.parents[2],
        )

    @staticmethod
    def _add_fixture_sources(root):
        for relative in LICENSE_INPUTS:
            (root / relative).parent.mkdir(parents=True, exist_ok=True)
            (root / relative).write_text("fixture license\n", encoding="utf-8")
        for relative in (TOOL_REGISTRY,):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'{"schema_version":1}\n')
        for layer in (
            "LAYER_1_META_ONTOLOGY_C9",
            "LAYER_2_META_METHODOLOGY_C58",
        ):
            path = root / layer / "AN-S-1-source.md"
            path.parent.mkdir(parents=True)
            path.write_text("source")

    def source_fixture(self) -> Path:
        "Minimal admitted build closure; Project state never enters this tree."
        root = self.fixture_root / "source"
        docker = (
            root
            / "LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker"
        )
        docker.mkdir(parents=True)
        (root / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine").mkdir(
            parents=True
        )
        (
            root
            / (
                "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/pyproject."
                "toml"
            )
        ).write_text("[project]\nname = 'fixture'\n", encoding="utf-8")
        (
            root / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/uv.lock"
        ).write_text("version = 1\n", encoding="utf-8")
        (root / "version.toml").write_text(
            f'[framework]\nversion = "{FRAMEWORK_VERSION}"\n', encoding="utf-8"
        )
        (docker / "Dockerfile").write_text("FROM scratch\n", encoding="utf-8")
        (docker / "Dockerfile.dockerignore").write_text(
            ".git\n", encoding="utf-8"
        )
        (docker.parent / "server.py").write_text(
            "SERVER = 'one'\n", encoding="utf-8"
        )
        exporter = root / "LAYER_4_ENGINE_STUDIO_C14/API_MIXER_beta_C91"
        exporter.mkdir()
        for name in ("__init__.py", "openapi.py"):
            (exporter / name).write_text("fixture")
        self._add_fixture_sources(root)
        return root
