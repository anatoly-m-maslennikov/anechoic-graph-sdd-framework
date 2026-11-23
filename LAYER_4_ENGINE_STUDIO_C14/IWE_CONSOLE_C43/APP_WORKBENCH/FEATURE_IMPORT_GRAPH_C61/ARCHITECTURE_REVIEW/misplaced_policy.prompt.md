# Find decisions in the wrong layer

Use the [shared evidence prompt](review_evidence.prompt.md).

Find branches that decide eligibility, permissions, state transitions, or other
declared behavior. Compare the Component that makes the decision with the owner
named by the active Spec and its Spec Binding.

Look for the same decision repeated across entry points and for callers that bypass
the owning operation. Cite the decision branch and the evidence of ownership.
