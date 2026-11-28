"""Package audit query contracts for the native Import Graph."""

import asyncio
from contextlib import redirect_stderr
from io import StringIO
import json

from mcp import types

from ...query.group_1 import test_native_query_stdio as fixture


PACKAGE_SPEC_SOURCE = (
    "---\natom_family: SPEC\natom_id: AN-S-007\ncontainer: {component: C1}\ntier: 2\n"
    "context: {lens: SPEC, template: component_seed_manifest}\n"
    "state: {status: active, version: 2, updated_at: '2026-11-22T09:00:00+00:00'}\n---\n"
    "## Formal Manifest\n\n```python\n"
    "from anechoic.formal_claims import declare_entity\n"
    "from anechoic.model import ComponentSeedManifest\n"
    'declare_entity(entity_name="Component Seed Manifest", '
    'instance=ComponentSeedManifest(component_seed_id="CS1"))\n```\n\n'
    "## Purpose\n\nProvide a service.\n\n## Solution\n\nAccept a request.\n"
)


class _PackageAuditCases:
    async def _prepare_package_audit(self):
        package = "src/UNIT_C1/service_CS1"
        self._source("src/UNIT_C1/__init__.py", "")
        marker = self._source(f"{package}/main__public.py", "pass\n")
        self._source(f"{package}/child/main__shared.py", "pass\n")
        self._source(f"{package}/service_CS1__tests/test_main.py", "pass\n")
        control = f"{fixture.CONTROL}/UNIT_C1"
        spec_source = PACKAGE_SPEC_SOURCE
        spec = self._source(
            f"{control}/AN-S-007-SPEC-COMPONENT_SEED_MANIFEST--service.md",
            spec_source,
        )
        self._source(
            (
                f"{control}"
                "/099_archived/AN-S-007@1-SPEC-COMPONENT_SEED_MANIFEST--servi"
                "ce.md"
            ),
            spec_source.replace("active, version: 2", "archived, version: 1"),
        )
        sidecar = self._source(
            f"{package}/service_CS1__spec_bind.yaml",
            "implements: [AN-S-007@1, AN-S-999@1]\napplies: [AN-S-007@2]\n",
        )
        structure = self._source(
            ".anechoic_tmp/structure.json",
            json.dumps({
                "model_sha256": "fixture",
                "project": {"ref": "AN-S-001@1", "sha256": "fixture"},
                "components": {
                    "C1": {
                        "parent": "C00",
                        "ref": "AN-S-006@1",
                        "sha256": "fixture",
                        "source_path": (
                            'AN-S-006-SPEC-COMPONENT_MANI'
                            'FEST--unit.md'
                        ),
                        "fields": {"name": "Unit"},
                    }
                },
            }),
        )
        gateway = await self._gateway(structure_snapshot=structure)

        return package, marker, spec_source, spec, sidecar, structure, gateway

    async def _package_audit(self, owner, path):
        response = await owner.call(
            None,
            types.CallToolRequestParams(
                name="query_run",
                arguments={
                    "sql": "SELECT has_internal, has_public, has_spec_bind, binding_status, "
                    "all_pins_active, list_sort(json_extract_string(pin_issues, '$[*].reason')), "
                    "contract_ref, contract_covered FROM package_audit "
                    f"WHERE relative_path = '{path}'",
                    "result_delivery": "inline",
                },
            ),
        )
        self.assertFalse(response.is_error, response.structured_content)
        return response.structured_content["rows"][0]

    async def _expect_package_audit(self, audit, expected):
        async with asyncio.timeout(6):
            while await audit() != expected:
                await asyncio.sleep(0.03)

    async def _assert_initial_package_audit(self, gateway, audit, package):
        schema = await gateway.call(
            None,
            types.CallToolRequestParams(name="query_schema", arguments={}),
        )
        self.assertIn("package_audit", schema.structured_content["tables"])
        self.assertEqual(
            [
                False,
                True,
                True,
                "valid",
                False,
                ["archived", "missing"],
                "AN-S-007@2",
                False,
            ],
            await audit(),
        )
        self.assertEqual(
            [False, False, False, "missing", None, [], None, None],
            await audit(path=f"{package}/service_CS1__tests"),
        )

    async def _assert_sidecar_refresh(
        self, package, marker, sidecar, expect_audit
    ):
        sidecar.write_text("{}\n", encoding="utf-8")
        await expect_audit([
            False,
            True,
            True,
            "empty",
            None,
            [],
            "AN-S-007@2",
            False,
        ])
        sidecar.write_text("implements: not-a-list\n", encoding="utf-8")
        await expect_audit([
            False,
            True,
            True,
            "invalid",
            None,
            [],
            "AN-S-007@2",
            False,
        ])
        self._source(
            f"{package}/service_CS1.p.spec_trace.md",
            "## Implements\n- AN-S-007@2\n",
        )
        sidecar.unlink()
        await expect_audit([
            False,
            True,
            False,
            "missing",
            None,
            [],
            "AN-S-007@2",
            False,
        ])
        sidecar.write_text("implements: [AN-S-007@2]\n", encoding="utf-8")
        marker.rename(marker.with_name("main__shared.py"))
        await expect_audit([
            True,
            False,
            True,
            "valid",
            True,
            [],
            "AN-S-007@2",
            True,
        ])

    async def _assert_spec_refresh(self, spec, spec_source, expect_audit):
        updated_spec = spec_source.replace("version: 2", "version: 3")
        spec.write_text(updated_spec, encoding="utf-8")
        expected = [
            True,
            False,
            True,
            "valid",
            False,
            ["missing"],
            "AN-S-007@3",
            False,
        ]
        await expect_audit(expected)
        stderr = StringIO()
        with redirect_stderr(stderr):
            spec.write_text(
                updated_spec.replace("Accept a request.", ""), encoding="utf-8"
            )
            await expect_audit(expected[:-2] + [None, None])
        self.assertIn("Invalid Component Seed Manifest", stderr.getvalue())
        spec.write_text(updated_spec, encoding="utf-8")
        await expect_audit(expected)
        return expected

    async def _assert_rebuild_reopen(
        self, gateway, audit, structure, expected
    ):
        rebuild = await gateway.call(
            None,
            types.CallToolRequestParams(
                name="query_rebuild", arguments={"target": "package_audit"}
            ),
        )
        self.assertFalse(rebuild.is_error, rebuild.structured_content)
        self.assertEqual(expected, await audit())
        await gateway.close()
        reopened = await self._gateway(structure_snapshot=structure)
        self.assertEqual(expected, await audit(owner=reopened))

    async def test_package_audit_tracks_exact_pins_and_contracts(self):
        (
            package,
            marker,
            spec_source,
            spec,
            sidecar,
            structure,
            gateway,
        ) = await self._prepare_package_audit()

        async def audit(owner=gateway, path=package):
            return await self._package_audit(owner, path)

        async def expect_audit(expected):
            await self._expect_package_audit(audit, expected)

        await self._assert_initial_package_audit(gateway, audit, package)
        await self._assert_sidecar_refresh(
            package, marker, sidecar, expect_audit
        )
        expected = await self._assert_spec_refresh(
            spec, spec_source, expect_audit
        )
        await self._assert_rebuild_reopen(gateway, audit, structure, expected)
