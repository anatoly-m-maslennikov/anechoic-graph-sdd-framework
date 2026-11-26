---
atom_family: SPEC
atom_id: AN-S-2207
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 5
  updated_at: "2026-11-25T23:19:17.805562+00:00"
---
## Summary

Define Extension Sources Selection

## Claim

### Prose Claim


Extension Sources is the named Selection of immutable installed Extension source Atoms available as candidate inputs to methodology compilation. Membership establishes availability, not activation. Framework Settings separately selects activation and the installed source version for an Extension; Applicable Methodology separately includes only sources applicable under those settings.


### Formal Claim

```python
# model
subject_path(address="Named Selection//Extension Sources")
```

## Details

CA-R-1175 requires preservation of installed source versions as candidate inputs. CA-R-1228 governs the applicable Methodology subset, and CA-R-1724 separates installed availability from activation and version selection. This definition identifies their shared candidate population; it adds no activation procedure, new Scope Unit, or automatic conflict resolution.
