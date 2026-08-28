# DESIGN r3 assignment

## objective

Produce the final permitted design revision by correcting the two high-severity findings left open by DESIGN-REVIEW r2, without changing already accepted design decisions.

## inputs

- Candidate design: `Generated Files\hackathon-fleet\agents\hackathon-fix-designer\output\DESIGN.r2.md`
- Exact formal review: `Generated Files\hackathon-fleet\agents\hackathon-design-risk-reviewer\output\DESIGN-REVIEW.r2.md`
- RISK-004 and RISK-005 corrections at DESIGN-REVIEW r2 lines 37-55 are accepted and relayed unchanged.
- All other findings are resolved and must remain resolved.

## constraints

- Do not edit product code or the manager workboard.
- Do not launch subagents.
- Preserve the ABI, production flow, BOM, packaging, baseline, hardware matrix, and gates already accepted.
- Pin exact Qt plugin packages/files and define icon/media probes at source, frozen, Inno-installed, and MSIX-installed stages.
- Fully specify an independently reproducible golden oracle: exact formulas, one pixel/sample format, options, numeric time bases/PTS, fixed expected outputs or independent reference generator, and exact padding behavior.
- Write only the required output record.

## expected_output

Write the complete, self-contained candidate design to `Generated Files\hackathon-fleet\agents\hackathon-fix-designer\output\DESIGN.r3.md`, including explicit RISK-004/RISK-005 corrections and retaining all accepted r2 content needed for implementation.

## acceptance_evidence

Every correction must be implementable without inventing missing oracle/plugin details. End with `confidence: high|medium|low` and one sentence justifying it. High confidence is required for freeze.
