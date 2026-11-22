"""Keep image startup inside the built, isolated Python environment."""


import json
from pathlib import Path
import unittest


class DockerfileUVEntrypointTests(unittest.TestCase):
    def test_runtime_omits_git_and_strips_only_the_cryptography_extension(self):
        dockerfile = Path(__file__).resolve().parents[1] / "docker/Dockerfile"
        contents = dockerfile.read_text()
        self.assertNotIn("git config", contents)
        self.assertNotIn("no-install-recommends git", contents)
        self.assertIn("no-install-recommends ca-certificates", contents)
        extension = "/opt/venv/lib/python3.14/site-packages/cryptography/hazmat/bindings/_rust.abi3.so"
        self.assertIn(f"strip --strip-unneeded -o /tmp/cryptography-rust.so {extension}", contents)
        self.assertIn(f"mv /tmp/cryptography-rust.so {extension}", contents)
        self.assertIn("apt-get purge -y --auto-remove binutils", contents)
        self.assertIn("/usr/bin/perl /usr/bin/perl5.* /usr/lib/*/perl-base", contents)
        self.assertIn("! command -v git && ! command -v perl && ! command -v strip", contents)

    def test_entrypoint_has_no_ambient_python_or_environment_file_fallback(self):
        dockerfile = Path(__file__).resolve().parents[1] / "docker/Dockerfile"
        rows = [line for line in dockerfile.read_text().splitlines() if line.startswith("ENTRYPOINT ")]
        self.assertEqual(len(rows), 1)
        command = json.loads(rows[0].removeprefix("ENTRYPOINT "))
        self.assertEqual(command[0], "/opt/venv/bin/python")
        self.assertEqual(command[1:], ["-B", "LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker/entrypoint.py"])
        self.assertNotIn("workflow-orchestrator", dockerfile.read_text())
        self.assertNotIn(
            "RUN /opt/venv/bin/python LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/"
            "FEATURE_MCP/generate_tool_registry.py --package-root /workspace",
            dockerfile.read_text(),
        )

    def test_image_copies_runtime_components_and_canonical_ca_skill(self):
        dockerfile = (Path(__file__).resolve().parents[1] / "docker/Dockerfile").read_text()
        self.assertIn(
            "COPY LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC ./LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC",
            dockerfile,
        )
        for component in ("MCP_PATCHBAY_C21", "IWE_CONSOLE_C43"):
            path = f"LAYER_4_ENGINE_STUDIO_C14/{component}"
            self.assertIn(f"COPY {path} ./{path}", dockerfile)
        self.assertIn("FEATURE_AGENTIC/FEATURE_SKILLS/ane", dockerfile)
        self.assertNotIn("COPY LAYER_4_ENGINE_STUDIO_C14 ./LAYER_4_ENGINE_STUDIO_C14", dockerfile)
        self.assertNotIn("FEATURE_AGENTIC/FEATURE_PROMPTS", dockerfile)


if __name__ == "__main__":
    unittest.main()
