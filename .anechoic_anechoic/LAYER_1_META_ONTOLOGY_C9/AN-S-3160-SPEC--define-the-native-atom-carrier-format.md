---
identity:
  atom_id: AN-S-3160
context:
  container:
    component: C9
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-20T17:01:14.806545+00:00'
---

## Summary

Define the native Atom Carrier format

## Claim

The Atom Carrier is the source of truth. The YAML Header carries the
Atom's Properties. The Markdown Content follows the Header.

### Header order

1. `atom_family` is required. Use SPEC, TKT, or PMETA.
2. `atom_id` is required. Its project prefix and numeric identity remain
   stable. Its family marker is S, T, or P and agrees with Atom Family.
3. `concern` is optional on Atom. An explicit Concern names its subject,
   path, and relation, in that order.
4. `structure` contains the required Container, then Tier when a SPEC Atom
   declares it. A Container references one Component or Atom.
5. `context` carries Template, then Lens. TKT and PMETA require Template.
   SPEC can declare Template according to its Template rule. Lens belongs
   to SPEC.
6. `relations` is optional on Atom. Each entry follows the target reference
   form and endpoint rules of its declared Relation.
7. `state` carries Status, Version, and Updated At, in that order.

Priority is a TKT Property. Concern carries its subject, path, and relation.

### Content

The Package Spec declares its Package ID in the Formal Claim. Its Purpose
and Contract remain authored in their Markdown sections. The Realization
uses its Spec Binding to identify the exact Spec revision.

### Materialized Views

The Atom ID, Header, Content, and declared Project Structure determine
the filename and location. The files and directories materialize that
placement. Destination and Ref ID are computed values. Ref ID derives from
Atom ID, Version, and Status. A Draft suffix identifies a Draft revision.

### Migration

Apply this layout after the native tools can read and write it. Compare
migrated authored values to exact Git revisions through the migration
bindings. Restore admitted values and preserve evidence for unresolved
fields. Preserve Atom IDs, exact revision references, and Markdown Content
during a mechanical format migration.

## References

AN-T-2929, AN-S-3118, AN-S-2181, AN-S-3013, AN-S-3014.
