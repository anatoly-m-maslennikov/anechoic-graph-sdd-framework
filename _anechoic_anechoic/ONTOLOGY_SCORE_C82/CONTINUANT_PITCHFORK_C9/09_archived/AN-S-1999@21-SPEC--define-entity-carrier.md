---
atom_family: SPEC
atom_id: AN-S-1999
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: "archived"
  version: 21
  updated_at: '2026-11-24T17:25:13+00:00'
---

## Summary

Define Entity/Carrier

## Semantics

A Carrier is a Folder or File that carries or represents a Graph entity. The Graph entity and the Carrier are distinct: a File or Folder does not become the entity it carries. The applicable representation and ownership rules identify the authoritative Carrier for each entity; a derived copy does not gain SSOT authority merely by representing that entity.

A File is executable or non-executable. An Executable File has Binary and Interpreted branches. A Binary is an executable binary artifact. An Interpreted file is executed directly by an interpreter.

A Non-executable File has Markdown, YAML, and TOML branches. Markdown has Markdown with YAML Front Matter and Plain Markdown branches. Source recognition for the Realization Graph is independent of Carrier classification and remains governed by its existing source-recognition rules.

A companion Folder may physically contain child Atom carriers while logical Atom ownership remains in the Graph. A sidecar correspondence can bind a Carrier to the represented Graph entity without making the Carrier the entity.

### Adoption and evidence

This is a design Draft. The existing scoped Carrier declaration remains authoritative until the proposed classification and correspondence are admitted.

Adoption requires one typed, scoped carrier per subject and a validated correspondence and binding migration. Authoring admission, compilation, and runtime admission must pass before cutover. Checks must cover executable files, interpreted files, binaries, derived copies, and source recognition. An unsupported classification or correspondence blocks adoption.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

class Carrier: pass
class Folder(Carrier): pass
class File(Carrier): pass
class ExecutableFile(File): pass
class Binary(ExecutableFile): pass
class Interpreted(ExecutableFile): pass
class NonExecutableFile(File): pass
class Markdown(NonExecutableFile): pass
class YAML(NonExecutableFile): pass
class TOML(NonExecutableFile): pass
class MarkdownWithYAMLFrontMatter(Markdown): pass
class PlainMarkdown(Markdown): pass
```
