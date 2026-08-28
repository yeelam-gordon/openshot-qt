# DESIGN-REVIEW r1 assignment

## objective

Formally review the designer's current r1 design against your independent risk assessment and current source/upstream reality.

## inputs

- Exact design: `Generated Files\hackathon-fleet\agents\hackathon-fix-designer\output\DESIGN.r1.md`
- Exact independent findings: `Generated Files\hackathon-fleet\agents\hackathon-design-risk-reviewer\output\RISK.r1.md`
- All RISK-001 through RISK-008 findings are manager-accepted unchanged.
- Original files under `Generated Files\`

## constraints

- Do not edit product code or the manager workboard.
- Do not launch subagents.
- Preserve stable finding IDs; mark each resolved, open, or superseded with evidence.
- Review the actual r1 design rather than merely repeating the independent assessment.
- Write only the required output record.

## expected_output

Write `Generated Files\hackathon-fleet\agents\hackathon-design-risk-reviewer\output\DESIGN-REVIEW.r1.md` with finding-by-finding disposition, any new stable findings, severity, exact required correction, and GO / REVISE / NO-GO verdict.

## acceptance_evidence

GO requires no open critical/high findings, all assumptions verified or explicit gates, and evidence-backed high confidence. End with `confidence: high|medium|low` and one sentence justifying it.

