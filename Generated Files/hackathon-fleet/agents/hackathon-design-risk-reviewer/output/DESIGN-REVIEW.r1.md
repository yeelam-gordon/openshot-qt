# DESIGN-REVIEW r1

verdict: REVISE

The r1 design corrects the production artifact order and selects a credible single-distribution CLANGARM64 direction, but it remains non-approvable while one critical and four high-severity findings are open. Current upstream state still shows issue `openshot-qt#5853` and release PRs `openshot-qt#6075`, `libopenshot#1082`, and `libopenshot-audio#170` open as of 2026-08-27; no cited or discovered PR supersedes this work.

## RISK-001 - No coherent Python/Qt/C++ ABI contract

- severity: critical
- disposition: open
- location/evidence: `DESIGN.r1.md:7-9,41-53,71-74,96-100,109-111,130,135-137`
- observed behavior: The design now chooses one MSYS2 `CLANGARM64` Python/PyQt6/Qt6 prefix, prohibits mixing PyPI Qt DLLs, fixes `OPENSHOT_QT_API=pyqt6`, requires AArch64 machine checks, and places dependency discovery before the three implementation PRs. However, it still does not identify the CPython version, PyQt6/sip version, Qt version, clang/runtime version, or resulting CRT and extension ABI. “Pin and archive the successful manifest” is deferred until after the design and is not accompanied by the exact compatibility record that PRs must consume.
- expected behavior: The reviewed design must define an immutable ABI contract, or an explicit pre-implementation output schema and stop gate, covering interpreter and extension ABI, compiler/runtime, Qt and binding provenance/version, and every consumer's artifact compatibility metadata.
- required design correction: Define the dependency-spike deliverable as a checked, immutable toolchain lock containing exact package versions, package URLs/checksums, target triplets, clang/CRT identities, CPython SOABI, PyQt6/sip and Qt identities, and loaded Qt DLL provenance. Require PR A, PR B, and PR C to consume that lock unchanged, and stop before implementation if QWidget interop loads more than one Qt distribution or any ABI field differs.

## RISK-002 - Production CI owners are omitted and the proposed landing order is dependency-inverted

- severity: high
- disposition: resolved
- location/evidence: `DESIGN.r1.md:18-20,62-82,94-103,124,137`
- observed behavior: The design adds Arm64 jobs to both native repositories' release-producing `.gitlab-ci.yml` files, keeps GitHub jobs supplemental, defines `windows-builder-arm64` and `install-arm64`, lands audio before libopenshot before openshot-qt, and identifies provisioning of the self-hosted production runner as a maintainer gate.
- expected behavior: The production artifact chain must be owned and validated bottom-up without replacing existing lanes.
- resolution evidence: PR A publishes the audio artifact; PR B consumes that exact artifact; PR C consumes PR B; architecture-specific names prevent collision with x64/x86; runner provisioning is explicit rather than assumed.

## RISK-003 - The native dependency closure is not a plan

- severity: high
- disposition: open
- location/evidence: `DESIGN.r1.md:35-58,67,71-74,96-100,109,128-130,133-138`
- observed behavior: The design names the major dependency families, selects MSYS2 as the preferred producer, requires a spike and PE-machine inventory, and forbids silent architecture mixing. It does not provide a complete bill of materials with producer, package/version constraint, checksum, license, build configuration, target triplet, optionality, and smoke test. OpenMP and the complete transitive runtime/plugin closure are not assigned; ASIO alone receives an explicit optional-feature policy.
- expected behavior: Every native or redistributed input must be traceable under the RISK-001 contract, and optional features must have explicit ship/disable behavior.
- required design correction: Add a dependency BOM covering Python, PyQt6/sip, Qt modules/plugins, SWIG runtime, FFmpeg configuration/codecs/devices, OpenCV and Protobuf policy, OpenMP, ZeroMQ/cppzmq, jsoncpp, babl/ImageMagick, cx_Freeze-generated bases/hooks, OpenShotAudio, and Windows redistributables. For each entry specify producer, target triplet, pin/checksum, license, configuration, required/optional status, package owner, and import/load/feature smoke test; define user-visible behavior for every disabled optional feature.

## RISK-004 - The proposed CI gate cannot prove a native packaged application

- severity: high
- disposition: open
- location/evidence: `DESIGN.r1.md:75,81-82,99-101,107-114,130-131`
- observed behavior: Architecture-header checks, native Python/import/QWidget tests, native CTest/render, frozen launch, package metadata, and install-launch-export-uninstall are now separate gates. The package gate still does not specify an offscreen startup oracle, Qt platform/image/media plugin loading, inspection of modules loaded by the running installed process, or an assertion that no emulated x64 process/module participated. Static inspection of the frozen directory does not cover system-resolved or dynamically loaded modules.
- expected behavior: Source, frozen, and installed execution must each prove native Arm64 process identity and complete runtime/plugin closure.
- required design correction: Define commands and pass criteria for offscreen frozen and installed launches; load representative Qt platform, image, icon, and media plugins; capture the process architecture and loaded-module list; machine-check every non-system loaded module; fail on WOW64/x64 process or module evidence, missing/doubled Qt DLLs, plugin-load warnings, or unresolved imports. Run this against both unpackaged and installed Inno/MSIX candidates.

## RISK-005 - Golden determinism is underspecified and may reject valid FFmpeg outputs

- severity: high
- disposition: open
- location/evidence: `DESIGN.r1.md:75,81,111-112`
- observed behavior: The design correctly compares decoded frame and normalized PCM hashes rather than container bytes and defines exact frame/sample counts. It still leaves the software codecs, pixel/sample formats, encoder options, thread count, timestamps/time bases, metadata normalization, codec-padding bound, and reference hashes unspecified. It also omits the required unavailable-codec, open, write, close, and cancellation failure tests.
- expected behavior: The oracle must be reproducible and must distinguish semantic corruption from valid encoder/container variation while exercising failures.
- required design correction: Name and pin the CI video/audio codecs and all deterministic settings; define synthetic input values, frame/sample formats, time bases, thread count, metadata policy, decoded hash-generation procedure, committed expected hashes, and any exact padding tolerance. Add assertions for unavailable codec and failed writer open/write/close plus cancellation cleanup and partial-output behavior.

## RISK-006 - Installer architecture, upgrade, signing, and coexistence failure paths lack acceptance criteria

- severity: high
- disposition: open
- location/evidence: `DESIGN.r1.md:54-55,79-80,100-101,109,113-124,130-131,138`
- observed behavior: The design supplies canonical lane, prefix, manifest, filename, and Inno architecture mappings and requires Arm64 metadata, signing ownership, clean install/uninstall, and rollback by withdrawing only the Arm asset. It does not decide AppId/package identity and x64-to-Arm64 upgrade versus coexistence behavior, nor test upgrade, downgrade rejection, transactional failure/rollback, signature and signed-uninstaller validity, file associations, firewall cleanup, or MSIX publisher failures.
- expected behavior: Package identity and migration semantics must be explicit and exercised on physical Arm64 Windows, including failure paths.
- required design correction: Specify Inno AppId/default-directory and MSIX identity policy; decide and document x64-to-Arm64 upgrade, downgrade, repair, and side-by-side behavior. Add manifest/payload architecture inspection, installer/MSIX/signature verification, x64-to-Arm64 migration, downgrade rejection, interrupted/failed install rollback, invalid publisher/certificate failure, launch, association activation, firewall-rule cleanup, uninstall cleanup, and signed-uninstaller tests on physical Arm64 hardware.

## RISK-007 - Current upstream release and issue state is not incorporated

- severity: medium
- disposition: open
- location/evidence: `DESIGN.r1.md:13-15,94-103,135,139`; live GitHub state checked 2026-08-27
- observed behavior: The design accurately records current releases, open issue `#5853`, and the three coordinated release PRs, and requires rebasing and regenerated evidence. It still does not select either the active release branches or post-release-merge `develop` as the implementation baseline, so cross-repository version/SO compatibility remains undecided.
- expected behavior: One baseline and compatibility contract must be selected before artifact production.
- required design correction: Name the target branch and commit in each repository after maintainer coordination; record expected OpenShotAudio/libopenshot versions and SO/API identities in artifact metadata; require all three PRs to rebuild from that baseline and invalidate evidence whenever one baseline SHA or version contract changes.

## RISK-008 - Windows Arm hardware behavior coverage is too narrow

- severity: medium
- disposition: open
- location/evidence: `DESIGN.r1.md:101,116-120,131`
- observed behavior: The design adds physical-device provenance, repeated performance runs, clean package lifecycle, software export, and an explicit WASAPI baseline/optional-ASIO distinction. It still omits preview and timeline playback, audio device enumeration/input/recording, unavailable hardware-encoder fallback, sleep/resume, long and non-ASCII paths, low-memory behavior, repeated launch/export stability, crash/log thresholds, and process/module architecture capture on hardware.
- expected behavior: Physical acceptance must cover the user-visible native stack and representative Windows Arm failure paths.
- required design correction: Add a physical-device matrix with explicit pass/fail thresholds for GUI preview, timeline playback, output/input device enumeration and recording, WASAPI, software export, available and unavailable hardware-codec paths and fallback, sleep/resume, long/non-ASCII project and media paths, constrained-memory behavior, repeated launch/export, crash-free operation, logs, clean install/upgrade/uninstall, and native process/module evidence.

## New findings

None.

## Verdict basis

`REVISE` is required because RISK-001 remains open at critical severity and RISK-003 through RISK-006 remain open at high severity. The selected architecture is credible and the corrections are designable, so `NO-GO` is not warranted; `GO` is prohibited until the immutable ABI/BOM, native runtime proof, deterministic render oracle, and package migration/failure criteria are explicit.

confidence: high
The verdict is supported by direct comparison of the accepted findings with the complete r1 design, current repository evidence, and live issue/PR state checked on 2026-08-27.