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
- **Contract** states a concrete guarantee. The Project and each child
  Component use Tier 0 Contracts to state what they provide. When a child
  Component has a Purpose, its Contracts collectively meet it. An optional
  **Demand** records a consumer's need from a producer. A producer Contract can
  fulfill the Demand.

Tier 1 holds a Component's main Policies, Standards, and Solutions for how it
provides its Contracts. Project Applicable Principles belong at Tier 1 under
the Project Contracts. See CA-A-1461 for the proposed Project Contracts.

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
later become a full Component by Operator decision. Size and complexity can
suggest that change. A small Package can need a Spec when it is critical.

Place a specified Package immediately under its Component Package. Include
its ID in its Realization directory name, for example `create_order_pkg3344`.
The ID and the descriptive name are separate.

### Manifest Runtime

Manifest Runtime (C62) is a child of Kernel Mixer (C59). It contains three
ordinary Packages, each with its own `PKG` Spec Atom. Run the Hosts as
separate, long-lived processes. Each Host imports only what it needs to
load and serve its output.

- **Manifest Compiler** compiles Active SPEC Anechoic Python eDSL into small
  Model modules and a Structure snapshot validated against that Model. Reuse
  the source watcher to trigger compilation in a short-lived process.
- **Model Host** provides the Model types and rules that implementation
  and validators import. Activate a new Model by restarting the Model Host
  and consumers that imported the previous Model.
- **Structure Host** publishes the current validated Structure through a
  read-only snapshot API. It swaps in a valid snapshot without a restart and
  keeps the last valid one on failure. Each operation reads one snapshot at
  its start and uses it until completion.

The Compiler writes complete local artifacts before either Host publishes
them. A Structure snapshot records its source revisions and Model fingerprint.
Structure reload leaves the consumers and database running. Startup settings
such as the MCP port still take effect at runtime restart.

Before the first release, reconcile Active Model declarations with Component
and Manifest rules. Use those Active declarations as the Compiler inputs.
Preserve superseded Scope Unit and Project Settings declarations in history.

### Boundary Allowlists

Use `boundaries` for the three allowlists of a Component or Package.
CA-P-3075 specifies and delivers Code Access. AN-T-2921 owns the State and
runtime I/O designs and their enforcement.

- `code_access` governs code imports and exports.
- `shared_state` governs access to shared state.
- `runtime_io` governs read and write operations for Server and Client.

#### Code Access

`imports` lists what code a Package may import. `exports` lists the Modules
and Units it makes available and the callers that may import them. Resolve
`parent` and `siblings` in the package tree. An allowlist can name stable
Package or Component IDs. A Component ID selects its Component Package.

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

An import allowlist limits the dependencies of the caller.
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

Runtime protocols such as HTTP REST and MCP belong to `runtime_io`.
Deployment controls network reach.

`child_of` links a Component to its `parent` Component. The inverse gives
the parent's `children`. `contained_by` links an Atom to its `container`,
which can be a Component or another Atom. Within an ordered sibling group,
a layer can import only from upstream siblings (lower layer numbers).
Downstream imports are forbidden even when an export is Public. Upstream
imports still require provider visibility and caller permission. Unordered
siblings have no layer restriction. Each Atom’s tier is local to its
containing Component.

#### State

`shared_state` allows read and write access to shared state, such as
global variables, singletons, and ambient channels. Use `pure` to allow no
shared state. Check access statically where possible, even without an import
edge. Other State values and the exact checks remain open.

#### I/O

Use `server` and `client` under `runtime_io`. Server provides operations.
Client requests operations or accesses resources, such as files. Each role
can allow read, write, or both. A Component can use separate read and write
servers. A read-only request remains read-only when the server sends a response.

The allowance applies to the Component's modules and ordinary Packages.
Child Components inherit it by default. A child Component can declare its
own allowance. An ordinary Package can narrow its inherited allowance.
An omitted role inherits the corresponding role. The default without an
ancestor is `all`. Use an empty allowance to deny direct I/O.

A parent can use a Spec Policy to limit the allowances in its child
Component Manifests. If an effective allowance violates the Policy, report
the role, channel, capability, and Policy. Preserve the authored value.
The exact channel notation and enforcement remain open.

### Contracts and trace sidecars

SPEC defines explicit Contracts, including their visibility. Sidecars trace
Spec Atoms to existing Realization, such as a module or unit. A sidecar can
record `implemented` and `applied` bindings. Version pins identify exact
Atom revisions. Mapped QA checks supply evidence for Contract behavior.

When SPEC declares a Package’s export list, cross-package callers use that
list. An explicitly empty list closes access from other Packages. Contracts
that omit the export list, such as a latency guarantee, leave filename-based
visibility in effect.

Without a SPEC export list, a Package uses the Internal default until it
adds a marked root module. A marker has the form
`<name>__<visibility>.<extension>`, with visibility `internal` or `public`
and the module's normal extension. Once a Package has a marked root module,
only its marked root modules are eligible for cross-package access.

Use the normal Python module name including the suffix, such as
`from billing import orders__public` for `billing/orders__public.py`.

### Source notes

Gemini transcript lines 3596–3604, 12895–12932, 14421, and 15242–15479.
Second brainstorm, lines 533, 949, and 1073, for Manifest size and local tiers.
Third brainstorm, lines 719–1119, 1379, 1500, 1603, 1742, and 1894, for access and sidecars.
Fourth brainstorm, lines 155–223, 294, 363, 507, 557, 610–614, 668, 723,
850, 930, 997, 1081, 1203, 1301, 1372, and 1492.
Fifth brainstorm, user prompts at lines 2, 111, 178, 594, 831, 968, 1105, 1174,
1295, 1397, and 1477.
