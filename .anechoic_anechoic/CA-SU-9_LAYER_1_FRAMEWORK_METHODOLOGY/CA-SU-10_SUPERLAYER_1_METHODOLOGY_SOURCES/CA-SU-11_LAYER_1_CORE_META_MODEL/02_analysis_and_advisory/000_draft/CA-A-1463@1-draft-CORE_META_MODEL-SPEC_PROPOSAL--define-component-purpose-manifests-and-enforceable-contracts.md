---
identity:
  atom_id: CA-A-1463
  ref_id: CA-A-1463@1-draft
context:
  container:
    scope_unit: CA-SU-11
  role: analysis_and_advisory
  form: Spec Proposal
  topics:
    main_subject: MODEL//ANECHOIC <+ Atom
  tier: 3
state:
  status: draft
  version: 1
  updated_at: '2026-11-16T21:31:32.278582+00:00'
destination:
  file:
    name: CA-A-1463@1-draft-CORE_META_MODEL-SPEC_PROPOSAL--define-component-purpose-manifests-and-enforceable-contracts.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/02_analysis_and_advisory/000_draft
---
## Summary

Define Component purpose, manifests, and enforceable contracts

## Proposal

A Component has a **Component Spec Section** and a **Component Package** in
the Realization. Components can contain child Components. Their code can
also contain ordinary Packages. A Module is one source file. A Unit is a
function, class, or method.

### Purpose, Manifest, and Contract

- **Component Purpose** (Tier 0) states why the child Component exists. A child
  Component can start with a Manifest and add one Purpose later. Put its
  responsibilities and obligations in the Purpose details.
- **Component Manifest** (Tier 0) declares the child Component’s existence,
  stable ID, name, `parent`, and layer where applicable.
- **Project Goal** and **Project Manifest** are Tier −1. The Goal is the
  Project’s Purpose. The native runtime selects one Active Project Manifest
  with `context.template: project_manifest`. Its formal Python Claim
  declares `name` and `prefix` plus any other Project configuration.
  Keep at most 20 parameters in total.
- **Contract** states a concrete guarantee. When a child Component has a
  Purpose, its Contracts collectively meet it. Tier 1 is the working placement
  for child Component Contracts. An optional **Demand** records a consumer’s
  need from a producer. A producer Contract can fulfill the Demand.

At the Project root, Applicable Principles guide decisions independently of
Contracts. Use a Contract when the Project exposes a concrete guarantee.

The parent Component contains the child’s Purpose and Manifest in its own
Component Spec Section. Both Atoms identify the child they describe.
Resolve a Component’s settings from the Manifest that describes it. Manifests
and Purposes are Spec Atoms. A local extension that defines a new kind of
Component belongs in the Project’s meta-model in PMETA.

For Workbench, a Purpose can call for timely query feedback. An Internal Contract
can set a memory budget. A Public Contract can guarantee query latency for
callers that need it.

### Component names and directories

Migrate Scope Unit IDs to Component IDs using the existing number. For
example, `CA-SU-43` becomes `C43`.

Compose the logical Component `Name` from its Label and name. Allow
conditional prefixes and postfixes when deriving `Name`. Policy filters
can match the logical name, for example `component.name: ADAPTER_*`.

Use the logical Name and stable Component ID in the directory layout.

```text
(LAYER_<layer number>)_<Name>_C<ID>
```

The Layer prefix is optional.

### Package Spec

Give an ordinary Package one `PKG` Spec Atom when it needs a specified
boundary. Include its stable package ID, a short Purpose, and its Contract.
Keep that Atom in the owning Component’s Spec Section. The Package can
later become a full Component.

Place a specified Package immediately under its Component Package. Include
its ID in its Realization directory name, for example `create_order_pkg3344`.
The ID and the descriptive name are separate.

### Visibility and dependencies

Component Packages and ordinary Packages can declare boundaries. Visibility
governs access from other packages. Resolve `parent` and `siblings` in the
package tree. An explicit allowlist can name stable Package or Component IDs.
A Component ID selects its Component Package.

| Visibility | Access from other packages |
|---|---|
| `internal` | Immediate parent and siblings |
| `internal: [parent]` | Immediate parent only |
| `internal: [siblings]` | Immediate siblings only |
| `public` | Any caller |
| `public: [C43]` | Only the named caller |

Both visibility modes accept allowlists. An explicit allowlist selects the
consumers for that entry. Omitted visibility defaults to Internal for every
Package, including Component Packages, Packages with a Spec, and ordinary
Packages. This also applies to explicit SPEC exports. Use `public` to grant
Public access.

A caller can restrict its dependencies with import allowlists or denylists.
A Component’s caller-side rules apply to its own modules and ordinary
Packages at every depth. Child Components inherit these rules throughout
the Component tree. An import must pass the provider’s visibility rule and
every applicable caller-side rule, including inherited rules. A child
Package can expose an entry directly to an allowed caller in another
Component.

For a Unit-level export, callers import the named Unit directly. If a
Contract exports only `billing.api.run`, allow
`from billing.api import run`. Importing `billing.api` as a Module requires
a Module-level export. Check each named import against its own export.

Visibility and protocol are independent. Import is the default protocol. Other
protocols can include HTTP REST, CLI, MCP, and TUI. Deployment controls network reach.

`child_of` links a Component to its `parent` Component. The inverse gives
the parent's `children`. `contained_by` links an Atom to its `container`,
which can be a Component or another Atom. Within an ordered sibling group,
a layer can import only from upstream siblings (lower layer numbers).
Downstream imports are forbidden even when an export is Public. Upstream
imports still require provider visibility and caller permission. Unordered
siblings have no layer restriction. Each Atom’s tier is local to its
containing Component.

### I/O allowances

A Component Manifest has one `io_allowance`. It applies to the Component’s
own modules and ordinary Packages. A child Component inherits its parent’s
allowance by default and can declare a different allowance in its Manifest.
An ordinary Package can further narrow the allowance it inherits.

```yaml
io_allowance:
  input: [db, api]
  output: [db]
```

An allowlist such as `io_allowance: [db, api]` applies to both directions.
`input` covers reads and receives. `output` covers writes and sends.
Use `[]` or `false` to deny all direct I/O. An omitted direction inherits
that direction from the parent. The default without an ancestor is `all`.

For REST calls, use `api` input for `GET`, `HEAD`, and `OPTIONS`.
Use `api` output for `POST`, `PUT`, `PATCH`, and `DELETE`.
A read-only fetch is input. Classify the operation once, regardless of
which way its request and response travel.

To limit child Components, write a Spec Policy that selects their
Component Manifests in the parent’s Spec Section. Validate each selected
Manifest’s effective allowance against that Policy. Report a violation
with the direction, channel, and Policy. Keep the authored allowance intact.

Block imports of I/O libraries for channels forbidden in both directions.
Use permitted adapters for I/O outside the direct allowance. Exact channel
definitions and enforcement remain open.

### Contracts and trace sidecars

SPEC defines explicit Contracts, including their visibility. Sidecars trace
Spec Atoms to existing Realization, such as a module or unit. A sidecar can
record `implemented` and `applied` bindings. Version pins identify exact
Atom revisions. Mapped QA checks supply evidence for Contract behavior.

When SPEC declares a Package’s export list, cross-package callers use that
list. An explicitly empty list closes access from other Packages. Contracts
that omit the export list, such as a latency guarantee, leave filename-based
visibility in effect.

Without a SPEC export list, root modules can self-declare visibility using
`<name>__<visibility>.<extension>`. The reserved visibility values are
`internal` and `public`. The extension is the module’s normal file extension.
In this case, only marked root modules are eligible for cross-package access.
Other Packages use the Internal default when neither an export list nor a
filename marker is present.

Use the normal Python module name including the suffix, such as
`from billing import orders__public` for `billing/orders__public.py`.

### Source notes

Gemini transcript lines 3596–3604, 12895–12932, 14421, and 15242–15479.
Second brainstorm, lines 533, 949, and 1073, for Manifest size and local tiers.
Third brainstorm, lines 719–1119, 1379, 1500, 1603, 1742, and 1894, for access and sidecars.
Fourth brainstorm, lines 155–223, 294, 363, 507, 557, 610–614, 668, 723,
850, 930, 997, 1081, 1203, 1301, 1372, and 1492.
