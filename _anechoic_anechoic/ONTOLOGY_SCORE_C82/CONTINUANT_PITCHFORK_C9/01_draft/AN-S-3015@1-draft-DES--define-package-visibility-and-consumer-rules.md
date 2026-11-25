---
atom_family: SPEC
atom_id: AN-S-3015
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:05:13.637753+00:00'
---
## Summary

Define package visibility and consumer rules

## Claim

### Prose Claim

Component Packages and ordinary Packages can declare access boundaries. Omitted visibility defaults to internal for Component Packages, specified ordinary Packages, and ordinary Packages without a Spec, including explicit SPEC exports. Internal permits immediate parent and siblings; `internal: [parent]` permits only the immediate parent, and `internal: [siblings]` only immediate siblings. Public permits any caller. An explicit allowlist selects consumers for that entry; both visibility modes accept allowlists, and a Component ID selects its Component Package. Resolve parent and siblings in the package tree.

A caller may restrict dependencies using import allowlists or denylists. A Component’s rules apply to its own modules and ordinary Packages at every depth and are inherited throughout the child Component tree. Each import must pass the provider’s visibility and every applicable caller rule. An allowed external caller may directly access a child Package entry.

## Details

Acceptance: an unconfigured package permits an immediate sibling and rejects an unrelated package; `internal: [parent]` rejects a sibling; `public` permits an unrelated caller unless an applicable caller rule denies the import; `public: [C43]` permits C43 and rejects another caller. A parent Component denylist applies to nested ordinary Packages and a child Component even if their provider permits access.

Sources: CA-A-1463@1-draft. Task: CA-P-3084.
