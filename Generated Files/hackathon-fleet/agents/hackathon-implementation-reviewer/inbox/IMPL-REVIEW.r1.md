# IMPL-REVIEW r1 assignment

## objective

Review the documentation implementation against immutable DESIGN r3 and actual repository behavior, looking only for high-confidence correctness, compliance, architecture, packaging, regression, error-handling, and upstreamability defects.

## inputs

- Approved design: `Generated Files\hackathon-fleet\agents\hackathon-fix-designer\output\DESIGN.r3.md`
- Design approval: `Generated Files\hackathon-fleet\agents\hackathon-design-risk-reviewer\output\DESIGN-REVIEW.r3.md`
- Implementation report: `Generated Files\hackathon-fleet\agents\hackathon-implementer\output\IMPLEMENT.r1.md`
- Implemented files: the four top-level Markdown files under `Generated Files\`
- Current openshot-qt source plus sibling libopenshot and libopenshot-audio source

## constraints

- Do not edit any files or launch subagents.
- Do not edit the manager workboard.
- Review the complete current implementation, not only the implementer report.
- Preserve the documentation-only scope; absent native runtime results are expected only when honestly gated.
- Use stable finding IDs with exact file/location, observed, expected, reproduction, severity, and required correction.

## expected_output

Write only `Generated Files\hackathon-fleet\agents\hackathon-implementation-reviewer\output\IMPL-REVIEW.r1.md` with PASS / REVISE verdict, all findings, design-compliance mapping, product-code isolation assessment, and confidence.

## acceptance_evidence

PASS requires zero open critical/high findings, faithful DESIGN r3 coverage, no product-code changes, consistent exact pins/oracles/plugin inventory, executable downstream gates, and high confidence. End with `confidence: high|medium|low` and one sentence justifying it.
