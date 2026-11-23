---
atom_family: SPEC
atom_id: AN-S-3830
container:
  component: C16
tier: 4
context:
  lens: DES
state:
  status: archived
  version: 8
  updated_at: 2026-09-17 20:06:20 +0000
---
## Summary

Register immediate executable Tool folders

# Register immediate executable Tool folders

**every** immediate canonical folder under `102_FRAMEWORK_ENGINE/201_PROGRAMMATIC/201_TOOLS/` that owns one independently executable deterministic Tool entrypoint **must** have a one-to-one binding **to** an immediate unordered Tool Scope Unit owned by TOOLS **and** declared **in** authoritative Project Structure under CA-R-1483 **and** CA-R-1484.

- verify the observed folder **and** executable against that declaration; their presence alone **must not** establish a Scope Unit **or** admit a Tool.
- a declared Tool Scope Unit remains declared **when** its executable **or** Directory Carrier is absent; report missing materialization separately **without** claiming an executable Tool is available.
- an admitted Tool is active by default **and** **may** be excluded from the active Tool frontier **only** by explicit current Project authority **or** Configuration.
- shared libraries, caches, tests, **and** migration collections that do **not** own one canonical independently executable Tool entrypoint **must not** be classified as Tool Scope Units merely from their observed folders.

an absent **or** invalid Project Structure declaration blocks admission; do **not** create declarations **or** infer them from the folder scan.
