---
atom_family: SPEC
atom_id: AN-S-3303
container:
  component: C30
tier: 0
context:
  template: component_contract
  lens: SWD
relations:
  ANSWERS:
  - AN-S-3069
state:
  status: "archived"
  version: 15
  updated_at: "2026-11-26T15:54:01.356278+00:00"
---
## Summary

Read guarded filesystem inputs

## Guarantee

Open admitted filesystem paths without following symbolic links. A bounded read checks its declared roots and read limits, refuses protected paths, and records input fingerprints. A caller can check whether its recorded inputs still match the filesystem.

Parse UTF-8 YAML frontmatter within fixed syntax limits. Refuse aliases,
merge keys, duplicate keys, and non-string mapping keys. Return header
data and body text for the caller to interpret.

Read and write TOML settings carriers. Validate a replacement before
publishing it.

Append Journal rows to Project-local files in input order or stage them
for the database owner. Return receipts for completed appends. Report
partial completion when a batch stops.

Read grouped and historical Header fields without altering the carrier.
Reject conflicting aliases. Read legacy Atom identifiers. Given an admitted Atom ID, version, and
Status, return its exact reference in the form `<atom-id>@<version>`.
Append `-draft` for Draft. This operation has no file effects.

Read native Headers and derive Carrier filenames and directories from
the supplied fields. Preserve the legacy filename grammar and reject
unsupported paths or contradictory fields.

Read authored Component Contracts and recognize legacy Scope Unit carriers.
Parse and render Subject notation with the selected grammar profile.

Read the legacy Project Settings selected for the current request.
Parse legacy Python Claims as literal calls and preserve their
Model or Instance grouping.

Read native Model Claims and Structure declarations without executing them.
Check Dependencies Declarations against the reviewed callback source.
Read one published Structure snapshot into a read-only value. Refuse
malformed JSON and invalid Component or Package records.
Map realization paths to declared Component and Package owners. Retain
the source pins when discovering legacy Scope Unit declarations.

Capture Project carriers with their revisions, containment and source pins.
Report invalid sources and refuse a capture if the Manifest or carrier
inventory changes during the read. Decode Markdown headings and retain
the source ranges for declared Content properties.

Read literal placement rules, property order, and dataclass field contracts
from Model Claims. Decode cardinality bounds and normalize Model addresses.

Read and decode active Project Manifest carriers from guarded inputs.
Allocate temporary files under the selected Project on the destination
filesystem. Observe changes in selected directories and return their
old and new paths to the caller.

Index Relation Declarations and their inverse names. Refuse duplicate
names, unresolved derivations, and Relations that derive from themselves.

Read Current legacy carriers with their exact source bytes and pins.
Select Model Declarations and verify any explicit Draft overlay against
its predecessor and revision pins.

## Claim

### Formal Claim

The following Lean claim covers only `frontmatter_bounds` and `source_body`
in `carrier_body__pub.py`. Each `Nat` in an input list denotes one byte
(0 through 255). `missingDelimiter` represents no bounds or the explicit
unsupported-delimiter error; the `path` supplied to `source_body` is used
for the error message. It is not read as a file.

```lean
import Lean

namespace CarrierBodyContract

-- Byte offsets are zero-based; the separator belongs to the closing boundary.
def openingEnd (raw : List Nat) : Option Nat :=
  if raw.take 4 == [45,45,45,10] then some 4
  else if raw.take 5 == [45,45,45,13,10] then some 5
  else none

-- A closing line is exactly three hyphens with an LF or CRLF terminator.
def closingEnd (raw : List Nat) (separator : Nat) : Option Nat := do
  let afterSep ← if (raw.drop separator).take 2 == [13,10] then some (separator + 2)
    else if (raw.drop separator).take 1 == [10] then some (separator + 1)
    else none
  if (raw.drop afterSep).take 3 != [45,45,45] then none
  else if (raw.drop (afterSep + 3)).take 2 == [13,10] then some (afterSep + 5)
  else if (raw.drop (afterSep + 3)).take 1 == [10] then some (afterSep + 4)
  else none

def bounds (raw : List Nat) : Option (Nat × Nat × Nat) := do
  let opening ← openingEnd raw
  let start ← ((List.range raw.length).drop (opening - 1)).find? (fun i => (closingEnd raw i).isSome)
  let stop ← closingEnd raw start
  some (opening, start, stop)

inductive Outcome where
  | missingDelimiter
  | body (bytes : List Nat)
  deriving Repr, BEq, DecidableEq

def body (raw : List Nat) : Outcome :=
  match bounds raw with
  | none => .missingDelimiter
  | some (_, _, stop) => .body (raw.drop stop)

-- Project-level effect guarantee: these operations make no Project state changes,
-- filesystem accesses, or network accesses. This is an implementation obligation;
-- the pure definitions above do not establish it for the Python implementation.
end CarrierBodyContract
```

## References

AN-S-3069 and AN-T-2944.
