from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

import yaml


APP_ROOT = Path(__file__).resolve().parents[4]
ASSETS = (
    Path(__file__).resolve().parents[1] / "assets" / "content_declaration_schema"
)
SEALED_MODEL = APP_ROOT.parent / (
    "FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests/assets/lifecy"
    "cle_schema_declarations/04_requirement"
)

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (  # noqa: E402
    carrier_read_view,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.model__shared import (  # noqa: E402
    bindings_from_workbench_rows,
)

from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (  # noqa: E402
    compile_content_schema,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (  # noqa: E402
    parse_content,
)


SUMMARY_CLAIM = (
    "property_rule(address='Atom.Content.Summary', occurrences='1', "
    "values='1')"
)
RMED_CLAIM = """
property_rule(
    address='Atom/(.Header.Role in RMED).Content.Claim',
    value_format='', occurrences='1', values='0',
)
allowed_children(
    address='Atom/(.Header.Role in RMED).Content.Claim',
    names=('Formal Claim', 'Prose Claim'), occurrences='1..2', name_format='string',
)
property_rule(address='Atom/(.Header.Role in RMED).Content.Claim.Formal Claim', values='1')
property_rule(address='Atom/(.Header.Role in RMED).Content.Claim.Prose Claim', values='1')
""".strip()


def python_claim_body(source: str) -> str:
    return f"## Claim\n\n### Formal Claim\n\n```python\n{source}\n```\n"


class ContentSchemaFixture(unittest.TestCase):
    @staticmethod
    def atom(
        reference: str,
        *,
        role: str = "Requirement",
        form: str = "Declaration",
        status_group: str = "Current",
        body: str,
    ) -> dict:
        return {
            "ref": reference,
            "id": reference,
            "version": 1,
            "source_path": f"model/{reference}.md",
            "role": role,
            "form": form,
            "status_group": status_group,
            "content_markdown": body,
            "content_properties_json": parse_content(
                body, tolerate_duplicate_siblings=True
            ),
        }

    def declaration(self, reference: str, source: str) -> dict:
        return self.atom(
            reference,
            body=python_claim_body(source),
        )

    @staticmethod
    def _compile_model_rows(rows: list[dict]):
        bindings = bindings_from_workbench_rows(rows)
        return compile_content_schema(
            [{**row, "_model_class_bindings": bindings} for row in rows]
        )

    @staticmethod
    def _current_declaration(path: Path) -> dict:
        _opening, frontmatter, body = path.read_text(encoding="utf-8").split(
            "---", 2
        )
        metadata = yaml.safe_load(frontmatter)
        header = carrier_read_view(metadata)
        return {
            "ref": header.get("ref_id"),
            "id": header.get("atom_id"),
            "version": header.get("version"),
            "source_path": path.as_posix(),
            "role": header.get("role"),
            "form": header.get("form"),
            "status_group": "Current",
            "content_markdown": body,
            "header_json": metadata,
            "_content_bytes": body.encode("utf-8"),
            "content_properties_json": parse_content(
                body, tolerate_duplicate_siblings=True
            ),
        }

    @classmethod
    def _current_model_rows(cls) -> list[dict]:
        return [
            cls._current_declaration(path)
            for directory in (SEALED_MODEL, ASSETS / "04_requirement")
            for path in sorted(
                directory.rglob("*.md"), key=lambda item: item.name
            )
            if not {"archive", "archived", "draft", "drafts"}
            & {part.casefold() for part in path.parts}
            and cls._is_current(path)
        ]

    @staticmethod
    def _prepared_reference_transform():
        path = ASSETS / "content_declaration_schema__shared.py"
        spec = spec_from_file_location("prepared_header_impact", path)
        assert spec is not None and spec.loader is not None
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.transform

    @staticmethod
    def _is_current(path: Path) -> bool:
        _opening, frontmatter, _body = path.read_text(encoding="utf-8").split(
            "---", 2
        )
        header = carrier_read_view(yaml.safe_load(frontmatter) or {})
        return header.get("status") not in {
            "Draft",
            "Archived",
            "archived",
        } and not str(header.get("atom_id", "")).endswith(("-draft", "@draft"))


if __name__ == "__main__":
    unittest.main()
