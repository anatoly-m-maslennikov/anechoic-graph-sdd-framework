"""Fixture steps for checkpoint process tests."""


def exercise_live_watcher(self, write_ticket, TICKETS):
    edited = write_ticket(self.tickets, 1, "Before coverage gap")
    deleted = write_ticket(self.tickets, 2, "Before removal")
    archive = write_ticket(
        self.archive, 99, "Before history edit", archived=True
    )
    control = self.tickets.parent.parent
    detached = self.runtime / "detached"
    with self.live_runtime() as (api, client):
        self.wait(
            lambda: self.settled(client),
            api,
            "API generation did not settle",
        )
        control.rename(detached)
        try:
            self.wait(
                lambda: client.get("/health").json().get("state") != "ready",
                api,
                "Watcher did not lose coverage",
            )
            added = edit_detached(
                self, write_ticket, control, detached, edited, deleted, archive
            )
        finally:
            detached.rename(control)
        check_live_reconciliation(
            self, api, client, TICKETS, edited, archive, added
        )


def edit_detached(
    self, write_ticket, control, detached, edited, deleted, archive
):
    for path, before, after in (
        (edited, "Before coverage gap", "After coverage gap"),
        (archive, "Before history edit", "After history edit"),
    ):
        carrier = detached / path.relative_to(control)
        carrier.write_text(
            carrier.read_text().replace(before, after),
            encoding="utf-8",
        )
    (detached / deleted.relative_to(control)).unlink()
    added = write_ticket(
        detached / self.tickets.relative_to(control),
        3,
        "Added during coverage gap",
    )
    return added


def check_live_reconciliation(
    self, api, client, TICKETS, edited, archive, added
):
    expected = [
        ["AN-T-1", edited.name, "After coverage gap"],
        ["AN-T-3", added.name, "Added during coverage gap"],
        ["AN-T-99@1", archive.name, "After history edit"],
    ]

    def reconciled():
        if self.settled(client) and self.query(client, TICKETS) == expected:
            modes = self.query(
                client,
                "SELECT json_extract_string(detail, '$.kind') "
                "FROM flow_events "
                "WHERE component = 'C68' AND name = 'generation_result' "
                "AND outcome = 'succeeded'",
            )
            return modes if len(modes) > 1 else None
        return None

    modes = self.wait(
        reconciled,
        api,
        "Projection did not reconcile missed live and Archive edits",
    )
    if ["native_delta"] not in modes:
        self.fail(
            self.query(
                client,
                "SELECT o.run_id, o.name, o.outcome, o.detail "
                "FROM flow_events o "
                "WHERE o.component = 'C68' ORDER BY o.at",
            )
        )
    self.assertEqual(1, modes.count(["full"]), modes)


def offline_manifest(self):
    component = (
        self.tickets.parents[1]
        / "AN-S-2-SPEC-COMPONENT_MANIFEST--declare-example.md"
    )
    body = (
        "---\natom_family: SPEC\natom_id: AN-S-2\n"
        "container: {component: C00}\ntier: 1\n"
        "context: {template: component_manifest, lens: SPEC}\n"
        "state: {status: active, version: 1, "
        "updated_at: '2026-11-19T00:00:00Z'}\n---\n"
        "\n## Summary\n\nDeclare example\n"
        "\n## Purpose\n\nServe the example.\n\n"
        "## Component Identity\n\n```python\n"
        "from anechoic.model import ComponentManifest\n"
        "ComponentManifest(component_id='C2', name='Before edit')\n```\n"
    )
    return component, body
