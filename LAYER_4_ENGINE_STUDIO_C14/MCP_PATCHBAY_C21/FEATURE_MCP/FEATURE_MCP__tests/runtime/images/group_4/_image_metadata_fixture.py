"""Mock Docker executor and local fixture for image metadata tests."""

from __future__ import annotations

from pathlib import Path


class DockerProbeBase:
    """A bounded Docker image executor with inspectable public effects."""

    def __init__(
        self,
        *,
        tags=(),
        listed=("sha256:" + "a" * 64,),
        collision=False,
        missing_tag=False,
    ):
        self.calls: list[tuple[str, ...]] = []
        self.tags = set(tags)
        self.listed = tuple(listed)
        self.collision = collision
        self.missing_tag = missing_tag
        self.labels: dict[str, str] = {}
        self.build_context: Path | None = None
        self.architecture = "amd64"

    @staticmethod
    def _labels(argv: list[str]) -> dict[str, str]:
        labels = {}
        for index, value in enumerate(argv):
            if value == "--label":
                key, label = argv[index + 1].split("=", 1)
                labels[key] = label
        return labels

    def _inspect(self, image: str) -> str:
        env = self._fixture_globals
        OTHER_IMAGE, EXPECTED_TAG, IMAGE = (
            env["OTHER_IMAGE"],
            env["EXPECTED_TAG"],
            env["IMAGE"],
        )
        CREATED, json = env["CREATED"], env["json"]
        inspected = (
            OTHER_IMAGE if self.collision and image == EXPECTED_TAG else IMAGE
        )
        tags = (
            []
            if self.missing_tag and image == EXPECTED_TAG
            else sorted(self.tags)
        )
        return json.dumps([
            {
                "Id": inspected,
                "RepoTags": tags if inspected == IMAGE else [EXPECTED_TAG],
                "Created": CREATED,
                "Config": {"Labels": self.labels},
                "Os": "linux",
                "Architecture": self.architecture,
            }
        ])

    def __call__(self, argv, **_kwargs):
        env = self._fixture_globals
        subprocess, Path, IMAGE = env["subprocess"], env["Path"], env["IMAGE"]
        self.calls.append(tuple(argv))
        if argv[:3] == ["docker", "buildx", "prune"]:
            return subprocess.CompletedProcess(argv, 0, "", "")
        if argv[:2] == ["docker", "build"]:
            self.labels = self._labels(argv)
            self.build_context = Path(argv[-1])
            self.architecture = argv[argv.index("--platform") + 1].split("/")[
                1
            ]
            Path(argv[argv.index("--iidfile") + 1]).write_text(
                IMAGE, encoding="ascii"
            )
            return subprocess.CompletedProcess(argv, 0, "", "")
        if argv[:3] == ["docker", "image", "ls"]:
            output = (
                ""
                if argv[-1].startswith("anechoic-runtime:")
                else "\n".join(self.listed)
            )
            return subprocess.CompletedProcess(argv, 0, output, "")
        if argv[:3] == ["docker", "image", "inspect"]:
            if (
                argv[-1].startswith("anechoic-runtime:")
                and argv[-1] not in self.tags
                and not (self.collision or self.missing_tag)
            ):
                return subprocess.CompletedProcess(argv, 1, "", "")
            return subprocess.CompletedProcess(
                argv, 0, self._inspect(argv[-1]), ""
            )
        if argv[:3] == ["docker", "image", "tag"]:
            self.tags.add(argv[-1])
            return subprocess.CompletedProcess(argv, 0, "", "")
        if argv[:3] == ["docker", "image", "rm"]:
            self.tags.remove(argv[-1])
            return subprocess.CompletedProcess(argv, 0, "", "")
        return subprocess.CompletedProcess(argv, 1, "", "")

    def commands(self, *prefix: str) -> list[tuple[str, ...]]:
        return [call for call in self.calls if call[: len(prefix)] == prefix]


def setup_fixture(self, env):
    APP = env["APP"]
    tempfile = env["tempfile"]
    Path = env["Path"]
    patch = env["patch"]
    ImageManager = env["ImageManager"]
    runtime_images = env["runtime_images"]
    VERSION = env["VERSION"]
    parent = (
        APP.parents[2] / ".anechoic_tmp/CA-P-2791/CA-P-2818/image-metadata"
    )
    parent.mkdir(parents=True, exist_ok=True)
    self.temporary = tempfile.TemporaryDirectory(dir=parent)
    self.addCleanup(self.temporary.cleanup)
    self.root = Path(self.temporary.name)
    self.project_temp = self.root / ".anechoic_tmp"
    self.project_temp.mkdir()
    self.scratch = Path(tempfile.mkdtemp(dir=self.project_temp))
    self.enterContext(
        patch.object(ImageManager, "_refresh_model", return_value="a" * 64)
    )
    self.enterContext(
        patch.object(
            runtime_images,
            "_compile_tool_registry",
            return_value=b'{"schema_version":1}\n',
        )
    )
    self._write_fixture(VERSION)


def write_fixture(self, version, env):
    LICENSE_INPUTS = env["LICENSE_INPUTS"]
    DOCKERFILE = env["DOCKERFILE"]
    DOCKERIGNORE = env["DOCKERIGNORE"]
    TOOL_REGISTRY = env["TOOL_REGISTRY"]
    (self.root / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine").mkdir(
        parents=True, exist_ok=True
    )
    (
        self.root
        / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/pyproject.toml"
    ).write_text("[project]\nname='fixture'\n", encoding="utf-8")
    (
        self.root
        / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/uv.lock"
    ).write_text("version = 1\n", encoding="utf-8")
    (self.root / "version.toml").write_text(
        f'[framework]\nversion = "{version}"\n', encoding="utf-8"
    )
    for relative, content in (
        *((name, "fixture license\n") for name in LICENSE_INPUTS),
        ("LAYER_4_ENGINE_STUDIO_C14/API_MIXER_beta_C91/__init__.py", ""),
        ("LAYER_4_ENGINE_STUDIO_C14/API_MIXER_beta_C91/openapi.py", ""),
        (DOCKERFILE, "FROM scratch\n"),
        (DOCKERIGNORE, ".git\n"),
        ("LAYER_4_ENGINE_STUDIO_C14/marker.py", "fixture-current-code\n"),
        *(
            (f"{layer}/AN-S-1-source.md", "fixture source\n")
            for layer in (
                "LAYER_1_META_ONTOLOGY_C9",
                "LAYER_2_META_METHODOLOGY_C58",
            )
        ),
        (TOOL_REGISTRY, '{"schema_version":1}\n'),
    ):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def make_manager(self, probe, env):
    ImageManager = env["ImageManager"]
    SCHEMA_LABEL = env["SCHEMA_LABEL"]
    FINGERPRINT_LABEL = env["FINGERPRINT_LABEL"]
    OCI_VERSION_LABEL = env["OCI_VERSION_LABEL"]
    manager = ImageManager(
        self.root,
        executor=probe,
        timeout=5,
        uid=1000,
        gid=1000,
        platform="linux/amd64",
        build_temp_root=self.scratch,
        project_root=self.root,
    )
    identity = manager.identity()
    probe.labels.update({
        SCHEMA_LABEL: "1",
        FINGERPRINT_LABEL: identity.fingerprint,
        OCI_VERSION_LABEL: identity.version,
    })
    return manager
