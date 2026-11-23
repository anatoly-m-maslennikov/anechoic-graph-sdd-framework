---
atom_family: SPEC
atom_id: AN-S-2002
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

Define Project.Framework Settings.Confidence

## Claim

### Prose Claim


the Confidence grouping in the Project's Framework Settings.



### Formal Claim

```CFEL
# model
Project.Settings.Confidence{::0..1}:: []{::0};

Project.Settings.Confidence.*[in (Necessary Information Threshold, Semantic Resolution Threshold)]{::0..2};

Project.Settings.Confidence.*:: [int]
```

## Details

Evidence: CA-R-1652 defines the necessary-information threshold default; CA-R-380 defines the semantic-resolution threshold default. These define the child settings, not the parent grouping. Candidate #6 decision 8 retains Settings as the default source, and decision 18 distinguishes Project settings from the framework's name. This grouping adds no threshold, override layer or mandatory value. Concrete ANECHOIC setting definitions belong in Project Configuration.
