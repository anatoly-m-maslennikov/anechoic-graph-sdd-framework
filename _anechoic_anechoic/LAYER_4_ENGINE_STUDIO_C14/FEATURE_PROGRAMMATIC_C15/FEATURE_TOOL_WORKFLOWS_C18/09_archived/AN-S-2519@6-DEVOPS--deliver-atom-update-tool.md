---
atom_family: SPEC
atom_id: AN-S-2519
container:
  component: C18
tier: 4
context:
  lens: DevOps
state:
  status: archived
  version: 6
  updated_at: "2026-11-27T15:50:51.353081+00:00"
---
## Summary

Deliver ATOM_UPDATE Tool

## Claim

This contract describes the legacy sealed-carrier or Subject-batch route. Native Draft and Current carriers use AN-S-3160 and the lifecycle rules in AN-S-1604. Exact historical carrier references apply when interpreting legacy inputs.

### Prose Claim

Workflow admission owns identity, Version/time, lifecycle and complete schema decisions. Connector calls use CA-D-625 only to verify the supplied request, source preconditions and permission and to perform the explicit mechanical operation. A connector does not choose those decisions.

This Delivery carrier records `TOOL_WORKFLOWS` ownership of the rebuilt flat RMEDO contracts and binds the canonical `ATOM_UPDATE` wrapper. Its rebuilt source authority uses the FEATURE's role folders, not an `ATOM_UPDATE` child folder. The existing executable collection remains at `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_UPDATE/`, explicitly bound to `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_UPDATE/atom_update.py`; it is not an independently registered Scope Unit. The new FEATURE Delivery root is future/unmaterialized and does not relocate that collection. It retains the existing generic update input and sealed apply guard and specifies authoritative-source-read-only Subject-only preview with opt-in local derived-candidate staging. The revised by-value and add/remove/full-set contracts require future implementation verification; historical index-based fixtures and source pins do not prove readiness. It does not define Core semantics, grammar adoption, migration decisions, source repair, or a new MCP route. CA-D-531 binds its separately admitted one-target Subject effect to the existing MCP update action.

the `ATOM_UPDATE` Tool **must** deliver its canonical executable Carrier at `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_UPDATE/atom_update.py`; that Carrier realizes `CA-R-866` through the Action `CA-O-030`.

The delivered `ATOM_UPDATE` wrapper **must** accept only the closed Subject-only preview envelope `{atoms, subject_profile?}`. Omission means `legacy`; `approved` is explicit; an unknown or malformed supplied profile fails. Each atom item is exactly an exact repository-relative source-path `selector`, an `expected` object containing exactly `atom_id`, `version`, and `sha256`, and an explicit `subject_patches` list. A replacement patch contains exactly `field` equal to `governs` or `depends_on`, `old` and `new`. Select one dependency by its unique exact current `old` value; caller indexes are rejected. Missing, ambiguous or duplicate current values fail before effects. The connector may compute an occurrence location internally after binding the exact source state. The selected profile validates both the pinned source and the proposed result. For replacement, the old value must match the pinned current bytes exactly, and the new value is explicit: no target, relation move, profile conversion, grammar conversion, or migration mapping is inferred.

Legacy uses `/` as bearer qualification, `:` as Property-to-allowed-value, and literal dots, and rejects every `atom(...)` selector. Approved syntax is governed by the actual Current CA-R-1931, CA-R-1321, CA-R-1324, CA-M-228 and CA-E-833 definitions, resolved with their exact positive Versions, canonical paths and SHA-256 at the operation's Scope epoch. Preserve the case, references, grouping, escaping, operators and selector restrictions declared by those definitions; this consumer does not substitute an older descriptive grammar or infer a profile. Unsupported syntax, source drift or unavailable authority fails closed. Syntax validation does not establish Entity admission or instance resolution. The result includes the selected `subject_profile` and `subject_profile_evidence` containing exactly five reviewed grammar pins and `native_admission: not_performed`, sealed in `preview_sha256`. This is lexical syntax/direction checking only: it does not enumerate selector instances, establish target conformance, or admit a native endpoint.

The Subject-only mode is exclusive. A request carrying `subject_patches` must not also carry complete `frontmatter` or `content` replacement fields. The selected source must be a complete, canonical, non-symlink Atom Carrier at the exact path, with the expected identity, Version, and full-file SHA-256. The preview validates the complete resulting Carrier and preserves path, filename, identity, Summary, body, unrelated frontmatter, and line endings; only the declared Subject spans plus required Version and `updated_at` spans may differ.

Subject-only preview **must** select a complete original Atom Carrier with a stable Atom ID, excluding Draft and archived carriers by both carried Status and placement. Both the pinned source and proposed result **must** pass existing complete-carrier validation, including the applicable Content Role/Type Status model and correct Carrier placement. Preserve the carried Status byte-for-byte; do not activate the source or perform a lifecycle transition. Missing, ambiguous, unsupported, or stale validation authority **must** fail closed.

**Instructed Subjects-only batch binding**

The existing updater realizes CA-R-866/CA-O-030's instructed exact ordered batch through its existing Workflow/Tool boundary. The actual instruction, Initiative and existing Operator authorization bind the packet; no extra form, review/pause response, content-review round or confirmation receipt is required or invented. Compose existing commit/stage/commit/promote/graph operations, preserving ordinary generic update behavior and actual outcomes. Public batch effects derive from the exact packet without initial intent-hash metadata; derive any fresh native intent internally. Retain normal local target/draft/patch/layout, source, archive, Version/time and readback checks, not a redundant full-candidate preflight. No new executor, Tool family or recovery mechanism is introduced.

## Details

AN-S-1916 defines shared logical operations, staged preview,
deterministic Subject intent, and direct MCP preparation.

### Batch-transition intent delivery

The ordinary schema1 Subject intent and every public preview and preparation shape in AN-S-1916 remain closed and unchanged. Only an exact active member of CA-R-866/CA-M-371/CA-O-030's explicit schema2 legacy-to-approved batch may use the following separate private intent.

The transition intent is exactly `{schema_version: 2, target, subject_profile: "approved", subject_profile_evidence, source_subject_profile: "legacy", source_subject_profile_evidence, subject_patches, proposal, execution_metadata, predecessorArchive, noop}`. The target, patches, proposal, execution metadata, predecessor archive and no-op rules retain their schema1 representations. Each profile evidence object is exactly `{grammar_pins, native_admission: "not_performed"}`; each pin is exactly `{atom_id, version, path, sha256}` with a positive Version and canonical Project-relative source path. The source pair binds the five historical legacy definitions; the target pair binds the five actual Current approved definitions. The whole object uses the existing canonical-JSON SHA-256 procedure, including both pairs and schema version. There are no optional transition fields.

Validate source values only under the explicitly sealed legacy profile and every resulting value under approved, including unpatched values; preserve final complete-carrier validation and all existing byte, Status, identity and effect checks. Revalidate both grammar sets and the exact active packet/member/request at preparation, staging, materialization and effect. Refuse missing, malformed, unknown or mixed-version fields, drift and use outside that batch; do not infer a profile or fall back. Schema1 packets/intents still reject the transition fields. Staging preserves the selected packet version, so a schema2 packet remains schema2 when exact draft pins are added. The existing direct scratch manifest stays schema1 and does not admit this transition.

This delivery adds no public singleton field, execution permission, new route or runtime-activation claim. Recognize the transition only from the operative Current M371/R866/O030 clauses and the matching Current D531 packet binding, retaining their actual source pins.

### Existing-Atom edit-draft staging and promotion

The existing `atom_update` Tool accepts `{operation: "stage_subject_batch", subject_batch: {path, digest}, limit?}` under CA-D-531. `limit` is a strict integer 1..10, default 10. Each call creates at most that many drafts with normal safe create-only/no-follow file checks and readback, changes no canonical/history files, and returns compact actual progress: `operation`, `state: "staging"|"staged"|"stopped"`, `count`, `completed`, `remaining`, `stage_run_id`, and `reviewed_packet: {path, digest}|null`, plus actual failure evidence. Only completed staging returns the final packet pinning every draft, preserving its schema1 or schema2 version and exact declared profiles. Preserve truthful partial artifacts; never report partial work as completed.
