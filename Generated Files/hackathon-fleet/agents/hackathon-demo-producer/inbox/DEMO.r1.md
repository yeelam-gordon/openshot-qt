# DEMO r1 assignment

## objective

Create the complete 2-4 minute hackathon demo package from approved design and verified readiness evidence, presenting the current blocked status honestly.

## inputs

- Approved design: `Generated Files\hackathon-fleet\agents\hackathon-fix-designer\output\DESIGN.r3.md`
- Current four top-level generated documents
- Verified readiness: `Generated Files\hackathon-fleet\agents\hackathon-arm-readiness\output\ARM-READY.r1.md`
- Runbook: `Generated Files\windows-arm-build-test-guide.md`
- Final implementation review: `Generated Files\hackathon-fleet\agents\hackathon-implementation-reviewer\output\IMPL-REVIEW.r2.md`
- Demand/impact evidence in `Generated Files\appendix-references.md`

## constraints

- Do not launch subagents, edit product code, or edit the manager workboard.
- Never invent performance, power, downloads, users, compatibility, build, import, render, package, or hardware results.
- State that no native Arm64 candidate exists and IMPL-001 blocks G2/G3/G8/G11.
- The “after” segment may demonstrate the approved reproducible oracle, architecture-aware plan, and executable runbook, but must not imply a working native OpenShot application.
- Every number must cite the approved design or ARM-READY evidence.
- Subtitles must match narration exactly.

## expected_output

- `Generated Files\demo\demo-script.md`
- `Generated Files\demo\shot-list.md`
- `Generated Files\demo\narration.txt`
- `Generated Files\demo\subtitles.srt`
- `Generated Files\demo\impact-evidence.md`
- `Generated Files\hackathon-fleet\agents\hackathon-demo-producer\output\DEMO.r1.md`

The demo must cover: user problem, exact before gap, manager/worker workflow and reusable lock/oracle/runbook, honest after state, measured documentation/test evidence, ecosystem multiplier and separate upstream PRs, limitations, and next gate.

## acceptance_evidence

- Narration duration is 2-4 minutes at a stated words-per-minute assumption.
- SRT spoken text equals narration exactly after cue concatenation and line-ending normalization.
- Every quantitative or status claim maps to a cited artifact.
- End the output record with `confidence: high|medium|low` and one sentence justifying it.
