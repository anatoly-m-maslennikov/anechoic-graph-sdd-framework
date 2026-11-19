# Contract connections and delta — DSET 0.3

The following Contracts are already accepted and are only consumed here:

- `ANECHOIC-META-CNTR-011--repository-work-area-declaration` — repository/Work Area scope declaration.
- `ANECHOIC-CONTRACT-SKILL-001` — host-native skill distribution.
- `ANECHOIC-CONTRACT-SKILL-002` — target-project local-governance resolution.
- `ANECHOIC-CONTRACT-TOOL-001` — declared platform compatibility.
- `ANECHOIC-CONTRACT-TOOL-002` — dependency provenance and exceptions.
- `ANECHOIC-CONTRACT-OPS-001` — hosted protected-delivery evidence.

Their canonical text lives in the corresponding layer-owned
`dset/<layer>/specs/packages/methodology/contracts.md` file. This Change
does not restate them.

## ADDED — ANECHOIC-CONTRACT-OPS-002 Integration-first delivery topology

| Field | Value |
|---|---|
| Authority | Project release and Change contract in `.anechoic/anechoic_settings.toml` |
| Source | Schema 1.2 project and Change workspace declarations |
| Version or digest | `1.2` |
| Direction | Local integration branch to remote integration branch to protected release PR; optional isolated Change branch/worktree to integration branch first |
| Producer | Contributor or governed automation writing the declared Change workspace |
| Consumer | Review, traceability, release preparation, hosted CI, and archival |
| Conformance | Default `integration-branch`; optional explicit `branch-worktree`; configured branch roles; no permanent layer branches; separate Change identity, scope, authorization, and proof in either mode |
| Compatibility | Archived branch-worktree Changes remain valid; changing configured branch roles or a Change's selected mode requires refreshed affected evidence |
| Lifecycle | `active` |
