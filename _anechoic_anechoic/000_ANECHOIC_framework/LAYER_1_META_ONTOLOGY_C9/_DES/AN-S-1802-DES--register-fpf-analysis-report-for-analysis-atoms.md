---
atom_family: SPEC
atom_id: AN-S-1802
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: "active"
  version: 18
  updated_at: "2026-11-25T23:19:16.092286+00:00"
---
## Summary

Register FPF Analysis Report for Analysis Atoms

## Claim

### Prose Claim


the ANECHOIC Project Configuration contribution to `Atom/(.Header.Role := "Analysis & Advisory").Header.Form`.


the ANECHOIC Project Configuration **must** register FPF Analysis Report as an additional value of `Atom/(.Header.Role := "Analysis & Advisory").Header.Form` for legacy reports. Use the native analysis report Template under AN-S-1805 for new reports. this registration does **not** change the Core contribution under CA-R-1232@28 **or** create another Form Property.

## Details

CA-R-1889 defines the registered Form. Apply the native filename grammar under AN-S-3160. The Form remains within Role Analysis & Advisory.

