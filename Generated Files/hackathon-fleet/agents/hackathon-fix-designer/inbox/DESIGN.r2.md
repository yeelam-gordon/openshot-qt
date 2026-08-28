# DESIGN r2 assignment

## objective

Revise DESIGN r1 against every manager-accepted finding and produce a complete implementation-ready documentation design.

## inputs

- Exact prior design: `Generated Files\hackathon-fleet\agents\hackathon-fix-designer\output\DESIGN.r1.md`
- Exact independent findings: `Generated Files\hackathon-fleet\agents\hackathon-design-risk-reviewer\output\RISK.r1.md`
- All RISK-001 through RISK-008 findings are manager-accepted unchanged.
- Original files under `Generated Files\`

## constraints

- Do not edit product code or the manager workboard.
- Do not launch subagents.
- Address every accepted finding explicitly without weakening its required correction.
- Resolve uncertainty either with evidence or a named blocking gate and owner.
- Keep the workspace documentation-only and preserve separate repository/PR ownership.
- Write only the required output record.

## expected_output

Write `Generated Files\hackathon-fleet\agents\hackathon-fix-designer\output\DESIGN.r2.md`. Include a RISK-001 through RISK-008 disposition table, one coherent pinned ABI/toolchain contract, dependency BOM/ownership, bottom-up production CI flow, packaged-native and golden-render acceptance, package migration/failure tests, release-baseline policy, hardware matrix, exact change surface, sequence, rollback, and gates.

## acceptance_evidence

Every resolved claim cites commands, source lines, upstream links, or artifacts; unproven runtime claims are explicit gates. End with `confidence: high|medium|low` and one sentence justifying it. High confidence is required for freeze, based on design completeness and explicit gates rather than pretending hardware results exist.
