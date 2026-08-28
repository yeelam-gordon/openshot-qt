# IMPLEMENT r2 assignment

## objective

Address every manager-accepted IMPL-REVIEW r1 finding without silently redesigning the immutable approved design.

## inputs

- Exact accepted findings: `Generated Files\hackathon-fleet\agents\hackathon-implementation-reviewer\output\IMPL-REVIEW.r1.md`
- Current implementation report: `Generated Files\hackathon-fleet\agents\hackathon-implementer\output\IMPLEMENT.r1.md`
- Immutable design: `Generated Files\hackathon-fleet\agents\hackathon-fix-designer\output\DESIGN.r3.md`
- Implemented four top-level generated documents

## constraints

- Do not launch subagents, edit product code, or edit the manager workboard.
- IMPL-001 is accepted unchanged and invalidates an immutable design assertion. Do not silently change that assertion as if DESIGN r3 required it; return a formal design-change request and identify the exact safe correction and blocked gates.
- Correct IMPL-002 by copying the exact ordered 60 per-frame hashes from DESIGN r3 into the top-level appendix, preserving order, LF manifest rule, and aggregate hashes.
- Make only authorized top-level documentation edits plus the required output record.

## expected_output

- Correct IMPL-002 in `Generated Files\appendix-references.md` and any directly inconsistent top-level reference.
- Write `Generated Files\hackathon-fleet\agents\hackathon-implementer\output\IMPLEMENT.r2.md` with finding dispositions, commands/results, and a formal design-change request for IMPL-001.

## acceptance_evidence

- Exact automated comparison proves all 60 hashes are present in order and aggregate values are unchanged.
- `git diff --check` passes and no product code is modified.
- IMPL-001 remains explicit and is not mislabeled resolved.
- End with `confidence: high|medium|low` and one sentence justifying it.
