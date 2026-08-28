# IMPL-REVIEW r2

verdict: REVISE

## Finding dispositions

### IMPL-001 - Native Arm64 processes are rejected by the prescribed architecture oracle

- severity: high
- disposition: OPEN - BLOCKED; no approved immutable-design correction exists
- location: `Generated Files\design-spec.md:41`; inherited from immutable `Generated Files\hackathon-fleet\agents\hackathon-fix-designer\output\DESIGN.r3.md:181`
- observed: The implementation still requires `IsWow64Process2` to report ARM64 for both process and native machine. The exact remaining design evidence is: "Process architecture is read with `IsWow64Process2`: process machine is ARM64 and native machine is ARM64; `x86`, `x64`, `ARM64EC`, or emulation fails." The top-level implementation silently does not correct it: "`IsWow64Process2` must report ARM64 process and native machine." A native, non-WOW64 Arm64 process reports `IMAGE_FILE_MACHINE_UNKNOWN` for process machine and `IMAGE_FILE_MACHINE_ARM64` for native machine, so this oracle rejects valid native execution.
- expected: After design-owner approval of a new immutable revision, require native machine ARM64 and process machine UNKNOWN, reject any nonzero process-machine value as WOW/emulated execution, report host/native machine, WOW status, and payload PE machine separately, and retain recursive static/runtime ARM64 checks.
- reproduction: Apply the documented `(ARM64, ARM64)` requirement to the Windows-defined native result `(UNKNOWN, ARM64)`; the mandatory architecture check fails.
- correction: Approve and propagate the formal correction requested in `IMPLEMENT.r2.md:17-24`; do not weaken the `0xAA64`, provenance, import-closure, or runtime-module checks.

### IMPL-002 - The implemented appendix omitted the immutable per-frame oracle hashes

- severity: high (prior)
- disposition: RESOLVED
- location: `Generated Files\appendix-references.md:70-149`; referenced by `Generated Files\design-spec.md:58`
- observed: The appendix now contains exactly 60 ordered lowercase frame hashes and the LF manifest rule. Mechanical extraction found 60 design hashes and 60 appendix hashes with exact index equality. Independent formula recomputation matched every frame hash and reproduced video `a3602aa3a3e5316d9456c97eb8bafe5c97a692ed5c10f3409db763bfb331b83a`, PCM `fb240a5aa9dad1572ba742e9a98cd4d33dc078d57c6d2d7cdbfb077df8cb7cd2`, and manifest `be4c2c85757437afa5861ff92c121af4ec38ef7fd222371881c92511e5e5b1de`.
- expected: The complete immutable oracle is self-contained in the four top-level documents and mechanically reproducible.
- correction: None.

## New findings

None.

## Complete implementation assessment

The four top-level generated documents otherwise preserve the approved baseline, ABI and payload architecture, locked runtime dependencies, bottom-up GitLab artifact flow, Qt/plugin and QWidget probes, G0-G13 ownership, deterministic writer oracle, Inno/MSIX identity and signing requirements, x64-to-Arm64 migration behavior, failure handling, rollback, and two-device acceptance matrix. The accepted RISK-001 through RISK-008 controls remain represented. IMPL-001 is an identified defect in the frozen design itself, not an authorized implementation divergence.

## Blocked-gate consequences

G2 architecture/import cannot accept native process evidence under the current oracle. Consequently G3 Qt ABI/provenance, G8 source/frozen startup, and G11 installed smoke cannot produce valid executable acceptance evidence. Their downstream artifact-publication, QWidget/package, installer, and prerelease gates remain blocked until an approved immutable design revision is propagated. With one open high finding, final implementation acceptance cannot PASS.

## Product-code isolation

PASS. The tracked worktree and index contain no changes, every current untracked path is under `Generated Files`, and no product-code path is modified. This review wrote only this verdict record.

## Evidence

- Re-read immutable `DESIGN.r3.md`, its frozen GO disposition, both implementation findings and r2 dispositions, and all four current top-level documents.
- Mechanically confirmed IMPL-002 by ordered extraction, independent formula generation, and aggregate SHA-256 recomputation.
- Confirmed no approved immutable correction supersedes the exact IMPL-001 requirement.

Zero critical findings and one open high finding remain.

confidence: high
The verdict follows complete document review, independently reproduced oracle hashes, exact blocked-gate tracing, and product-code isolation evidence.
