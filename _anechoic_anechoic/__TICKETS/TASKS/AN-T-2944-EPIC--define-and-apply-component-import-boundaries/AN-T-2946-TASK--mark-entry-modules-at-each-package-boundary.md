---
atom_family: TKT
atom_id: AN-T-2946
container:
  atom: AN-T-2944
priority: 2
context:
  template: task
state:
  status: "in_queue"
  version: 10
  updated_at: "2026-11-22T16:06:07.956677+00:00"
---

## Summary

Mark entry Modules at each Package boundary

## Work

Give every Package with direct authored code exactly one direct
`__shared` entry Module. Apply the rule to Component Packages,
Component Seeds, ordinary nested Packages, and Test Packages.

Every import from another Package must target that entry and satisfy
the caller and provider Code Access rules. Keep implementation Modules
Package-local. Declare public or named exports on the same entry when
the Package Contract requires those callers.

Use the Realization Graph to verify entry counts and inbound imports
for each Package. Keep the existing module and function size checks.

## Verification

All 12 Beta implementation and Test Packages pass the entry and Code
Access checks. The local Realization Graph resolves Python, JavaScript,
TypeScript, and Svelte. The audit found 58 of 84 Packages with
one entry and no inbound imports to implementation Modules. It found
1,698 inbound sites to convert. The Structure reader and carrier
compatibility APIs now use the Adapters shared entry. Named C59
content and relation APIs and legacy C30 reader APIs use their
owning shared entries. The installed
image still needs the web parsers for web-language verification.

The static Test Suite traces named imports to the defining Package.
The first audit identified 65 pass-through imports. The check passed
after callers moved to the owning entries.

### Owner entry and visibility review

Route 20 TOOLS consumer imports and 74 Adapter import statements through
the defining Package entry. Preserve their existing Code Access. This
Realization Graph resolved 1,360 cross-Component import sites with zero
denied and zero unresolved. The 12 Beta production and Test Packages
pass both entry and Code Access checks. Across all 84 observed code
directories, 77 have exactly one entry and 1,544 inbound sites still
bypass an entry. The remaining work includes scope review for fixtures
and generated sources.

Use the public visibility review in AN-T-2958. The graph surfaced one
scoped candidate used by two external production families.
Keep `realization_component_paths` scoped to its Graph and Kernel users.
Its result exposes Framework ownership layout. Keep the already public
named exports unchanged.
