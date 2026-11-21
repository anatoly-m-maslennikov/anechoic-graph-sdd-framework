---
atom_family: TKT
atom_id: AN-T-2897
structure:
  container:
    component: C00
  priority: 2
context:
  template: Analysis Report
state:
  status: draft
  version: 1
  updated_at: '2026-11-13T17:40:50.546497+00:00'
---
## Summary

Atom Luna max benchmark 91d18eq8 batch 4

## Details

```json
{
  "model": "gpt-6-luna",
  "effort": "max",
  "role_evidence": {
    "query_id": "bc44fb26c45d4e45991fe959ed4f3bfc",
    "columns": [
      {
        "name": "reference",
        "type": "VARCHAR",
        "has_values": true
      },
      {
        "name": "content.summary",
        "type": "VARCHAR",
        "has_values": true
      },
      {
        "name": "content.claim.prose_claim",
        "type": "VARCHAR",
        "has_values": true
      },
      {
        "name": "content.semantics",
        "type": "VARCHAR",
        "has_values": true
      },
      {
        "name": "version",
        "type": "BIGINT",
        "has_values": true
      }
    ],
    "rows": [
      [
        "CA-R-2463",
        "Declare Operations",
        null,
        "An Operations Atom specifies work to perform and how it is coordinated, including its sequence, inputs and outputs.",
        7
      ],
      [
        "CA-R-2508",
        "Declare Atom",
        "Each Atom instance has exactly one outgoing HAS_ACTIVE_SUBJECT link. Its target is the declared entity or instance resolved from Header.Topics.Main Subject. An unresolved Subject is a diagnostic.\n\nFor each Atom instance, the outgoing GOVERNS Relation has cardinality 0..1 and targets only the canonical Subject the Atom governs through its applicable content. These are separate named outgoing permissions and do not grant an inverse or another Relation. The target-omitted bounds count each Atom’s outgoing links within each Relation Declaration’s admissible endpoint domain; they do not create links.\n\nEach Atom instance's outgoing IS_CONTAINED_BY Relation targets the Atom instance or Scope Unit instance selected by its Header.Container.",
        "An Atom is the smallest independently governed Object.",
        13
      ],
      [
        "CA-R-2512",
        "Declare Atom/(.Role := Requirement)",
        null,
        "A Requirement states a required outcome, behavior, property or constraint, or defines a governed model and its constraints. It applies across Aspects, including domain behavior, engineering performance, evaluation effectiveness and delivery reliability.",
        7
      ],
      [
        "CA-R-2514",
        "Declare Atom/(.Role := Evaluation)",
        null,
        "An Evaluation specifies falsifiable checks and how their evidence is interpreted to determine whether required results are achieved.",
        7
      ],
      [
        "CA-R-2515",
        "Declare Atom/(.Role := Delivery)",
        null,
        "A Delivery specifies how results are represented, packaged, stored and made available through their Carriers at their intended destinations.",
        7
      ],
      [
        "CA-R-2702",
        "Declare Atom.Header.Role",
        "Role Order Number classifies the Role-qualified Atom kind in the Model. Each Role Declaration assigns exactly one positive integer. Order numbers are distinct across Roles. Gaps are allowed.",
        null,
        3
      ]
    ],
    "row_count": 6,
    "source_row_count": 6,
    "column_count": 5,
    "offset": 0,
    "page_size": 30,
    "has_more": false
  },
  "atoms": [
    {
      "source_ref": "CA-O-215",
      "source_version": 12,
      "role": "Operations",
      "candidate": {
        "ref": "CA-O-215",
        "version": 12,
        "summary": "Rename one private carrier\n\n## Operation\n\nRename One Private Carrier is a reusable private Action. It performs one explicitly bound same-parent file or folder name change behind an admitted logical connector `modify`. It does not choose semantic identity or rewrite references.\n\n### Inputs and preconditions\n\nRequire CA-D-630's exact private rename binding, current source and parent evidence, and one explicit destination name. For an actual name change, require evidence that the destination is absent. For a folder, require sealed permission and context and a complete approved inventory. CA-R-1941 and CA-M-381 apply. Block the Action for a root or ancestor, escape, symlink, substitution, stale state, collision, overwrite, merge, or unapproved entry.\n\n### Action and result\n\nRequire CA-R-1941's exact staged-change review and a fresh trusted authorization/window record. The record must include confirmation that outside edits are paused. During that confirmed window, recheck the complete bound source, parent, and destination; inventory; preservation; authority; and permission frontier before the permitted storage effect. Retain independent readback and verification. Perform only the supplied same-parent name change. Independently verify the exact destination, absence of the old source, and preservation of contents, modes, inventory, and unrelated frontier. Then return CA-D-625's common result with actual evidence.\n\nA same-binding request is a no-op only when the requested state is verified as already satisfied and unchanged. On failure, retain known partial effects. Unknown effects require `effect_uncertain`, and nonempty errors never mean success. No automatic retry, rollback promise, reference discovery, or rewrite is implied.\n\n## Details\n\nThis is not O040's generic Artifact rename, which rewrites canonical references. The admitting Workflow owns domain identity, Version, lifecycle, and required history. A storage rename alone cannot complete them. No executable or runtime admission is established.",
        "prose_claim": null,
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-O-217",
      "source_version": 12,
      "role": "Operations",
      "candidate": {
        "ref": "CA-O-217",
        "version": 12,
        "summary": "Remove one non-Atom storage carrier\n\n## Operation\n\nRemove One Non-Atom Storage Carrier is a reusable private cleanup Action. It removes exactly one explicitly approved non-Atom file or empty folder behind an admitted logical connector `modify`. It is not an Atom deletion or a recursively selected cleanup set.\n\n### Inputs and preconditions\n\nRequire CA-D-630's private remove binding, an approved root and parent, the exact expected state, positive non-Atom cleanup eligibility, and explicit permission and context. Reject a root or ancestor, escape, symlink or substitution, nonempty folder, current or historical Atom carrier, required history, protected source, missing eligibility, or stale or ambiguous state. Do not treat an unrecognized or absent ID as proof that an item is non-Atom.\n\n### Action and result\n\nRequire CA-R-1941's exact staged-cleanup review and a fresh trusted authorization/window record, including recorded confirmation that outside edits are paused. During that confirmed window, recheck positive non-Atom eligibility, classification, root and parent, source state, empty-folder evidence, preservation, authority, and permission frontier before the effect. Retain independent readback and verification. Remove only the bound file or empty folder. Never discover child targets, follow a symlink, accept a wildcard or recursive flag, or touch a destination, referrer, or unrelated carrier. Independently verify observed absence and the unchanged preservation frontier.\n\nReturn CA-D-625's actual data, current_state, effects, and errors. A bound already-absent cleanup state is a no-op only when absence was explicitly expected, eligibility and permission remain valid, and the unchanged requested state is independently verified. A missing expected-present source is a failure, not inferred completion. Retain known partial effects. Unknown effects require `effect_uncertain`, and errors cannot indicate success.\n\n## Details\n\nAtom removal remains the existing admitted Archive/retire lifecycle with required history; O217 supplies no delete-Atom operation. No automatic set expansion, recovery, retry, or resume policy, implementation, or runtime route is established.",
        "prose_claim": null,
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-R-1041",
      "source_version": 18,
      "role": "Requirement",
      "candidate": {
        "ref": "CA-R-1041",
        "version": 18,
        "summary": "Coordinate Atom replacement intent\n\n## Scope\n\nREPLACE_ATOM's explicit singular or frozen bulk replacement intent, delegated application boundary, and truthful result evidence.\n\n## Claim\n\nREPLACE_ATOM must coordinate explicit Atom replacement intent without owning generic Carrier creation, relation editing, or archival semantics.\n\n- An atomic replacement accepts `=1` exact active predecessor Atom ID, `>=1` distinct exact sealed prepared-new successor Carrier sets, and action context. Each successor set contains complete sealed content, assigned identity, and destination. A preexisting-successor mode is not admitted.\n- Reject a missing, duplicate, inactive, or self-referential predecessor; missing, duplicate, partial, or unsealed prepared-new successor content; or a used successor identity or destination. Return a sealed replacement action containing the supplied predecessor, complete prepared-new successor set, and predecessor archive intent.\n- A Workflow with several predecessors supplies explicit mappings but invokes one independently admitted replacement Action per predecessor. Stop at the first failed Action, retain completed replacements, and leave the remainder untouched. Do not promise an all-or-nothing effect across predecessors.\n- Use the canonical Atom lifecycle capability to materialize only the complete sealed prepared-new successor set, establish every successor as Active, and then archive the predecessor. Pass the explicit IDs to the provenance pipeline. Do not infer successor content, perform generic Carrier creation, or write replacement relations in Atom Carriers.\n- Default to a mutation-free dry run. Permit apply only through authorized project-local MCP delegation with a sealed Initiative action envelope.\n- A successful delegated effect requires durable COMMIT_TRIGGER intake acknowledgment before MCP reports success. This acknowledgment is necessary for that handoff, but it does not prove that replacement was applied or that its authoritative Journal event and Run evidence were durably recorded. REPLACE_ATOM does not append the Journal, stage files, or create a Git Commit.\n- Distinguish a prepared sealed description, a deferred delegated request, and an actually applied replacement. Prepared or deferred results must state that the archive effect is not applied. Acceptance, sealing, or intake alone must not be reported as completed replacement.\n- At the actual effect boundary, revalidate the exact predecessor and every prepared-new successor's complete sealed content, identity, unused destination, current source and destination conditions, complete sealed mapping, and current delegated authority. Materialize every successor and verify that each is durably Active before archiving the predecessor. Use CA-O-051's whole-Carrier transition. Preserve the predecessor's body, Summary, Type, identity, and frontmatter values except actual archive Status, Version, and Updated At. Its actual changed archive Revision advances Version by `=1` and uses the applicable canonical archive encoding. Retain the exact before-Revision bytes and Version as required history.\n- Report actual replacement completion only with observed canonical lifecycle effects and durable authoritative archive-event evidence under CA-R-807. The evidence must name the explicit predecessor and the complete `>=1` materialized Active successor set. Preserve each explicit mapping and its actual result. Do not describe partial or uncertain effects as completed replacement.\n- Retain exact actual Workflow and Action Run identities, definition Revisions, input, result, and effect references, start and truthful terminal or pending evidence, and actual durable receipts under the reviewed CA-P-1443/CA-P-1451 shared contract. A recording failure leaves completion evidence blocked and pending evidence intact. Preserve the missing-recording disposition without replaying a performed replacement or resetting authority. An unpersisted acknowledgment is not Journal completion.\n\n## Details\n\nCA-O-031 owns the replacement Action. CA-O-051 and CA-R-807 govern canonical lifecycle effects and immutable replacement history. CA-E-299 covers the prepared description; CA-E-247 covers admission, delegated-effect, and receipt distinctions. The Tool admits no preexisting-successor mode, does not infer missing successor content, and gains no lifecycle or Journal authority from intake acceptance.\n\nEvery Summary value change requires a new Atom ID and predecessor archival through this replacement Workflow, even when the Claim remains unchanged. Return the explicit target, created, and archived IDs separately. For target `100` replaced by new Atom `200`, the result identifies target `100`, created `200`, and archived `100`. Replacement does not automatically retarget incoming references. Independent Find and Modify Workflows select and update those referencing Atoms. Resume and retry policy for independent replacements remains deferred. Current source, destination, permission, preview, and each replacement's internal storage-effect safeguards remain required.",
        "prose_claim": null,
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-R-865",
      "source_version": 29,
      "role": "Requirement",
      "candidate": {
        "ref": "CA-R-865",
        "version": 29,
        "summary": "Create ANECHOIC Markdown Atoms\n\n## Scope\n\nATOM_CREATE admission and creation of complete new Markdown Atom Carriers within configured Project control-root Content Role locations.\n\n## Claim\n\nThe ATOM_CREATE Tool must provide admission and creation of complete new Markdown Atom Carriers within configured Project control-root Content Role locations:\n\n- Accept one explicit logical CreateAtom request with complete admitted Atom content and its owning Scope Unit. The Workflow decides the admitted identity, metadata, initial Revision, and ownership, then supplies the exact content and applicable schema and authority bindings to the connector. The connector maps the logical target to private storage and mechanically checks the supplied placement and preconditions. It does not allocate identity or decide lifecycle policy.\n- Reject destination collisions and reused assigned Atom IDs, including IDs retained only in historical authority. Identity admission follows CA-D-508. An unassigned Draft does not acquire an invented ID.\n- Create `=1` Atom per independently admitted Action. A Workflow with several Atoms stops at the first failed Action, retains completed creations, and leaves the remainder untouched. Retain each one-Atom Action's complete admission, preflight, and storage-effect safeguards. Do not promise an all-or-nothing effect across Atoms.\n- Permit generic Carrier-construction mechanics while retaining responsibility for Atom admission, identity, Revision, one-Atom storage-effect safeguards, and effect semantics.\n- Default to a mutation-free dry run. Accept `--apply` only through authorized Project-local MCP delegation with a sealed Initiative action envelope.\n- Admit any requested initial Status allowed by the Atom's applicable Role/Type Status model and transition conditions. Journal append is an independent observation attempt. Its absence, incompleteness, or failure neither blocks a created Atom nor authorizes replay.\n\n## Details\n\nCA-O-032 defines the operational Action. CA-E-303 supplies its automated conformance cases. Delivery authority governs exact Carrier syntax; this Atom does not duplicate it.",
        "prose_claim": null,
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-D-631",
      "source_version": 13,
      "role": "Delivery",
      "candidate": {
        "ref": "CA-D-631",
        "version": 13,
        "summary": "Deliver complete configuration read data\n\n## Scope\n\nthe Configuration Read refinement of CA-D-625's closed logical interface.\n\n## Claim\n\nConfiguration Read must use the common request and result keys and the complete source representation below. CA-O-218 is its source Action binding on the same shared TOML connector as CA-O-204. Separate Actions do not create separate connectors.\n\n## Details\n\n### Request refinement\n\nKeep exactly `operation`, `target`, `query`, `delta`, `expected_state`, `authorization`, and `context`. Use `operation = \"read\"`, `target = {kind: \"Configuration\", identity}`, `query = null`, and `delta = null`. The identity is exactly `Project Structure` or `Project Settings` in the Project bound by context. A filename, path, or backend key is not a logical identity.\n\nContext binds the admitted Project, source view, exact source authority, and applicable schema definitions, including declared schema-version constraints. The caller selects these bindings; the connector checks them. `expected_state = null` selects an unpinned current Read. A non-null value enforces the supplied exact existing source-state evidence. Historical selection is explicit in context and requires available exact historical source and schema authority. It creates no retention policy.\n\n### Result refinement\n\nKeep exactly `data`, `current_state`, `effects`, and `errors`. Successful `data = {identity, source_text, document}` carries the complete unchanged UTF-8 TOML text and its complete parsed values, including unrelated tables and present optional values. Preserve the source text exactly. Do not synthesize absent optional fields. Use the TOML value representation in the existing connector binding. It must preserve value types and reject a lossy representation rather than silently stringify typed values.\n\n`current_state` carries the logical configuration identity, bound Project and source view, and exact observed source-state evidence used by the existing common contract. It identifies the same source bytes as `source_text` and `document`; it does not invent an Atom Version. A subsequent Modify uses this observed evidence as expected current state and rechecks it. It does not trust a prior Read as permission to write.\n\nA normal Read has `effects = []`. Use these errors: `target_not_found` for a missing source; `target_ambiguous` for ambiguous target or source resolution; `input_invalid` for an invalid request; `schema_invalid` for malformed TOML, invalid complete schema, or invalid schema binding; `stale_state` for mismatched evidence; `permission_denied` for denied permission; `backend_failure` for unavailable historical or backend evidence; and `unsupported_operation` for an unsupported operation. Retain CA-D-625's exact `{code, message, field}` error shape. Unavailable complete data is null, not an empty successful document. Nonempty errors never mean success. Empty errors require verified complete data and exact matching state evidence. Unexpected actual effects fail Read acceptance and remain truthfully reported. Unknown effects require `effect_uncertain`.\n\nReuse CA-D-527's existing outer envelope and recording rules. This source definition does not prove implementation, route admission, installed availability, a new history store, or stronger publication safety.",
        "prose_claim": null,
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-O-203",
      "source_version": 11,
      "role": "Operations",
      "candidate": {
        "ref": "CA-O-203",
        "version": 11,
        "summary": "Create one Scope Unit\n\n## Operation\n\nCreate One Scope Unit is the logical Action that adds exactly one explicitly requested Scope Unit to authoritative Project Structure under CA-R-1829. It does not infer a Scope Unit from a folder or invent a connector or authority root. The Workflow decides Scope identity and hierarchy, complete structure schema, and admission. A mechanical connector receives only the checked explicit target, delta, preconditions, and permission through CA-D-625.\n\n### Action\n\n1. Bind the explicit new Scope Unit identity, its declared parent, allowed type and properties, current Project Structure source pin, applicable current schema and authority, and exact permission. Reject duplicate identities, a missing or ambiguous parent, invalid hierarchy or root constraints, or an unsupported schema before effects.\n2. Validate the complete proposed authoritative structure under CA-D-441 and the current structure authority. Preserve all unrelated Scope Units and every protected field. The implicit Project root is not a duplicate `scope_units` row.\n3. Use the same shared TOML realization selected for O204 and resolve the Project Structure target privately. There is no separate TOML connector. Derive and expose this one exact mutation-free proposal before an independently admitted effect.\n4. Recheck source, authority, schema, and permission immediately before the safe one-Scope-Unit effect. Independently read back and schema-check the complete result. Report actual identity and effects, or truthful failed, partial, or unknown evidence. No Atom deletion, automatic reference rewrite, or unsupplied structural change follows.\n\n## Details\n\nIts separate governing Workflow and executable realization remain future-gated work. This Action does not introduce an additional Workflow or Step now. Current Project Structure dispatch semantics remain applicable. Storage paths and folders are private realization details, not the public Scope Unit selector.\n\nThese are normative source definitions, not executable bindings or live admission. Before any actual Run, resolve and independently verify the selected realization, current definition pins, applicable permissions, and shared Run recording under CA-R-1525/CA-R-1720. Missing, stale, unsupported, or incompatible bindings stop before dispatch. No new retry or resume decision, MCP activation, runtime manifest change, Core adoption, or Subject publication is authorized.",
        "prose_claim": null,
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-E-569",
      "source_version": 14,
      "role": "Evaluation",
      "candidate": {
        "ref": "CA-E-569",
        "version": 14,
        "summary": "Verify Artifact query and selected fetch\n\n## Scope\n\nGolden QA for `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FIND_AND_FETCH_ARTIFACTS/tests/test_find_and_fetch_artifacts.py`.\n\n## Claim\n\nThe golden test must prove that FIND_AND_FETCH_ARTIFACTS returns only the correct default IDs or explicitly selected fetch values from one stable read-only snapshot. It must truthfully reject every unsupported or incomplete case.\n\n## Details\n\nUse fixtures with distinct frontmatter and section namespaces; equal spelling across those namespaces; explicit null and absent fields; boolean and number values; date-like strings; typed arrays and maps; every status; nested headings containing slash or tilde; Atom and non-Atom identities; and several IDs. Assert RFC 8259 literals, RFC 6901 pointer and heading escaping, and CA-R-1850's precedence and parentheses for `NOT`, `AND`, and `OR`; equality, inequality, and `IN`; no implicit Active narrowing; selected-only fetch; bytewise identity ordering; bounded cursor continuation that validates exact retained members without a second enumeration; and rejection of a changed-snapshot cursor.\n\nIndependently exercise invalid grammar, type, JSON literal, or selector; SQL/code-like input; missing, conflicting, or duplicate identity; malformed frontmatter; duplicate key or heading; incomplete read; inaccessible root; filename-only identity; secret-shaped selection; attempted mutation; and every resolved query budget. Assert that no partial result is accepted and that no mutation, secret value, fabricated Run/Event, or snapshot enlargement occurs. If execution is admitted, assert use of the shared RUN_SUPPORT Journal contract.",
        "prose_claim": null,
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-O-178",
      "source_version": 17,
      "role": "Operations",
      "candidate": {
        "ref": "CA-O-178",
        "version": 17,
        "summary": "Install the runtime and project-local ca Skill\n\n## Step\n\nThis Step invokes CA-O-169 once with phase `install`. It copies compiled `LAYER_1_FRAMEWORK_METHODOLOGY/`, preserves protected configuration and Project state, installs Engine `.install` into the Project runtime package, and installs the `ca` payload.\n\n## Details\n\nOnly this Step clears replaceable installed Framework members, copies the product as-is, installs `ca`, and restarts or reuses Project MCP for Docker/MCP smoke. It preserves settings and Project state. It does not alter authoring, push, create a PR, or retry an uncertain effect.\n\nReuse canonical image preparation only after the Workflow's full suite is green. This occurrence also owns CA-O-169's post-smoke selected-Project retention: keep the exact admitted current-Version candidate; remove only proven owned, unused noncandidate images; preserve all container references and other Projects' images; and report pending cleanup. The same fingerprint alone does not preserve an older rebuild. No additional retirement Step is inserted into CA-O-164.",
        "prose_claim": null,
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-O-182",
      "source_version": 11,
      "role": "Operations",
      "candidate": {
        "ref": "CA-O-182",
        "version": 11,
        "summary": "Run host-capable Candidate E2E\n\n## Step\n\nAfter CA-O-186's immutable image canary, this Step invokes CA-O-181 once. It binds the exact candidate/package/image/N identity and explicit host-capable controller authorization.\n\n## Details\n\nAbsent host capability is non-pass; it does not permit fallback to the frozen Docker worker. Failed, partial, stale, unsafe, or missing-recording results stop before Full Gate aggregation, promotion, and retirement. Do not replay.",
        "prose_claim": null,
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-O-175",
      "source_version": 14,
      "role": "Operations",
      "candidate": {
        "ref": "CA-O-175",
        "version": 14,
        "summary": "Stage the candidate Framework package and ca Skill\n\n## Step\n\nThis Step invokes CA-O-167 once with phase `stage_candidate`. It binds CA-O-165's frozen active boundary to one private active-source copy, compiled package, runtime, and complete `ca` payload before CA-O-185's complete suite.\n\n## Details\n\nIt stages the complete candidate package and complete `ca` directory without selecting a runtime or replacing a Project Skill. A target mismatch, incomplete Methodology or Skill directory, hook, partial staging, permission failure, or missing Journal receipt stops before image build or testing.",
        "prose_claim": null,
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    }
  ]
}
```
