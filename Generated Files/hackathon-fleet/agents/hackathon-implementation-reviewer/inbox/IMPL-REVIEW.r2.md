# IMPL-REVIEW r2 assignment

## objective

Perform the second and final implementation review of the complete current documentation implementation and accepted finding dispositions.

## inputs

- Prior review: `Generated Files\hackathon-fleet\agents\hackathon-implementation-reviewer\output\IMPL-REVIEW.r1.md`
- Fix report: `Generated Files\hackathon-fleet\agents\hackathon-implementer\output\IMPLEMENT.r2.md`
- Current four top-level generated documents
- Immutable approved design: `Generated Files\hackathon-fleet\agents\hackathon-fix-designer\output\DESIGN.r3.md`

## constraints

- Do not edit any file or launch subagents.
- Do not edit the manager workboard.
- Re-review the complete implementation.
- Confirm IMPL-002 mechanically.
- Preserve IMPL-001 unless an approved immutable design correction exists; do not accept a silent divergence.
- This is the final implementation review round.

## expected_output

Write only `Generated Files\hackathon-fleet\agents\hackathon-implementation-reviewer\output\IMPL-REVIEW.r2.md` with each finding disposition, any new findings, PASS / REVISE verdict, blocked-gate consequences, product-code isolation, and confidence.

## acceptance_evidence

PASS requires zero open critical/high findings. If blocked, quote the exact remaining evidence and affected gates. End with `confidence: high|medium|low` and one sentence justifying it.
