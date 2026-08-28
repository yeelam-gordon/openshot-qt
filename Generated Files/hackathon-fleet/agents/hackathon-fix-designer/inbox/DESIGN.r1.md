# DESIGN r1 assignment

## objective

Independently verify the current OpenShot Windows Arm64 native-stack problem and produce an evidence-backed fix design for this documentation-only workspace.

## inputs

- Every file under `Generated Files\` except `Generated Files\hackathon-fleet\`
- Current source and git history in `C:\s\Demo\Hack2026\OpenShot`
- Sibling repositories `C:\s\Demo\Hack2026\libopenshot` and `C:\s\Demo\Hack2026\libopenshot-audio`
- Relevant current releases, issues, PRs, CI, and dependency support where verifiable

## constraints

- Do not edit product code or the manager workboard.
- Do not launch subagents.
- Keep separate PR ownership for all three repositories.
- Separate agent-controlled work from maintainer/vendor/hardware-controlled gates.
- Do not claim a blocker without source or reproduction evidence.
- Write only the required output record.

## expected_output

Write `Generated Files\hackathon-fleet\agents\hackathon-fix-designer\output\DESIGN.r1.md` containing current-state evidence, root cause, already-solved work and duplication risks, dependency graph, proposed architecture and alternatives, exact files/symbols/workflows, implementation sequence, test and rollback design, and open assumptions.

## acceptance_evidence

Every material claim cites commands, source lines, upstream links, or artifacts. End with `confidence: high|medium|low` and one sentence justifying it.

