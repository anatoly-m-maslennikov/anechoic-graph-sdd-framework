---
identity:
  atom_id: AN-S-3013
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:05:07.161317+00:00'
---
## Summary

Define an ordinary Package Spec

## Claim

### Prose Claim

A **Specified Package**, also called a **Specified PKG**, is an ordinary Package in Realization whose boundary is defined by exactly one Package Spec (PKG Spec Atom).

The Package Spec records the Package’s stable ID, a short Purpose, and a Contract. It belongs in the owning Component’s Spec Section. Use a lens allowed by that Component’s effective whitelist. The Spec Atom retains its own stable Atom ID when its lens or name changes. The package ID is separate from its descriptive name.

Place the Specified Package immediately under its Component Package in Realization and include the package ID in the directory name, for example `create_order_pkg3344`. An ordinary Package may later become a Component.

A Specified Package keeps its implementation, tests, and Spec Binding file in
its own directory. If it has tests, put them in a direct subdirectory. To get
the test directory name, append `__tests` to the complete Specified Package
directory name, including its package ID.

Put the Spec Binding file at the root of the Specified Package. To get the file
name, append `__spec_bind.yaml` to the complete Specified Package directory name.

Put test assets, including fixtures and corpora, in the `assets/` subtree of the
test directory. Classify all files in that subtree as test assets, including
source files used as test inputs. Put test source files outside `assets/` within
the test directory and classify them as test code. Test total is the sum of test
code and test assets.

## Details

Acceptance: a PKG Spec in an owning Component’s Spec Section records package ID `pkg3344`, a short Purpose, and a Contract under an enabled lens; `create_order_pkg3344` is directly under the Component Package. Moving it beneath another ordinary Package fails the stated placement.

`create_order_pkg3344/` contains `create_order_pkg3344__tests/` and
`create_order_pkg3344__spec_bind.yaml`. In the test directory, classify
`test_create_order.py` as test code and `assets/input.py` as a test asset.

Sources: CA-A-1462@1-draft, CA-A-1463@1-draft. Task: CA-P-3083.
