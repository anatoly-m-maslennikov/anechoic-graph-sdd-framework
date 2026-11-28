"""Watcher assertions for native Workbench cases."""


async def check_atom_changes(self, gateway, original):
    self._write(
        original,
        "AN-T-010",
        "active",
        1,
        body="## Summary\n\nFirst content.\n",
    )
    first = await self._wait_for_atom(
        gateway, lambda rows: len(rows) == 1 and rows[0][2] == "AN-T-010@1"
    )
    self.assertTrue(first[0][0].endswith("__TKT/TASKS/new/nested"))

    self._write(
        original,
        "AN-T-010",
        "active",
        1,
        body="## Summary\n\nChanged content.\n",
    )
    await self._wait_for_atom(
        gateway,
        lambda _: any(
            atom["id"] == "AN-T-010"
            and b"Changed content." in atom["_content_bytes"]
            for atom in gateway._native_query._capture.atoms
        ),
    )
    self._write(
        original,
        "AN-T-010",
        "active",
        2,
        body="## Summary\n\nChanged content.\n",
    )
    await self._wait_for_atom(
        gateway, lambda rows: len(rows) == 1 and rows[0][2] == "AN-T-010@2"
    )


async def check_atom_move(self, gateway, original, moved, control):
    source = self.root / control / original
    destination = self.root / control / moved
    destination.parent.mkdir(parents=True)
    source.rename(destination)
    await self._wait_for_atom(
        gateway,
        lambda rows: (
            len(rows) == 1
            and rows[0][0].endswith("__TKT/TASKS/moved")
            and rows[0][1] == destination.name
            and rows[0][2] == "AN-T-010@2"
        ),
    )
    destination.unlink()
    await self._wait_for_atom(gateway, lambda rows: not rows)


async def check_manifest_change(self, gateway, original):
    manifest = gateway.selection.manifest_path
    renamed = manifest.with_name(
        manifest.name.replace("--declare-", "--define-")
    )
    renamed.write_text(
        manifest.read_text().replace("version: 1", "version: 2", 1)
    )
    manifest.unlink()
    self._write(original, "AN-T-010", "active", 1)
    await self._wait_for_atom(
        gateway,
        lambda rows: (
            bool(rows)
            and any(
                row["_exact_ref"] == "AN-S-001@2"
                for row in gateway._native_query._capture.atoms
            )
        ),
    )
    self.assertEqual("AN-S-001@1", gateway.selection.manifest_ref)
    self.assertEqual(
        "AN-S-001@2",
        gateway._native_query._projection_selection.manifest_ref,
    )
