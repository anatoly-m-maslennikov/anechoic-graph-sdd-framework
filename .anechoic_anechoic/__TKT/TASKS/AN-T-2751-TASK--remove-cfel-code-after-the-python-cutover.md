---
identity:
  atom_id: AN-T-2751
context:
  container:
    atom: AN-T-2221
  tier: 3
  template: task
state:
  status: active
  version: 1
  updated_at: '2026-11-13T17:14:03.749993+00:00'
---
## Summary

Remove CFEL code after the Python cutover

## Work

Move the remaining CFEL-dependent Workbench, Lifecycle, graph and build readers to the native Python Model from CA-P-3055 and the migrated Claims in CA-P-3022. Once their replacement inputs are ready, delete CFEL readers, parsers, compilers, Python-to-CFEL translation, and CFEL-only build hooks, tests and fixtures. Verify the image builds, the affected consumers work, and the build and runtime have no CFEL dependency.

## Progress

The generated Python Model loads inside the isolated ANECHOIC image as its normal runtime user. Lifecycle reads Header order from Current Declarations and checks real Carriers with and without Label. The image remains a local verification build.

Lifecycle now reads native Python for Status, Role/Form, Header, Content and
placement. Entity Graph and the Claim linter read structured Python helper
calls. A pinned comparison of 3,676 Graph carriers matched the prior graph,
including Delivery sources and all 36 Relations. The Graph suite passed 214
tests and Lifecycle passed 237 tests. The generated Model matched byte-for-byte.

Workbench still uses the shared CFEL translator for its schema build. CA #8
has the cutover details. Legacy CFEL fence readers remain until source retirement.

Graph no longer imports the legacy compiler for native Claims. The Graph suite
passed 218 tests after the containment and narrowing updates. Lifecycle passed
238 tests, Model validation passed 41 and the Model generator passed 34.
The 76 Scope Unit carrier headers wait for an image with the new Topic reader.

Isolated image `sha256:46fe79f3d8b61f10c3c5678f3eedeab4ef19aff8d5df080875e5af5d0c59f951`
built and loaded the generated Model, Lifecycle candidate schema, and
Workbench schema as the normal runtime user. Deployment verification is pending.
