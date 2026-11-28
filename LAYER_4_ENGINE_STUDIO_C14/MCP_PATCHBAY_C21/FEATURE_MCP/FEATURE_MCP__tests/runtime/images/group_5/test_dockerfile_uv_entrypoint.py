"""Keep image startup inside the built, isolated Python environment."""

import json
from pathlib import Path
import re
import unittest


def _dockerfile():
    path = Path(__file__).resolve().parents[4] / "docker/Dockerfile"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"(?<=\S)\\\n(?=\S)", "", text)
    return re.sub(r"[ \t]*\\\n[ \t]*", " ", text)


class DockerfileUVEntrypointTests(unittest.TestCase):
    def test_runtime_omits_git_and_strips_only_the_cryptography_extension(
        self,
    ):
        contents = _dockerfile()
        self.assertNotIn("git config", contents)
        self.assertNotIn("no-install-recommends git", contents)
        self.assertIn("no-install-recommends ca-certificates", contents)
        extension = (
            "/opt/venv/lib/python3.14/site-packages/cryptography/hazmat/"
            "bindings/_rust.abi3.so"
        )
        self.assertIn(
            f"strip --strip-unneeded -o /tmp/cryptography-rust.so {extension}",
            contents,
        )
        self.assertIn(f"mv /tmp/cryptography-rust.so {extension}", contents)
        self.assertIn("apt-get purge -y --auto-remove binutils", contents)
        self.assertIn(
            "/usr/bin/perl /usr/bin/perl5.* /usr/lib/*/perl-base", contents
        )
        self.assertIn(
            "! command -v git && ! command -v perl && ! command -v strip",
            contents,
        )

    def test_entrypoint_has_no_ambient_python_or_environment_file_fallback(
        self,
    ):
        dockerfile = _dockerfile()
        rows = [
            line
            for line in dockerfile.splitlines()
            if line.startswith("ENTRYPOINT ")
        ]
        self.assertEqual(len(rows), 1)
        command = json.loads(rows[0].removeprefix("ENTRYPOINT "))
        self.assertEqual(command[0], "/opt/venv/bin/python")
        self.assertEqual(
            command[1:],
            [
                "-B",
                (
                    "LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/"
                    "docker/entrypoint.py"
                ),
            ],
        )
        self.assertNotIn("workflow-orchestrator", dockerfile)
        self.assertNotIn(
            "RUN /opt/venv/bin/python LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/"
            "FEATURE_MCP/generate_tool_registry.py --package-root /workspace",
            dockerfile,
        )

    def test_image_precompiles_only_the_current_runtime(self):
        dockerfile = _dockerfile()
        stages = re.findall(r"(?m)^FROM .+ AS (\w+)$", dockerfile)
        self.assertEqual(
            [
                "workbench_frontend",
                "runtime_build",
                "current",
                "openapi_build",
                "packaged",
            ],
            stages,
        )
        current = dockerfile.split("FROM scratch AS current\n")[1].split(
            "FROM current AS openapi_build\n"
        )[0]
        prefix = "/workspace/.anechoic_tmp/python/bytecode"
        self.assertIn(
            (
                "RUN PYTHONPYCACHEPREFIX="
                f"{prefix}"
                " /opt/venv/bin/python -B -m compileall"
            ),
            current,
        )
        self.assertIn("--invalidation-mode timestamp", current)
        self.assertIn('chmod -R a+rX "$PYTHONPYCACHEPREFIX"', current)
        for path in (
            "/usr/local/lib/python3.14",
            "/opt/venv/lib/python3.14/site-packages",
            "/workspace/LAYER_4_ENGINE_STUDIO_C14",
        ):
            self.assertIn(path, current[current.index("-m compileall") :])
        kernel = "LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59"
        self.assertIn(f"COPY {kernel} ./{kernel}", current)
        self.assertNotRegex(current, r"_beta_C[0-9]+")
        self.assertIn("ENV ANECHOIC_RUNTIME_STACK=current", current)
        self.assertIn("LABEL org.anechoic.runtime.stack=current", current)
        self.assertTrue(current.strip().endswith("USER anechoic"))

    def test_image_copies_runtime_components_and_canonical_ca_skill(self):
        dockerfile = _dockerfile()
        self.assertIn(
            (
                "COPY LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC ./"
                "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC"
            ),
            dockerfile,
        )
        for component in ("MCP_PATCHBAY_C21", "IWE_CONSOLE_C43"):
            path = f"LAYER_4_ENGINE_STUDIO_C14/{component}"
            self.assertIn(f"COPY {path} ./{path}", dockerfile)
        self.assertIn("FEATURE_AGENTIC/FEATURE_SKILLS/ane", dockerfile)
        self.assertNotIn(
            "COPY LAYER_4_ENGINE_STUDIO_C14 ./LAYER_4_ENGINE_STUDIO_C14",
            dockerfile,
        )
        self.assertNotIn("FEATURE_AGENTIC/FEATURE_PROMPTS", dockerfile)


if __name__ == "__main__":
    unittest.main()
