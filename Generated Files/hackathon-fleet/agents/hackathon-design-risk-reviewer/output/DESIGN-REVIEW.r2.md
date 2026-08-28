# DESIGN-REVIEW r2

verdict: REVISE

DESIGN r2 closes the ABI, production-flow, dependency, packaging, baseline, and hardware-coverage findings, but it does not fully close two unchanged high-severity acceptance requirements. It cannot be frozen unchanged while the packaged Qt plugin proof and semantic golden oracle remain underspecified. Live checks on 2026-08-27 still show issue `openshot-qt#5853` and release PRs `openshot-qt#6075`, `libopenshot#1082`, and `libopenshot-audio#170` open; no upstream implementation supersedes this design.

## RISK-001 - No coherent Python/Qt/C++ ABI contract

- severity: critical
- disposition: resolved
- remaining severity: none
- location/evidence: `DESIGN.r2.md:37-64,111-117,160-179,255-274`
- observed behavior: The design fixes one CLANGARM64 target triplet, compiler/runtime, CPython, Qt, PyQt6/sip, generator, and C runtime policy. G1 creates an immutable checksummed package lock; producer contracts carry SOABI, compiler/CRT, Qt identity, and lock digest; G2-G3 block publication and QWidget use on architecture, ABI, provenance, fallback, or duplicate-Qt failures.
- expected behavior: One immutable ABI contract, or a measurable blocking pre-implementation contract artifact, must govern every producer and consumer.
- resolution evidence: G1 is owned by release infrastructure and blocks native builds; PR A, PR B, and PR C consume the same digest; any drift requires a contract revision and all downstream gates to rerun.

## RISK-002 - Production CI owners are omitted and the proposed landing order is dependency-inverted

- severity: high
- disposition: resolved
- remaining severity: none
- location/evidence: `DESIGN.r2.md:7-11,91-170,255-270`
- observed behavior: Both native release-producing `.gitlab-ci.yml` files, the application pipeline, runner provisioning, immutable artifact contracts, and exact producer digests are assigned. Validation and landing are ordered audio, libopenshot, then openshot-qt.
- expected behavior: The production artifact chain must be owned and validated bottom-up without replacing existing lanes.
- resolution evidence: G4 blocks PR B, G5-G6 block PR C, and G7-G12 block package publication; GitHub Actions remains supplemental.

## RISK-003 - The native dependency closure is not a plan

- severity: high
- disposition: resolved
- remaining severity: none
- location/evidence: `DESIGN.r2.md:58-89,111-117,158-166,255-287`
- observed behavior: The BOM covers the required native families, versions, producers, target environment, feature/license policy, owners, and feature smokes. G1 extends the lock to direct and transitive PE-producing dependencies, signatures, checksums, licenses, and the runner image; recursive static and runtime closure scans fail on unresolved, duplicate, foreign-prefix, or wrong-machine inputs.
- expected behavior: Every native or redistributed input must be traceable under the ABI contract, with explicit required/optional behavior.
- resolution evidence: Required current features fail closed; ASIO and PyOpenGL acceleration have explicit optional policies; cx_Freeze is source-built and blocked by G7 rather than assumed operational.

## RISK-004 - The proposed CI gate cannot prove a native packaged application

- severity: high
- disposition: open
- remaining severity: high
- location/evidence: `DESIGN.r2.md:174-185,255-270`
- observed behavior: The design now separates source, frozen, Inno-installed, and MSIX-installed execution; uses `IsWow64Process2`; inventories loaded modules; machine-checks bundled PEs; and fails on duplicate Qt, unresolved imports, plugin warnings, and emulation. However, G8 explicitly exercises platform and PNG/JPEG/SVG image loading but never names or requires representative Qt icon and media plugin loading in each frozen and installed candidate. The BOM likewise names `qt6-base`, `qt6-svg`, and `qt6-imageformats`, but no media-plugin package or exact required plugin inventory. Generic “loads images/plugins” and a tiny project do not prove the unchanged icon/media-plugin criterion.
- expected behavior: Source, frozen, Inno-installed, and MSIX-installed execution must prove native Arm64 process/module identity and exercise representative Qt platform, image, icon, and media plugins with a defined required-plugin inventory.
- required design correction: Pin the exact Qt plugin packages and required plugin filenames, then add explicit icon and media load/playback probes to source, frozen, Inno-installed, and MSIX-installed gates. Each probe must capture loaded paths/modules and fail on absence, fallback outside the package, duplicate Qt provenance, plugin-loader warnings, or non-ARM64 modules.

## RISK-005 - Golden determinism is underspecified and may reject valid FFmpeg outputs

- severity: high
- disposition: open
- remaining severity: high
- location/evidence: `DESIGN.r2.md:187-200`
- observed behavior: The design correctly selects lossless FFV1/PCM in Matroska, semantic decoded hashes, fixed counts, one thread, normalized metadata, and real writer failure/cancellation cases. It still leaves the frame color-block dimensions/value formula and integer PCM sample formula unspecified, permits `rgba` **or** another later-selected pixel format, gives no numeric stream time bases or complete FFV1 encoder options, and does not provide the expected frame/PCM hashes or an independent procedure that fixes them before testing. Hashes generated and stored by the implementation under test can bless a consistently wrong oracle.
- expected behavior: The oracle must fully define input values, codec/pixel/sample formats, encoder settings, timestamps/time bases, metadata policy, and independently fixed semantic expectations while exercising required failure paths.
- required design correction: Define the exact per-pixel and per-sample formulas, choose one pixel format without an alternative, specify all FFV1 and muxer options plus numeric PTS/time bases, and include committed expected frame/PCM hashes or a separately implemented reference generator with fixed outputs. State exact decoded audio padding behavior; retain the unavailable-codec, open/write/close, cancellation, cleanup, and partial-output assertions already specified.

## RISK-006 - Installer architecture, upgrade, signing, and coexistence failure paths lack acceptance criteria

- severity: high
- disposition: resolved
- remaining severity: none
- location/evidence: `DESIGN.r2.md:143-155,202-227,249-274`
- observed behavior: The design fixes every architecture mapping, retains one production AppId/package identity, selects replacement rather than side-by-side semantics, defines upgrade/repair/downgrade and rollback behavior, and assigns payload, signature, publisher, association, firewall, uninstall, and injected-failure checks on physical Arm64 hardware.
- expected behavior: Package identity and migration semantics must be explicit and exercised for both success and failure paths.
- resolution evidence: G10-G12 block signing and prerelease; failed replacement, invalid signatures/publishers, interrupted installs, stale registration, or mixed-architecture payloads fail acceptance.

## RISK-007 - Current upstream release and issue state is not incorporated

- severity: medium
- disposition: resolved
- remaining severity: none
- location/evidence: `DESIGN.r2.md:11,26-33,160-163,255-258`
- observed behavior: The design selects post-4.0-release-merge `develop`, records the intended 4.0.0/1.0.0 SO contract, and blocks production implementation until exact SHAs, versions, and SO values are frozen after the coordinated release PRs merge or are explicitly superseded.
- expected behavior: One baseline and compatibility contract must be selected before artifact production.
- resolution evidence: G0 is maintainer-owned, blocks all production implementation, and invalidates downstream evidence when a baseline SHA or version contract changes.

## RISK-008 - Windows Arm hardware behavior coverage is too narrow

- severity: medium
- disposition: resolved
- remaining severity: none
- location/evidence: `DESIGN.r2.md:229-247,269-272`
- observed behavior: G13 defines two physical-device classes, provenance and native-module capture, and measurable launch, preview, playback, audio input/output, software/hardware codec, fallback, sleep, path, memory-pressure, repetition, and install-lifecycle procedures.
- expected behavior: Physical acceptance must cover the user-visible native stack and representative Windows Arm failure paths with explicit thresholds.
- resolution evidence: The matrix sets time, count, A/V sync, crash, cleanup, and growth thresholds and blocks stable release on mandatory architecture, render, audio, upgrade, signing, or uninstall failures.

## New findings

None.

## Verdict basis

`REVISE` is required because RISK-004 and RISK-005 remain open at high severity. DESIGN r2 may not be frozen unchanged. The selected architecture and all other accepted corrections are credible, measurable, blocking, and assigned, so `NO-GO` is not warranted; `GO` requires the exact packaged Qt plugin probes and fully fixed independent golden oracle above.

confidence: high
The verdict follows a complete finding-by-finding comparison against RISK r1 and DESIGN-REVIEW r1, direct inspection of DESIGN r2, and current upstream issue/PR evidence checked on 2026-08-27.
