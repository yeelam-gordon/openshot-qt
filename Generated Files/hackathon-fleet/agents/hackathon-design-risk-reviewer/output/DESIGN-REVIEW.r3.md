# DESIGN-REVIEW r3

verdict: GO
freeze_design: yes

DESIGN r3 is complete and may be frozen unchanged. The final candidate retains all previously resolved controls and closes the two remaining high-severity findings with exact, blocking acceptance evidence. Live checks on 2026-08-27 confirm issue `openshot-qt#5853` and release PRs `openshot-qt#6075`, `libopenshot#1082`, and `libopenshot-audio#170` remain open, published releases remain v3.5.1/v0.7.0/v0.6.0, and the recorded `develop` SHAs remain current; no upstream implementation supersedes the design.

## RISK-001 - No coherent Python/Qt/C++ ABI contract

- severity: critical
- disposition: resolved
- remaining severity: none
- location/evidence: `DESIGN.r3.md:37-64,176-181,330-349`
- observed behavior: One immutable CLANGARM64 contract fixes the target, compiler/runtime, CPython, Qt, PyQt6/sip, generator, dependency lock, provenance, and no-fallback policy. Static and runtime gates reject foreign architecture, duplicate Qt, or incompatible provenance before QWidget interop.
- expected behavior: One immutable ABI contract must govern every producer and consumer.
- resolution evidence: G1-G3 block native builds, publication, and QWidget use on contract drift or ABI/provenance failure.

## RISK-002 - Production CI owners are omitted and the proposed landing order is dependency-inverted

- severity: high
- disposition: resolved
- remaining severity: none
- location/evidence: `DESIGN.r3.md:7-11,91-172,330-345`
- observed behavior: Both native release-producing GitLab pipelines, runner provisioning, immutable producer contracts, and exact consumer digests are assigned and ordered audio, libopenshot, then openshot-qt.
- expected behavior: The production artifact chain must be owned and validated bottom-up without replacing existing lanes.
- resolution evidence: G4 blocks PR B, G5-G6 block PR C, and G7-G12 block package publication; GitHub Actions remains supplemental.

## RISK-003 - The native dependency closure is not a plan

- severity: high
- disposition: resolved
- remaining severity: none
- location/evidence: `DESIGN.r3.md:58-89,113-119,160-168,330-345`
- observed behavior: The checksummed BOM fixes producers, versions, target environment, transitive PE closure, feature/license policy, runner image, and feature smokes. Current MSYS2 CLANGARM64 package pages confirm the listed Python, PyQt6, Qt, FFmpeg, OpenCV, and Protobuf versions.
- expected behavior: Every native or redistributed input must be traceable under the ABI contract with explicit required/optional behavior.
- resolution evidence: G1 fails closed on unavailable, mutable, unlicensed, wrong-machine, unresolved, duplicate, or foreign-prefix inputs; required features cannot be silently disabled.

## RISK-004 - The proposed CI gate cannot prove a native packaged application

- severity: high
- disposition: resolved
- remaining severity: none
- location/evidence: `DESIGN.r3.md:50,64,72,97-100,157,176-190,330-345`
- observed behavior: The design pins the exact platform, image, icon, and multimedia files and runs one unchanged explicit probe at source, frozen-directory, Inno-installed, and MSIX-installed stages. MSYS2 package inventories confirm the named owners and filenames, including `qsvgicon.dll` and `ffmpegmediaplugin.dll`. Each stage captures plugin paths, hashes, loader output, process/module architecture, and Qt provenance and fails on absence, warning, fallback, duplicate runtime, external load, emulation, or non-ARM64 code.
- expected behavior: All four execution stages must prove native Arm64 identity and representative Qt platform, image, icon, and media plugin operation from a defined package inventory.
- resolution evidence: G3/G8/G11 require separate four-stage reports, canonical image/icon digests, exact decoded PCM from the Qt FFmpeg media plugin, `IsWow64Process2`, static PE scans, and runtime module inventories.

## RISK-005 - Golden determinism is underspecified and may reject valid FFmpeg outputs

- severity: high
- disposition: resolved
- remaining severity: none
- location/evidence: `DESIGN.r3.md:192-275,330-345`
- observed behavior: The oracle fixes every pixel/sample formula, BGRA/s16le layout, dimensions/counts, time bases/PTS, FFV1/PCM/muxer options, metadata policy, decoded padding rule, semantic exclusions, and real writer failure/cancellation cases. A stdlib-only generator independent of OpenShot, FFmpeg, Qt, NumPy, and production helpers validates committed outputs before writer execution.
- expected behavior: The oracle must fully define inputs, formats, encoder settings, timestamps, metadata, independently fixed semantic expectations, and failure paths.
- resolution evidence: Independent recomputation exactly matched all 60 frame hashes and the committed aggregate video, PCM, and manifest SHA-256 values. G9 prevents the implementation under test from generating or blessing expectations and retains unavailable-codec, open/write/close, cancellation, cleanup, and partial-output assertions.

## RISK-006 - Installer architecture, upgrade, signing, and coexistence failure paths lack acceptance criteria

- severity: high
- disposition: resolved
- remaining severity: none
- location/evidence: `DESIGN.r3.md:145-160,277-302,324-345`
- observed behavior: Exact architecture mappings, stable identities, replacement semantics, signatures, upgrade/repair/downgrade behavior, rollback, payload inspection, uninstall cleanup, and injected failures are specified for Inno and MSIX on physical Arm64 hardware.
- expected behavior: Package identity and migration semantics must be explicit and exercised for success and failure paths.
- resolution evidence: G10-G12 block signing and release on mixed architecture, unsafe replacement, invalid signature/publisher, interrupted install, stale registration, or cleanup failure.

## RISK-007 - Current upstream release and issue state is not incorporated

- severity: medium
- disposition: resolved
- remaining severity: none
- location/evidence: `DESIGN.r3.md:11,26-33,162-170,330-345`
- observed behavior: The design selects post-4.0-merge `develop`, records the intended 4.0.0/1.0.0 SO contract, and blocks production implementation until exact SHAs, versions, and SO values are frozen after coordinated release selection.
- expected behavior: One baseline and compatibility contract must be selected before artifact production.
- resolution evidence: G0 invalidates downstream evidence when a baseline SHA or version/SO contract changes; live upstream state still matches the design's premise.

## RISK-008 - Windows Arm hardware behavior coverage is too narrow

- severity: medium
- disposition: resolved
- remaining severity: none
- location/evidence: `DESIGN.r3.md:296-322,330-345`
- observed behavior: G13 defines two physical-device classes with measurable native launch, preview, playback, audio input/output, software/hardware codec, fallback, sleep, path, memory-pressure, repetition, and install-lifecycle procedures.
- expected behavior: Physical acceptance must cover the user-visible native stack and representative Windows Arm failure paths with explicit thresholds.
- resolution evidence: Stable release is blocked on mandatory architecture, render, audio-output, upgrade, signing, uninstall, or other matrix failures.

## New findings

None.

## Verdict basis

No critical or high finding remains. RISK-004 now provides exact plugin/runtime proof at all four required stages, and RISK-005 supplies a fully independent deterministic oracle whose fixed hashes were independently reproduced. All other accepted controls remain blocking, assigned, and internally consistent.

confidence: high
The verdict follows a complete finding-by-finding review, independent oracle recomputation, direct package/plugin inventory checks, and current upstream issue, PR, release, branch, build, and dependency evidence.
