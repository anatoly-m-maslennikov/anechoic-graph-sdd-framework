"""Generated lifecycle grid scenario helpers."""

from hashlib import sha256
import json
from pathlib import Path

import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.structure_snapshot__pub import (
    parse_structure,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.native_carrier_header__pub import (
    canonical_native_header,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.native_carrier_placement__pub import (
    native_carrier_path,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.PROJECT_SELECTION.\
    PROJECT_SELECTION__shared import (
    NativeProjectSelection,
)


class LifecycleGridCases1:
    def _grid_project(self, directory, body):
        root = Path(directory).resolve()
        (root / ".git").mkdir()
        control = root / ".anechoic_test"
        control.mkdir()
        manifest = control / "AN-S-1-PROJECT_MANIFEST--manifest.md"
        manifest.write_text("""---
identity: {atom_id: AN-S-1}
context: {container: {component: C00}, tier: -1, lens: SPEC, template: project_manifest}
state: {status: active, version: 1, updated_at: '2026-01-01'}
---
## Summary

Manifest

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ProjectManifest
declare_entity(entity_name='Project Manifest', instance=ProjectManifest(name='Test', prefix='AN', lens_whitelist=['DES', 'SPEC']))
```
""")
        project = NativeProjectSelection(
            root=root,
            control_root=control,
            control_relative=control.relative_to(root),
            instance_id="a" * 64,
            project_name="Test",
            project_prefix="AN",
            manifest_path=manifest,
            manifest_ref="AN-S-1@1",
            manifest_sha256=sha256(manifest.read_bytes()).hexdigest(),
        )
        component, declaration = self._grid_component(control, body)
        snapshot = self._grid_snapshot(manifest, declaration, control)
        owner_dir = self._grid_owner(project)
        return project, component, snapshot, owner_dir

    def _grid_component(self, control, body):
        component = control / "UNIT_C9"
        component.mkdir()
        declaration = control / "AN-S-2-SPEC--component.md"
        declaration.write_text(
            "---\n"
            + yaml.safe_dump(
                {
                    "identity": {"atom_id": "AN-S-2"},
                    "context": {
                        "container": {"component": "C00"},
                        "lens": "SPEC",
                    },
                    "state": {
                        "status": "active",
                        "version": 1,
                        "updated_at": "2026-01-01",
                    },
                }
            )
            + "---\n"
            + body
        )
        return component, declaration

    def _grid_snapshot(self, manifest, declaration, control):
        return parse_structure(
            json.dumps(
                {
                    "model_sha256": "model",
                    "project": {
                        "ref": "AN-S-1@1",
                        "sha256": sha256(manifest.read_bytes()).hexdigest(),
                    },
                    "components": {
                        "C9": {
                            "parent": "C00",
                            "ref": "AN-S-2@1",
                            "sha256": sha256(
                                declaration.read_bytes()
                            ).hexdigest(),
                            "fields": {"name": "Unit", "lens_whitelist": None},
                            "source_path": declaration.relative_to(
                                control
                            ).as_posix(),
                        }
                    },
                    "packages": {},
                }
            ).encode()
        )

    def _grid_owner(self, project):
        control = project.control_root
        owner_header = canonical_native_header(
            {
                "identity": {"atom_id": "AN-T-1"},
                "context": {
                    "container": {"component": "C00"},
                    "template": "task",
                },
                "state": {
                    "status": "in_queue",
                    "version": 1,
                    "updated_at": "2026-01-01",
                },
            }
        )
        owner_path = native_carrier_path(
            owner_header,
            "Owner",
            project_root=control,
            owner_directory=control,
        )
        owner_path.parent.mkdir(parents=True, exist_ok=True)
        owner_path.write_text(
            "---\n"
            + yaml.safe_dump(owner_header, sort_keys=False)
            + "---\n\n## Summary\n\nOwner\n"
        )
        return owner_path.with_suffix("")

    def _grid_carrier(
        self, case, project, component, owner_dir, container, body
    ):
        family, template, situation, contained, route = (
            case[k]
            for k in ("family", "template", "situation", "contained", "route")
        )
        atom_id = {
            "TKT": "AN-T-2",
            "SPEC": "AN-S-3",
            "PROJECT_CONFIG": "AN-C-1",
        }[family]
        if (
            family == "SPEC"
            and template == "project_manifest"
            and situation == "current"
            and not contained
        ):
            atom_id = "AN-S-1"
        elif situation != "new":
            self._write_grid_carrier(
                case, project, component, owner_dir, container, body, atom_id
            )
        return atom_id

    def _write_grid_carrier(
        self, case, project, component, owner_dir, container, body, atom_id
    ):
        family, template, situation, contained, route = (
            case[k]
            for k in ("family", "template", "situation", "contained", "route")
        )
        control = project.control_root
        context, status = self._grid_carrier_context(case, container)
        if (
            family == "PROJECT_CONFIG"
            and template is None
            and situation != "draft"
        ):
            pass
        else:
            version = (
                2
                if family == "PROJECT_CONFIG"
                and situation == "draft"
                and template is not None
                and not contained
                else 1
            )
            if version == 2:
                self._write_grid_previous(control, atom_id, context, body)
            self._write_grid_current(
                control,
                atom_id,
                context,
                status,
                version,
                owner_dir,
                contained,
                component,
                family,
                container,
                body,
            )

    def _write_grid_current(
        self,
        control,
        atom_id,
        context,
        status,
        version,
        owner_dir,
        contained,
        component,
        family,
        container,
        body,
    ):
        header = canonical_native_header(
            {
                "identity": {"atom_id": atom_id},
                "context": context,
                "state": {
                    "status": status,
                    "version": version,
                    "updated_at": "2026-01-01",
                },
            }
        )
        path = native_carrier_path(
            header,
            "Example",
            project_root=control,
            owner_directory=owner_dir
            if contained
            else component
            if family == "SPEC" and container == {"component": "C9"}
            else control,
            owner_template="task" if contained else None,
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "---\n" + yaml.safe_dump(header, sort_keys=False) + "---\n" + body
        )

    def _write_grid_previous(self, control, atom_id, context, body):
        previous = canonical_native_header(
            {
                "identity": {"atom_id": atom_id},
                "context": context,
                "state": {
                    "status": "active",
                    "version": 1,
                    "updated_at": "2026-01-01",
                },
            }
        )
        previous_path = native_carrier_path(
            previous,
            "Example",
            project_root=control,
            owner_directory=control,
        )
        previous_path.parent.mkdir(parents=True, exist_ok=True)
        previous_path.write_text(
            "---\n"
            + yaml.safe_dump(previous, sort_keys=False)
            + "---\n"
            + body
        )

    def _grid_carrier_context(self, case, container):
        family, template, situation, route = (
            case[k] for k in ("family", "template", "situation", "route")
        )
        context = {"container": container}
        if template is not None:
            context["template"] = template
        if family == "SPEC":
            tiers = {
                "project_manifest": -1,
                "axiom": 0,
                "component_contract": 0,
                "project_contract": 0,
                "applicable_principle": 2,
            }
            context.update(lens="SPEC", tier=tiers.get(template, 1))
        status = {
            "current": ("active" if route == "archive" else "ready")
            if family == "SPEC"
            else "active"
            if family == "PROJECT_CONFIG"
            else "in_queue",
            "draft": "draft",
            "archived": "archived",
        }[situation]
        status = case.get("source_status", status)
        return context, status
