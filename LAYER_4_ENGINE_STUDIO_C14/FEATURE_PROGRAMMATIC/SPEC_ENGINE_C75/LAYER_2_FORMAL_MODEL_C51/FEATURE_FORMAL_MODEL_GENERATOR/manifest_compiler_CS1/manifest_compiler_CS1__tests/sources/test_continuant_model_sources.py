import tempfile
import unittest
from pathlib import Path

# fmt: off
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.\
    manifest_compiler_CS1 import (
    active_model_sources as sources,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.\
    manifest_compiler_CS1.manifest_compiler_CS1__shared import (
    read_active_model_sources,
)
# fmt: on

CONTINUANT_SOURCE = """---
atom_family: SPEC
atom_id: AN-S-1
concern:
  subject: Graph
  path: Model
  relation: is_contained_by
structure:
  container:
    component: C9
  tier: 2
context:
  lens: DOM/CONT
  template: manifest_node
state:
  status: active
  version: 1
  updated_at: 2026-11-20T00:00:00Z
---
## Formal Manifest

```python anechoic-edsl
class Graph:
    pass
```
"""


class ContinuantModelSourceTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.tmp_path = Path(directory.name)

    def test_continuant_disk_and_row_compilation(self):
        # fmt: off
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
            carriers.content.carrier_read__pub import parse_carrier
        from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
            LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.\
            manifest_compiler_CS1.active_model_sources import (
            compile_active_model_rows,
        )
        # fmt: on
        root = self.tmp_path.resolve()
        folder = root / "META_ONTOLOGY_C9" / "_DOM" / "CONT"
        folder.mkdir(parents=True)
        text = CONTINUANT_SOURCE
        path = folder / "AN-S-1-DOM--graph.md"
        path.write_text(text)
        disk = read_active_model_sources(root, root / "META_ONTOLOGY_C9")
        carrier = parse_carrier(text.encode(), path)
        rows = [
            {
                "source_path": str(path.relative_to(root)),
                "exact_ref": "AN-S-1@1",
                "metadata": carrier.metadata,
                "body": carrier.body,
            }
        ]
        assert disk == compile_active_model_rows(rows, has_c9=True)
        assert disk[0][1] == "MODEL//ANECHOIC <+ Graph"
        for change in (
            text.replace("  template: manifest_node\n", ""),
            text.replace(
                "  template: manifest_node", "  template: model_manifest"
            ),
            text.replace("  path: Model", "  path: Other"),
            text.replace("  relation: is_contained_by", "  relation: unknown"),
            text.replace(
                "## Formal Manifest",
                "## Claim scope\n\nMODEL//ANECHOIC <+ Graph\n\n"
                "## Formal Manifest",
            ),
        ):
            path.write_text(change)
            with self.assertRaises(ValueError):
                read_active_model_sources(root, root / "META_ONTOLOGY_C9")

    def test_continuant_node_concern_matches_direct_base(self):
        check = sources._check_continuant_address
        source = "META_ONTOLOGY_C9/_DOM/CONT/AN-S-1-CONT--task.md@1"
        text = "class SessionTask(Ephemeral):\n    pass\n"
        addresses = {
            "Ephemeral": "Graph/Node//Ephemeral",
            "OperativePlan": "Graph/Node//Ephemeral//Operative Plan",
        }
        check(
            source,
            "MODEL//ANECHOIC <+ Graph/Node//Ephemeral//Session Task",
            text,
            "manifest_node",
            addresses,
        )
        with self.assertRaisesRegex(ValueError, "direct node base"):
            check(
                source,
                "MODEL//ANECHOIC <+ Graph/Node//Ephemeral//"
                "Operative Plan//Session Task",
                text,
                "manifest_node",
                addresses,
            )
        check(
            source,
            "MODEL//ANECHOIC <+ Graph/Node//Ephemeral/Session Task",
            text,
            "manifest_node",
            addresses,
        )


if __name__ == "__main__":
    unittest.main()
