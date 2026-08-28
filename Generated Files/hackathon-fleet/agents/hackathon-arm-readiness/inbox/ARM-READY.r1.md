# ARM-READY r1 assignment

## objective

Independently assess build/test/Windows Arm64 readiness, produce the authoritative executable Windows Arm runbook, and return an evidence-backed verdict without claiming unavailable native results.

## inputs

- Approved design: `Generated Files\hackathon-fleet\agents\hackathon-fix-designer\output\DESIGN.r3.md`
- Current top-level generated documents
- Final implementation review: `Generated Files\hackathon-fleet\agents\hackathon-implementation-reviewer\output\IMPL-REVIEW.r2.md`
- Formal blocker request: `Generated Files\hackathon-fleet\agents\hackathon-implementer\output\IMPLEMENT.r2.md`
- Current openshot-qt source and sibling libopenshot/libopenshot-audio source

## constraints

- Do not launch subagents or edit product code/workboard.
- IMPL-001 is an open high finding; do not present G2/G3/G8/G11 or downstream readiness as passing.
- Distinguish checks executable on this AMD64 host from commands requiring a native Windows Arm64 runner, signing credentials, or physical devices.
- Use existing build/test/lint commands only.
- Never invent architecture, import, render, install, performance, power, or compatibility evidence.

## expected_output

- Create `Generated Files\windows-arm-build-test-guide.md` with exact prerequisites, bottom-up commands, expected outputs, architecture/import/plugin/render/package/signing/install/hardware checks, corrected `IsWow64Process2` diagnostic semantics clearly labeled as blocked pending design approval, failure diagnostics, rollback, and evidence capture.
- Write `Generated Files\hackathon-fleet\agents\hackathon-arm-readiness\output\ARM-READY.r1.md` with verdict, exit codes, test/build evidence, architecture-closure state, what was not tested and why, and confidence.

## acceptance_evidence

- Run the smallest existing checks possible on this host and report exact exit codes.
- Verify the guide covers G0-G13 and all three repositories in dependency order.
- Quote the exact readiness blocker and downstream consequences.
- End with `confidence: high|medium|low` and one sentence justifying it.
