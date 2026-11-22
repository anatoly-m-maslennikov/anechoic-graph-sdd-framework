---
atom_family: SPEC
atom_id: AN-S-3310
container:
  component: C00
tier: 2
context:
  lens: DevOps
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-22T10:29:51.115829+00:00"
---

## Summary

Isolate Python roots and environments by Project child

## Solution

Engine Studio, Release, and Setup are separate uv Projects. Each child
owns one Python import root, one virtual environment, and its executable
entry points. Define these in the owning child.

Run each executable through uv in its owning Project. Engine Studio
exposes runtime and test commands. Release exposes image build, Local
Release, and Public Release. Setup exposes installation.

A child calls another child through its CLI or API. For example, Release
invokes the Engine Studio test executable in the Engine Studio environment.
The Import Graph resolves each child's code from that child's Python root.

Build the Engine Studio virtual environment inside its Docker image using
the Engine Studio dependency lock.

## References

AN-T-2977, AN-T-2980, AN-T-2983.
