# IMPL-REVIEW r1

verdict: REVISE

## Findings

### IMPL-001 - Native Arm64 processes are rejected by the prescribed architecture oracle

- severity: high
- location: `Generated Files\design-spec.md:41`; inherited from immutable `DESIGN.r3.md:181`
- observed: The implemented gate requires `IsWow64Process2` to report ARM64 for both the process machine and native machine. Windows defines `pProcessMachine` as `IMAGE_FILE_MACHINE_UNKNOWN` when the target is not a WOW64 process. A native Arm64 OpenShot process therefore returns `UNKNOWN` for the process machine and `ARM64` for the native machine, so the documented mandatory gate rejects the exact native process it is intended to accept.
- expected: On an Arm64 host, accept `pNativeMachine == IMAGE_FILE_MACHINE_ARM64` and `pProcessMachine == IMAGE_FILE_MACHINE_UNKNOWN` as native execution. Reject a nonzero process-machine value as WOW/emulated execution, and prove the executable itself is `0xAA64` with the required static PE scan (or another API that directly reports the executable machine).
- reproduction: Microsoft `IsWow64Process2` documentation states that `pProcessMachine` receives `IMAGE_FILE_MACHINE_UNKNOWN` when the target is not a WOW64 process. Apply the implemented assertion to a native Arm64 process: `(UNKNOWN, ARM64)` fails the required `(ARM64, ARM64)` result.
- required correction: Escalate an immutable-design revision, then correct the G2/G3/G8/G11 oracle everywhere it is stated and make the report distinguish host architecture, WOW/emulation status, and payload PE machine. Do not weaken the `0xAA64` static and runtime-module checks.

### IMPL-002 - The implemented appendix omits all 60 immutable per-frame oracle hashes

- severity: high
- location: `Generated Files\design-spec.md:58`; `Generated Files\appendix-references.md:70-84`
- observed: `design-spec.md` says the exact frame hashes are in `appendix-references.md`, but the appendix contains only the three aggregate hashes and a pointer into an internal fleet design record. A direct comparison finds 60 ordered frame hashes in `DESIGN.r3.md:206-269` and zero of those hashes in any implemented top-level document. This also contradicts the implementer report's claim of a discoverable implementation home across the four documents.
- expected: The implemented fixed-oracle appendix contains the complete ordered 60-hash manifest verbatim, alongside the PCM and aggregate hashes, so the required stdlib-only generator can consume a complete immutable oracle from the implemented documentation set.
- reproduction: Extract lines matching `^\s*[0-9a-f]{64}\s*$` from `DESIGN.r3.md:206-269` and compare them with `appendix-references.md`; all 60 are absent. Reading `design-spec.md:58` then `appendix-references.md:84` follows a second-level reference instead of finding the promised values.
- required correction: Copy the 60 ordered hashes from immutable `DESIGN.r3.md:206-269` verbatim into the fixed G9 oracle section, retain their exact order and LF manifest rule, and make `design-spec.md:58` point to that self-contained list. Verify the three aggregate values remain unchanged.

## Design-compliance mapping

| Design area | Implemented location | Assessment |
| --- | --- | --- |
| Decision, post-4.0 baseline, scope, non-goals, fallback | `goal.md:3-39` | Compliant; native results are honestly gated. |
| Immutable ABI, exact Python/Qt/toolchain pins, recursive graph | `goal.md:9-17`; `design-spec.md:3-25`; `appendix-references.md:36-55` | Compliant except the runtime architecture oracle in IMPL-001. |
| Bottom-up PR A/B/C ownership and release-producing GitLab chain | `goal.md:3-7`; `design-spec.md:27-35`; `files-to-update.md:1-55` | Compliant and consistent with the three current `.gitlab-ci.yml` files. |
| Exact producer artifact contracts and canonical architecture names | `files-to-update.md:5-57` | Compliant; artifact names, `install-arm64`, and digest-only consumption match DESIGN r3. |
| G0-G13 procedures, owners, blocks, rollback, assumptions | `design-spec.md:27-134` | Compliant in coverage; G2/G3/G8/G11 are not executable until IMPL-001 is corrected. |
| Four-stage Qt/platform/image/icon/media probe and plugin inventory | `design-spec.md:37-54`; `appendix-references.md:57-68` | Compliant; all ten required paths and the WAV digest are consistent. |
| Deterministic G9 semantics and real-writer failures | `design-spec.md:56-64`; `appendix-references.md:70-86` | Incomplete due to IMPL-002; formulas, aggregate hashes, formats, options, exclusions, and negative cases otherwise match. |
| Inno/MSIX identity, signing, migration, failure injection | `design-spec.md:66-90`; `files-to-update.md:31-57` | Compliant with DESIGN r3 and the current hard-coded x86/x64 source surfaces. |
| Physical two-device acceptance matrix | `design-spec.md:91-109` | Compliant; thresholds and no-waiver rows are preserved. |
| Approval, source evidence, exact BOM, feature/license policy | `appendix-references.md:3-55` | Compliant; exact pins and current source SHAs match the checked-out repositories. |

## Product-code isolation

PASS. `openshot-qt` HEAD is `9cd2b3f3ee9024c3496487a2de30a402515ed659`, `libopenshot` HEAD is `eac81cf91555438c54fbadef7fdd05bf803f26ee`, and `libopenshot-audio` HEAD is `48516e0b64b9f3ddf2ab79975a42ba2f37023703`. The sibling repositories are clean, and the openshot-qt worktree contains only untracked `Generated Files` records; no product-code path is modified.

## Evidence

- Inspected the complete four top-level Markdown files, immutable DESIGN r3, its GO review, the implementer report, and all current worktree changes.
- Confirmed the cited current source behavior in all three repositories, including legacy Python discovery and QWidget typemaps, x64/x86 GitLab artifact flow, freezer dependency harvesting, Inno identity/cleanup, MSIX capture, and build/deploy architecture parsing.
- Confirmed issue `openshot-qt#5853` and PRs `openshot-qt#6075`, `libopenshot#1082`, and `libopenshot-audio#170` remain open on 2026-08-27.
- Confirmed all exact dependency pins, Qt plugin names, fixture/oracle aggregate digests, artifact names, AppId, and G0-G13 ownership are otherwise internally consistent.

Zero critical findings and two open high findings remain. Acceptance requires correction of both findings and, for IMPL-001, an approved revision to the immutable design requirement before the implemented documents can conform.

confidence: high
The verdict is based on complete document/source inspection, exact hash-set comparison, clean-worktree evidence across all three repositories, and the authoritative Windows API contract that directly reproduces the blocking architecture-gate failure.
