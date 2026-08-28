# DESIGN-REVIEW r2 assignment

## objective

Review DESIGN r2 as the candidate immutable design and decide whether it satisfies every accepted finding and is safe to freeze.

## inputs

- Candidate design: `Generated Files\hackathon-fleet\agents\hackathon-fix-designer\output\DESIGN.r2.md`
- Prior design: `Generated Files\hackathon-fleet\agents\hackathon-fix-designer\output\DESIGN.r1.md`
- Accepted independent findings: `Generated Files\hackathon-fleet\agents\hackathon-design-risk-reviewer\output\RISK.r1.md`
- Prior formal review: `Generated Files\hackathon-fleet\agents\hackathon-design-risk-reviewer\output\DESIGN-REVIEW.r1.md`
- All prior findings and required corrections are relayed unchanged.

## constraints

- Do not edit product code or the manager workboard.
- Do not launch subagents.
- Re-investigate source/upstream only where needed to test r2 claims.
- Preserve stable finding IDs and evaluate every open r1 disposition.
- Treat explicit pre-implementation/runtime gates as valid only if measurable, blocking, and assigned.
- Write only the required output record.

## expected_output

Write `Generated Files\hackathon-fleet\agents\hackathon-design-risk-reviewer\output\DESIGN-REVIEW.r2.md` with finding-by-finding status, any new findings, remaining severity, GO / REVISE / NO-GO verdict, and whether DESIGN r2 can be frozen unchanged.

## acceptance_evidence

GO requires zero open critical/high findings, all assumptions verified or explicit gates, and high confidence supported by sources/artifacts. End with `confidence: high|medium|low` and one sentence justifying it.
