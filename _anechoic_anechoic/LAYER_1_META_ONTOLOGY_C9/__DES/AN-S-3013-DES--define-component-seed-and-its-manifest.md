---
atom_family: SPEC
atom_id: AN-S-3013
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-22T09:00:09.209014+00:00'
---

## Summary

Define Component Seed and its Manifest

## Claim

### Prose Claim

An ordinary Package becomes a **Component Seed** when it gains its first
Manifest. A Component Seed can become a Component with a Component Manifest.

A Component Seed has one Manifest Atom in the SPEC Lens of its owning
Component. Use three Markdown sections in this order.

1. `## Formal Manifest` declares its ID and any boundaries. The ID uses
   `CS` followed by ASCII digits, for example `CS123`.
2. `## Purpose` states why the Component Seed exists.
3. `## Solution` states how it fulfills its Purpose.

The Manifest has its own stable Atom ID. Place the Seed directly under its
owning Component Package in Realization. Append its ID to its Package
name, for example `create_order_CS123`.

A Component Seed keeps its implementation, tests, and Spec Binding file in
its own directory. If it has tests, put them in a direct subdirectory. To get
the test directory name, append `__tests` to the complete Component Seed
directory name, including its Component Seed ID.

Put the Spec Binding file at the root of the Component Seed. To get the file
name, append `__spec_bind.yaml` to the complete Component Seed directory name.

Put test assets, including fixtures and corpora, in the `assets/` subtree of the
test directory. Classify all files in that subtree as test assets, including
source files used as test inputs. Put test source files outside `assets/` within
the test directory and classify them as test code. Test total is the sum of test
code and test assets.

## Details

`create_order_CS123/` contains `create_order_CS123__tests/` and
`create_order_CS123__spec_bind.yaml`. The binding pins the exact Manifest
revision. Classify `test_create_order.py` as test code and `assets/input.py`
as a test asset.

Sources: CA-A-1462@1-draft, CA-A-1463@1-draft. Task: CA-P-3083.
