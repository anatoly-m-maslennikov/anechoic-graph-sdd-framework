---
atom_family: SPEC
atom_id: AN-S-2003
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 16
  updated_at: 2026-11-04 05:21:15 +0400
---
## Summary

Define Project.Framework Settings.Framework Control-Root Locator

## Claim

### Prose Claim


the Project's framework control-root reference in Framework Settings.



### Formal Claim

```CFEL
# model
Project.Settings.Framework Control-Root Locator:: [string]{::0..1};

Project.Settings.Framework Control-Root Locator.*[]{::0}
```

## Details

Evidence: CA-D-370 requires the locator to resolve to the Directory Carrier prescribed by CA-D-317 without selecting another authority root. Candidate #6 keeps concrete ANECHOIC mechanisms in Project Configuration. This definition adds no path or alternative authority root; those remain Delivery rules.
