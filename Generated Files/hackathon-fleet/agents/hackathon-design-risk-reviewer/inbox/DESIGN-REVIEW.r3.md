# DESIGN-REVIEW r3 assignment

## objective

Perform the third and final design review and determine whether DESIGN r3 can be frozen unchanged.

## inputs

- Final candidate: `Generated Files\hackathon-fleet\agents\hackathon-fix-designer\output\DESIGN.r3.md`
- Prior candidate: `Generated Files\hackathon-fleet\agents\hackathon-fix-designer\output\DESIGN.r2.md`
- Exact prior review: `Generated Files\hackathon-fleet\agents\hackathon-design-risk-reviewer\output\DESIGN-REVIEW.r2.md`
- Original accepted findings: `Generated Files\hackathon-fleet\agents\hackathon-design-risk-reviewer\output\RISK.r1.md`
- RISK-004 and RISK-005 corrections are relayed unchanged; all other resolved findings must remain resolved.

## constraints

- Do not edit product code or the manager workboard.
- Do not launch subagents.
- Preserve stable finding IDs and check the complete self-contained r3 design.
- This is the final permitted review round: issue GO only if no critical/high findings remain and confidence is high; otherwise issue NO-GO or scoped REVISE with exact evidence.
- Write only the required output record.

## expected_output

Write `Generated Files\hackathon-fleet\agents\hackathon-design-risk-reviewer\output\DESIGN-REVIEW.r3.md` with every finding disposition, any new findings, remaining severities, GO / REVISE / NO-GO, and an explicit `freeze_design: yes|no`.

## acceptance_evidence

GO requires exact plugin/runtime proof and a fully independent deterministic oracle, with all other accepted controls retained. End with `confidence: high|medium|low` and one sentence justifying it.
