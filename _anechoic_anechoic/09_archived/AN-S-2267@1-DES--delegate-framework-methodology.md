---
atom_family: SPEC
atom_id: AN-S-2267
container:
  component: C00
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: '2026-11-12T15:04:13+00:00'
---

## Summary

Delegate FRAMEWORK_METHODOLOGY

## Claim

### Prose Claim

Project//anechoic assigns Scope Unit//FRAMEWORK_METHODOLOGY responsibility for defining how Projects are represented and operated, including the Methodology used to develop ANECHOIC and its own Methodology. Project//anechoic remains its direct containing Scope Unit and retains its wider scope and accountability. FRAMEWORK_METHODOLOGY retains its own realization.

In addition to the applicable model defaults, the admitted local Role/Form pairs are exactly:

- Requirement / Rule;
- Requirement / Goal;
- Method / Direct Policy.

The admitted HAS_ACTIVE_SUBJECT targets are exactly the endpoint objects at these typed addresses:

- `Aspects <+ Product`;
- `Scope Unit//FRAMEWORK_METHODOLOGY`;
- `Scope Unit//METHODOLOGY_SOURCES`.

Each address selects only its endpoint object, not its descendants or other members of its kind. An unresolved address grants no admission. These local permissions apply only when Header.Container resolves to FRAMEWORK_METHODOLOGY. The applicable default admission of Scope Delegation and supporting Plan / Work Report remains unchanged.

### Formal Claim

```CFEL
# instances
Scope Unit//FRAMEWORK_METHODOLOGY.ID == "CA-SU-9";

Scope Unit//FRAMEWORK_METHODOLOGY.Name == "FRAMEWORK_METHODOLOGY";

Scope Unit//FRAMEWORK_METHODOLOGY.Label == "LAYER";

Scope Unit//FRAMEWORK_METHODOLOGY.order.ordered == true;

Scope Unit//FRAMEWORK_METHODOLOGY.order.number == 1;

Scope Unit//FRAMEWORK_METHODOLOGY ((IS_CONTAINED_BY)) Project//anechoic
```
