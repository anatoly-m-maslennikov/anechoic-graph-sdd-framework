"""Keep image startup inside the built, isolated Python environment."""

# CA-M-356@19

import json
from pathlib import Path
import unittest


class DockerfileUVEntrypointTests(unittest.TestCase):
    def test_git_trust_is_system_scoped_to_only_the_mounted_project(self):
        dockerfile = Path(__file__).resolve().parents[1] / "docker/Dockerfile"
        contents = dockerfile.read_text()
        self.assertIn("apt-get install -y --no-install-recommends git ca-certificates", contents)
        settings = [
            line.strip().removesuffix("\\").strip()
            for line in contents.splitlines()
            if "safe.directory" in line
        ]
        self.assertEqual(["&& git config --system --add safe.directory /project"], settings)

    def test_entrypoint_has_no_ambient_python_or_environment_file_fallback(self):
        dockerfile = Path(__file__).resolve().parents[1] / "docker/Dockerfile"
        rows = [line for line in dockerfile.read_text().splitlines() if line.startswith("ENTRYPOINT ")]
        self.assertEqual(len(rows), 1)
        command = json.loads(rows[0].removeprefix("ENTRYPOINT "))
        self.assertEqual(command[0], "/opt/venv/bin/python")
        self.assertEqual(command[1:], ["LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker/entrypoint.py"])
        self.assertNotIn("workflow-orchestrator", dockerfile.read_text())
        self.assertNotIn(
            "RUN /opt/venv/bin/python LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/"
            "FEATURE_MCP/generate_tool_registry.py --package-root /workspace",
            dockerfile.read_text(),
        )

    def test_image_copies_runtime_components_and_canonical_ca_skill(self):
        dockerfile = (Path(__file__).resolve().parents[1] / "docker/Dockerfile").read_text()
        self.assertIn(
            "COPY LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC ./LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC",
            dockerfile,
        )
        for component in ("MCP_PATCHBAY_C21", "IWE_CONSOLE_C43"):
            path = f"LAYER_3_ENGINE_STUDIO_C14/{component}"
            self.assertIn(f"COPY {path} ./{path}", dockerfile)
        self.assertIn("FEATURE_AGENTIC/FEATURE_SKILLS/ca", dockerfile)
        self.assertNotIn("COPY LAYER_3_ENGINE_STUDIO_C14 ./LAYER_3_ENGINE_STUDIO_C14", dockerfile)
        self.assertNotIn("FEATURE_AGENTIC/FEATURE_PROMPTS", dockerfile)


if __name__ == "__main__":
    unittest.main()
