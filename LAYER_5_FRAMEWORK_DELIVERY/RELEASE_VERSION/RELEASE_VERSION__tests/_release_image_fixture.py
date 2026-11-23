"""Provide a private source closure and a deterministic Docker test executor."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from RELEASE_VERSION import release_images as images


class ReleaseImageFixture(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.package = self.root / "package"
        self.package.mkdir()
        (self.package / "LAYER_5_FRAMEWORK_DELIVERY").mkdir()
        for relative in images._REQUIRED:
            path = self.package / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('[framework]\nversion = "1.2.3"\n' if relative == "version.toml" else "content")
        for layer in ("LAYER_1_META_ONTOLOGY_C9", "LAYER_2_META_METHODOLOGY_C58"):
            path = self.package / layer / "AN-S-1-source.md"
            path.parent.mkdir()
            path.write_text("source")
        self.build = self.root / ".anechoic_tmp/build"
        self.build.mkdir(parents=True)
        self.image = "sha256:" + "a" * 64
        self.provenance = {"project_id": "b" * 64, "project_root": str(self.root),
                           "control_root": ".anechoic_test", "project_name": "Project", "head_commit": "c" * 40}
        self.labels = {}
        self.tags = set()
        self.captured = set()
        self.build_args = []
        self.commands = []

    def docker(self, argv, **kwargs):
        self.commands.append((argv, kwargs["cwd"], kwargs["env"].get("BUILDX_CONFIG")))
        if argv[:3] == ["docker", "buildx", "prune"]:
            pass
        elif argv[:2] == ["docker", "build"]:
            self.build_args = argv
            labels = [argv[i + 1].split("=", 1) for i, item in enumerate(argv[:-1]) if item == "--label"]
            self.labels = dict(labels)
            context = Path(argv[-1])
            self.captured = {p.relative_to(context).as_posix() for p in context.rglob("*") if p.is_file()}
            Path(argv[argv.index("--iidfile") + 1]).write_text(self.image)
        elif argv[:3] == ["docker", "image", "inspect"]:
            data = [{"Id": self.image, "Os": "linux", "Architecture": self.manager.platform.split("/")[1],
                     "Config": {"Labels": self.labels}}]
            kwargs["stdout"].write(json.dumps(data).encode())
        elif argv[:3] == ["docker", "image", "ls"]:
            if argv[-1] in self.tags:
                kwargs["stdout"].write((self.image + "\n").encode())
        elif argv[:3] == ["docker", "image", "tag"]:
            self.tags.add(argv[-1])
        elif argv[:3] == ["docker", "image", "rm"]:
            self.tags.remove(argv[-1])
        else:
            self.fail(str(argv))
        return subprocess.CompletedProcess(argv, 0)

    def make_manager(self, package=None, provenance=True):
        self.manager = images.ImageManager(package or self.package, project_root=self.root,
                                           build_temp_root=self.build, executor=self.docker,
                                           build_provenance=self.provenance if provenance else None)
        return self.manager
