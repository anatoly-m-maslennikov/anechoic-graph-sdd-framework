---
atom_family: SPEC
atom_id: AN-S-2233
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 8
  updated_at: 2026-11-09 00:03:55 +0400
---
## Summary

Deliver Atoms to Markdown files

## Claim

### Prose Claim

The selected Carrier is the Markdown file delivering the selected Atom. Its filename includes the extension, and its location is the containing directory relative to the repository root.

Deliver the complete Header recursively as YAML frontmatter, preserving its declared nesting. Deliver declared Content Properties as Markdown sections.

For YAML, encode names and named values in lowercase words joined by single underscores. This is Carrier encoding; canonical model names and object identities retain their meaning. IDs, opaque references, free text and typed scalar data retain their exact values. Carrier metadata retains its exact spelling, including filenames, paths and locator values copied into Header destination fields.

### Formal Claim

```CFEL
# instances
Atom//$atom >> Carrier//$carrier;

$atom.Header >> $carrier.frontmatter;

$atom.Content >> $carrier.markdown;

$carrier.filename == $atom.Header.Destination.File.Name;

$carrier.location == $atom.Header.Destination.File.Path
```

## Details

The file layout is:

```text
---
<yaml>
---
<markdown>
```
