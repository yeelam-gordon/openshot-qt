# RISK r1 assignment

## objective

Independently investigate and attack the proposed Windows Arm64 native-stack direction before seeing the designer output. Identify incorrect assumptions, regressions, missing edge cases, dependency risks, upstream conflicts, and scope traps.

## inputs

- Every file under `Generated Files\` except `Generated Files\hackathon-fleet\`
- Current source and git history in `C:\s\Demo\Hack2026\OpenShot`
- Sibling repositories `C:\s\Demo\Hack2026\libopenshot` and `C:\s\Demo\Hack2026\libopenshot-audio`
- Relevant current releases, issues, PRs, CI, and dependency support where verifiable

## constraints

- Do not edit product code or the manager workboard.
- Do not launch subagents.
- Investigate current upstream reality independently.
- Keep findings within the documentation-only workspace goal.
- Write only the required output record.

## expected_output

Write `Generated Files\hackathon-fleet\agents\hackathon-design-risk-reviewer\output\RISK.r1.md` with stable finding IDs, location/evidence, observed versus expected, severity, required design correction, and a GO / REVISE / NO-GO verdict.

## acceptance_evidence

Every critical/high finding cites commands, source lines, upstream links, or artifacts. End with `confidence: high|medium|low` and one sentence justifying it.
