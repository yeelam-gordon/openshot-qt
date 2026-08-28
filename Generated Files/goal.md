# OpenShot Windows Arm64 native-release plan

## Decision and scope

Add an additive native Windows Arm64 lane to the three-repository release graph using one immutable MSYS2 `CLANGARM64` ABI contract. Build and land bottom-up as three separately owned PRs: `libopenshot-audio`, `libopenshot`, then `openshot-qt`. Existing x64/x86 lanes remain unchanged, GitLab remains the production artifact chain, and matching GitHub Actions lanes are supplemental presubmits only.

The target is post-4.0-release-merge `develop`, after maintainers merge or supersede `openshot-qt#6075`, `libopenshot#1082`, and `libopenshot-audio#170`. G0 must then pin all three SHAs and the OpenShot 4.0.0, libopenshot 1.0.0/SO 31, and libopenshot-audio 1.0.0/SO 10 contract. Any baseline change invalidates downstream evidence.

## Immutable technical outcome

- Contract identity: `windows-arm64-clangarm64-v1`.
- Target: Windows 11 Arm64, PE/COFF `Machine=ARM64` (`0xAA64`).
- Environment: MSYS2 `CLANGARM64`, `C:\msys64\clangarm64`, `aarch64-w64-mingw32`, Clang/libc++/UCRT, and Ninja.
- Runtime: MSYS2 Arm64 CPython 3.14.7-1, PyQt6 6.11.0-1/sip 13.12.0-1, and Qt 6.11.2; packaged builds force `OPENSHOT_QT_API=pyqt6` and libopenshot uses `USE_QT6=ON`.
- Dependency source: one signed, checksummed MSYS2 snapshot and exact producer artifacts. Official CPython, PyPI Qt wheels, MSVC-built Qt, MINGW32/MINGW64 binaries, x64 emulation, and automatic binding/runtime fallback are prohibited.
- Product boundaries: preserve the current Qt selector, SWIG module and QWidget bridge, JUCE graph, enabled dependency features, project formats, and user data unless a named gate reproduces a defect.
- Packaging: produce native `arm64` Inno and MSIX candidates while preserving existing production identities and defined x64-to-Arm64 replacement behavior.

## Required proof

G0-G13 in `design-spec.md` are blocking acceptance gates, not claimed successes. They cover baseline and dependency locking; PE/import purity; Qt ABI, exact plugin inventory, and QWidget interoperability; native audio and library artifacts; cx_Freeze; identical source/frozen/Inno/MSIX probes; deterministic semantic rendering and writer failures; package identity, signing, migration, rollback, and cleanup; and a two-device physical Windows Arm64 matrix.

Claims requiring a native runner, production credentials, signed installers, or physical Arm64 hardware remain open until their owning gates produce evidence. In particular, this AMD64 documentation workspace does **not** claim a successful Arm64 import, freeze, render, package, signature, migration, device test, or performance result.

## Success criteria

1. G0 freezes the coordinated post-4.0 three-repository SHA/version/SO baseline.
2. Every native or redistributed input is lock-owned, checksummed, licensed, and recursively proven ARM64.
3. Immutable PR A and PR B artifact contracts are consumed by exact URL/job ID and digest; no branch fallback is allowed.
4. The same explicit Qt image/icon/media/native-module probe passes independently at source, frozen, Inno-installed, and MSIX-installed stages.
5. The independent stdlib-only oracle and real writer path pass all G9 semantic and failure assertions.
6. Inno/MSIX inspection, signing, upgrade/repair/downgrade, rollback, and uninstall assertions pass.
7. All mandatory G13 rows pass on both required physical device classes before stable promotion.

## Non-goals and no-go policy

Do not consolidate repositories, redesign the Qt selector, rebuild Qt from source, remove required features, mix ABIs, add unrelated FFmpeg/OpenCV work, cover macOS/Linux Arm, claim ASIO certification, or publish unsupported performance promises. Stop on baseline disagreement, mutable or missing inputs, non-ARM64/duplicate/out-of-root modules, absent or warning-producing required plugins, QWidget failure, silently disabled features, incomplete dependency/license closure, any required stage or golden failure, unsafe package replacement, signing/cleanup failure, or incomplete mandatory hardware evidence.

The only architectural fallback is a separately approved, consistently rebuilt MSVC/official-Qt contract. PySide6, cross-compilation, and x64 emulation are not automatic fallbacks.
