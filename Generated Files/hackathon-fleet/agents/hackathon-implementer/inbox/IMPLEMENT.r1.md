# IMPLEMENT r1 assignment

## objective

Implement the manager-approved DESIGN r3 in this documentation-only workspace by integrating its complete, current Windows Arm64 port plan into the user-facing generated documents.

## inputs

- Immutable approved design: `Generated Files\hackathon-fleet\agents\hackathon-fix-designer\output\DESIGN.r3.md`
- Approval: `Generated Files\hackathon-fleet\agents\hackathon-design-risk-reviewer\output\DESIGN-REVIEW.r3.md`
- Existing `Generated Files\goal.md`, `design-spec.md`, `files-to-update.md`, and `appendix-references.md`
- Accepted findings RISK-001 through RISK-008

## constraints

- Do not redesign or modify the immutable DESIGN r3.
- Do not launch subagents or edit the manager workboard.
- Do not edit product code anywhere in this or sibling repositories.
- Preserve separate PR ownership for openshot-qt, libopenshot, and libopenshot-audio.
- Integrate the approved baseline, ABI lock, BOM/ownership, exact file surfaces, gates G0-G13, package and hardware limitations, and honest status into the four existing generated documents.
- Avoid duplicating fleet records into new report formats.

## expected_output

- Update only the four existing top-level generated documents as needed.
- Write `Generated Files\hackathon-fleet\agents\hackathon-implementer\output\IMPLEMENT.r1.md` mapping each design requirement to changed files, listing commands/results, limitations, diff readiness, and confidence.

## acceptance_evidence

- `git diff --check` passes.
- `git status --short` shows no product-code modifications.
- All approved design sections have a discoverable home in the four top-level generated documents.
- Claims requiring Arm hardware or production credentials remain explicit gates, not claimed successes.
- End with `confidence: high|medium|low` and one sentence justifying it.
