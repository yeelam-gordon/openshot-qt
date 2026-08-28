# Impact and claim evidence

## Claim map

| Demo claim | Evidence | Allowed wording / boundary |
| --- | --- | --- |
| Demand exists | `appendix-references.md:8`; `DESIGN.r3.md:28-29` | One verified open upstream issue, `openshot-qt#5853`. No user, download, or market-size claim is supported. |
| The before state lacks a production Arm64 edge | `DESIGN.r3.md:28-35`; `ARM-READY.r1.md:7-15,69-77` | Current Windows jobs are x64/x86-only; no candidate EXE, DLL, PYD, wheel, or MSIX was found. |
| Scope spans three repositories | `goal.md:3-23`; `DESIGN.r3.md:7-11` | `libopenshot-audio`, `libopenshot`, and `openshot-qt`, in dependency order. |
| Manager/worker workflow was documentation-only | `hackathon-fleet\workboard.md:3-24`; `IMPL-REVIEW.r2.md:38-40` | Manager routing and specialist review records are evidenced; no product-code delivery claim. |
| One reusable ABI/toolchain lock is designed | `DESIGN.r3.md:37-64`; `appendix-references.md:36-55` | Approved design requirement, not evidence that G1 has produced the signed lock. |
| Three separate upstream changes multiply the result across the stack | `DESIGN.r3.md:121-172`; `files-to-update.md:1-57` | Planned PR A/B/C ownership and artifact flow. Do not claim these Arm PRs exist, pass, or are merged. |
| The deterministic oracle is mechanically reproducible | `IMPLEMENT.r2.md:26-33`; `IMPL-REVIEW.r2.md:17-24`; `ARM-READY.r1.md:56` | Exactly 60 ordered frame hashes and the manifest digest were reproduced as documentation evidence. The real native writer was not run. |
| Oracle dimensions and counts | `DESIGN.r3.md:192-204`; `appendix-references.md:70-82` | 60 frames, 64x36 BGRA, and 96,000 stereo `s16le` audio frames are approved oracle inputs, not measured native output. |
| The runbook covers G0-G13 and two device classes | `ARM-READY.r1.md:98-104`; `windows-arm-build-test-guide.md:110-476` | Executable plan coverage only. Physical hardware procedures were not run. |
| Host tests produced measured documentation evidence | `ARM-READY.r1.md:50-67` | 3 release-detail tests passed. The full host suite ran 52 tests with 25 errors, dominated by missing Qt and `openshot`. |
| Current status is not ready | `windows-arm-build-test-guide.md:1-35`; `ARM-READY.r1.md:69-96` | No native Arm64 candidate exists; G0/G1 infrastructure and the Arm64 lanes are not implemented. |
| Native-process oracle is corrected | `design-spec.md:41`; `windows-arm-build-test-guide.md:16-35` | `(UNKNOWN, ARM64)` means native Arm64 execution; any nonzero process-machine value means WOW/emulation. Payload architecture is proven separately as PE machine `0xAA64`. |
| Native success and performance remain unclaimed | `ARM-READY.r1.md:106-120`; `goal.md:19-23` | No import, render, package, signing, migration, performance, power, or physical-device success claim. |
| Next gate | `windows-arm-build-test-guide.md:12-43,110-164` | Freeze G0, provision the G1 signed lock/native runner, then implement PR A/B/C. |

## Impact framing

The evidenced multiplier is engineering reuse, not audience size: one contract, lock format, architecture validator, oracle, and runbook govern three separately owned repositories, two package formats, four execution stages, and two required physical-device classes. These are approved design surfaces and acceptance requirements; none is presented as completed native execution.

## Status statement

There is no native Arm64 candidate and no native build, import, render, package, install, signing, migration, performance, power, or hardware result. The architecture oracle is corrected, but G0/G1 and the three Arm64 implementation lanes remain unfulfilled.
