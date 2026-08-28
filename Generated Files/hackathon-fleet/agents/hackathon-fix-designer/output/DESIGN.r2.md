# DESIGN r2 - Windows Arm64 native release lane

investigated_at: 2026-08-27T14:58:19Z

## Decision

Add a native Windows Arm64 lane to the existing three-repository release graph, built entirely in the MSYS2 `CLANGARM64` environment. The lane uses MSYS2 Arm64 CPython, PyQt6, Qt 6, Clang/LLVM, libc++, UCRT, and all linked native dependencies from one locked repository snapshot. It must not use official CPython, PyPI Qt wheels, MSVC-built Qt, MINGW64 binaries, or x64 emulation in the packaged process.

Land and validate from the bottom up: `libopenshot-audio`, then `libopenshot` and its SWIG module, then `openshot-qt` freeze/Inno/MSIX/signing. Keep one PR and production-artifact owner per repository. GitHub Actions can provide presubmit evidence, but the existing GitLab jobs remain the release-producing chain (`libopenshot-audio\.gitlab-ci.yml:60-110`, `libopenshot\.gitlab-ci.yml:94-160`, `openshot-qt\.gitlab-ci.yml:106-257`).

Target **post-4.0-release-merge `develop`**, not the current pre-4.0 commits or an independently modified release branch. As verified with `gh pr view` on 2026-08-27, [openshot-qt#6075](https://github.com/OpenShot/openshot-qt/pull/6075), [libopenshot#1082](https://github.com/OpenShot/libopenshot/pull/1082), and [libopenshot-audio#170](https://github.com/OpenShot/libopenshot-audio/pull/170) are open from `release-20260725` into `develop`; their declared contract is OpenShot 4.0.0, libopenshot 1.0.0/SO 31, and libopenshot-audio 1.0.0/SO 10. No production Arm artifact may be built until those merges, or equivalent maintainer-selected commits carrying that version contract, are pinned in the cross-repository lock.

## Accepted-finding disposition

| Finding | Disposition in this revision | Blocking evidence |
| --- | --- | --- |
| RISK-001 | Resolved by the single pinned CLANGARM64 ABI contract below. Packaged builds force `OPENSHOT_QT_API=pyqt6`, `USE_QT6=ON`, and reject any second Qt family or non-Arm PE before QWidget interop. | ABI-lock and Qt-provenance gates G1-G3. |
| RISK-002 | Resolved by adding both native `.gitlab-ci.yml` files, runner provisioning, versioned artifacts, and bottom-up producer-to-consumer flow. | Production-flow gates G4-G6. |
| RISK-003 | Resolved by the dependency BOM, explicit optional-feature policy, signed repository snapshot, checksums, licenses, and import-closure scan. | Dependency-lock gate G1; cx_Freeze gate G7. |
| RISK-004 | Resolved by separate source/native, frozen-directory, Inno-installed, and MSIX-installed Arm64 acceptance, including process/module architecture checks. | Packaged-native gates G8-G11. |
| RISK-005 | Resolved by a lossless, synthetic FFV1/PCM oracle based on decoded frame/PCM hashes rather than container bytes, plus writer failure/cancel tests. | Golden-render gate G9. |
| RISK-006 | Resolved by exact architecture mappings, stable identity/upgrade policy, package inspection, signature checks, migration/failure tests, and physical Arm64 install lifecycle. | Packaging and migration gates G10-G12. |
| RISK-007 | Resolved by choosing post-4.0-merge `develop`, pinning all three SHAs/versions/SO values, and requiring evidence regeneration after baseline selection. | Release-baseline gate G0. |
| RISK-008 | Resolved by the physical-device matrix covering GUI, preview, playback, audio, export/fallback, sleep, paths, memory pressure, repetition, and install lifecycle. | Hardware gate G13. |

## Evidence and root cause

- The source-proven baseline commits are `openshot-qt` `9cd2b3f3ee9024c3496487a2de30a402515ed659`, `libopenshot` `eac81cf91555438c54fbadef7fdd05bf803f26ee`, and `libopenshot-audio` `48516e0b64b9f3ddf2ab79975a42ba2f37023703`; `gh api repos/OpenShot/<repo>/branches/develop --jq .commit.sha` returned those values on 2026-08-27.
- Published baselines remain openshot-qt v3.5.1, libopenshot v0.7.0, and libopenshot-audio v0.6.0 (`gh api repos/OpenShot/<repo>/releases/latest --jq .tag_name`). Open issue [#5853](https://github.com/OpenShot/openshot-qt/issues/5853) remains `OPEN`; no shipped Arm64 implementation is already solved.
- Production Windows jobs are x64/x86 only. The audio job produces `build\install-x64` (`libopenshot-audio\.gitlab-ci.yml:60-80`); libopenshot downloads that exact job (`libopenshot\.gitlab-ci.yml:94-123`); openshot-qt downloads `windows-builder-x64` and freezes from `install-x64` (`.gitlab-ci.yml:106-144`).
- Packaging is architecture-hardcoded in `freeze.py:357-443`, `installer\windows-installer.iss:7-53`, `installer\package_msix.ps1:178-208,270-382`, `installer\build_server.py:575-598,640-685`, and `installer\deploy.py:45-46,94-102,153-161`.
- The native boundary is ABI-sensitive: `_openshot.pyd` links libopenshot to Python and Qt, while the SWIG typemap unwraps a PyQt QWidget through sip and reinterprets it as `QWidget *` (`libopenshot\bindings\python\openshot.i:140-202,252-258`). Qt-major matching alone is insufficient.
- The available machine is AMD64, so this record does not claim a successful Arm64 import, package, render, device test, or performance result. Such claims are blocked by G4-G13, with named owners.

The root cause is an implicit, duplicated architecture contract. Each producer emits only x64/x86 names and prefixes, each consumer downloads those names, the freezer harvests architecture-specific native DLLs, and installer/signing/deployment code recognizes only x86-family outputs. There is no production Arm64 artifact edge and no gate that proves the complete packaged process is native.

## Pinned ABI and toolchain contract

### Contract identity

`windows-arm64-clangarm64-v1` has these immutable properties:

| Dimension | Required value |
| --- | --- |
| Target | Windows 11 Arm64; PE/COFF `Machine=ARM64` (`0xAA64`) |
| Environment | MSYS2 `CLANGARM64`; prefix `C:\msys64\clangarm64`; target triplet `aarch64-w64-mingw32` |
| C/C++ ABI | Clang/LLVM 22.1.8-2, libc++ 22.1.8-1, compiler-rt 22.1.8-2, UCRT, libwinpthread 14.0.0.r302.gd7f3c5201-1 |
| Build tools | CMake 4.4.2-2, Ninja 1.13.2-1, SWIG 4.5.0-1 |
| Python ABI | MSYS2 CPython 3.14.7-1 Arm64 only; debug Python and official python.org/PyPI interpreter mixing prohibited |
| Qt ABI | MSYS2 Qt 6.11.2 (`qt6-base` 6.11.2-2, `qt6-svg` and `qt6-imageformats` 6.11.2-1) |
| Binding ABI | MSYS2 `python-pyqt6` 6.11.0-1 and `python-pyqt6-sip` 13.12.0-1; `OPENSHOT_QT_API=pyqt6` |
| libopenshot configuration | `USE_QT6=ON`, `PYTHON_MODULE_PATH=python`, same Python executable/include/import library, Release configuration |
| C runtime rule | Only the CLANGARM64/UCRT runtime closure may be bundled; no MSVC, MINGW64, MINGW32, x64, or PyPI-bundled Qt DLL |
| Generator | Ninja for all Arm jobs; existing generators stay unchanged in x64/x86 lanes |

MSYS2 documents CLANGARM64 as a distinct Clang/UCRT/libc++ environment at [MSYS2 environments](https://www.msys2.org/docs/environments/). The package versions above were retrieved from `https://packages.msys2.org/package/mingw-w64-clang-aarch64-<name>` on 2026-08-27; package pages link the signed repository artifacts and source packages. `python-pyqt6` declares dependencies on CLANGARM64 `cc-libs`, Python, `python-pyqt6-sip`, and `qt6-base`, keeping the binding in that Qt distribution.

### Lock and provenance

The implementation creates `ci\windows-arm64-packages.lock` in each native repository from one frozen MSYS2 `clangarm64.db` snapshot. It records package filename, exact version-release, source URL, binary URL, SHA-256, license/SPDX expression, and direct dependencies. The same lock digest is embedded as `TOOLCHAIN_LOCK_SHA256` in both producer metadata files and the application metadata.

Package installation is by exact cached artifact filename after `Get-FileHash -Algorithm SHA256`; a live `pacman -Syu` or unversioned `pacman -S` in a release job is forbidden. MSYS2 repository signatures and each cached package hash must both verify. The platform maintainer owns the mirror and lock regeneration. G1 blocks implementation promotion until every BOM row and its transitive PE-producing dependency has a checksum; this is a named gate, not an assertion that today’s moving repository will remain unchanged.

The Qt provenance test records `QLibraryInfo::path(QLibraryInfo.LibrariesPath)`, `QtCore.qVersion()`, the loaded path for `Qt6Core.dll`, and imports of `PyQt6.sip`. It fails unless all paths resolve under the frozen application root and all Qt DLLs have the same package-lock origin. Packaged auto-fallback is prohibited: absence or failure of PyQt6 is a hard startup/test failure, not permission to load PySide6 or PyQt5. `src\qt_api.py` already accepts the environment override (`src\qt_api.py:2284-2486`) and does not require architecture work.

## Dependency BOM and ownership

| Input / exact pin | Source and target | Feature/license policy | Owner and proof |
| --- | --- | --- | --- |
| CPython 3.14.7-1 | MSYS2 CLANGARM64 package | PSF; package only native stdlib/extensions | openshot-qt packaging owner; `platform.machine()`, `sysconfig`, PE scan |
| PyQt6 6.11.0-1, sip 13.12.0-1 | MSYS2 CLANGARM64, against Qt below | GPL-3/commercial compatibility reviewed by maintainer under existing distribution policy | openshot-qt; binding and QWidget interop |
| Qt 6.11.2 packages | MSYS2 CLANGARM64 `qt6-base`, `qt6-svg`, `qt6-imageformats` | LGPL/GPL components; deploy only required plugins/DLLs and notices | libopenshot + openshot-qt; DLL provenance, image/plugin smoke |
| LLVM/Clang 22.1.8-2, libc++ 22.1.8-1, compiler-rt 22.1.8-2, `llvm-openmp` 22.1.8-1 | MSYS2 CLANGARM64 | Apache-2.0 with LLVM exceptions; OpenMP is required by `src\CMakeLists.txt:489-503` | native-repo CI owners; compile/link and `libomp.dll` import proof |
| OpenShotAudio 1.0.0/SO 10 at locked SHA | PR A artifact `libopenshot-audio-1.0.0-so10-windows-arm64-<sha>.zip` | LGPL-3.0; ASIO excluded from baseline, WASAPI required; ASIO remains optional (`CMakeLists.txt:211-230`) | libopenshot-audio owner; CTest/device gates |
| libopenshot 1.0.0/SO 31 at locked SHA | PR B artifact `libopenshot-1.0.0-so31-cp314-qt6.11-windows-arm64-<sha>.zip` | LGPL-3.0; includes `_openshot.pyd` and metadata | libopenshot owner; CTest/import/render gates |
| FFmpeg 9.0.1-3 | MSYS2 CLANGARM64 | LGPL/GPL configuration and enabled codecs captured verbatim from package build info. Release requires demux/decode and FFV1, PCM, Matroska; `gdigrab`/`dshow` capability recorded, not assumed (`src\CMakeLists.txt:421-487`) | libopenshot owner; `ffmpeg -buildconf`, codec/device inventory, golden render |
| OpenCV 5.0.0-3 + Protobuf 35.1-2 | MSYS2 CLANGARM64 | Keep `ENABLE_OPENCV=ON`; preserve Stabilizer/Tracker/Object Detection. Build/configure incompatibility blocks release rather than silently disabling (`CMakeLists.txt:73-76`, `src\CMakeLists.txt:542-610`) | libopenshot owner; configure summary and one OpenCV-backed smoke per feature family |
| ZeroMQ 4.3.5-5 + cppzmq 4.11.0-1 | MSYS2 CLANGARM64 | Required socket/logging path; MPL/LGPL terms and notices captured (`src\CMakeLists.txt:505-523`) | libopenshot owner; link/import closure and message-loop smoke |
| babl 0.1.128-1 | MSYS2 CLANGARM64 | Keep advanced chroma keying enabled; LGPL notice; package only referenced extensions (`src\CMakeLists.txt:525-540`, `freeze.py:379-384`) | libopenshot + freezer owners; effect smoke and extension load |
| ImageMagick 7.1.2.30-1 | MSYS2 CLANGARM64 | Keep `ENABLE_MAGICK=ON`; preserve image/text reader features; package policy/license delegates reviewed (`CMakeLists.txt:73`, `src\CMakeLists.txt:232-288`) | libopenshot owner; image/text read-write smoke |
| jsoncpp 1.9.8-1 | MSYS2 CLANGARM64 | Use system package (`USE_SYSTEM_JSONCPP=ON`, `DISABLE_BUNDLED_JSONCPP=ON`) to make provenance unambiguous | libopenshot owner; CMake target and PE closure |
| NumPy 2.5.2-1 | MSYS2 CLANGARM64 | Existing numerical runtime; BSD license | openshot-qt owner; native import |
| cx_Freeze 8.7.0 sdist | PyPI sdist built by the pinned Arm64 Python/toolchain; SHA-256 `3d6aed189f96fb6d13182bbc6f33f73d14526fc6fec934286d0456e31faf1543` | PSF license; PyPI has no native win_arm64 wheel. Merged Arm support is documented in [cx_Freeze#2943](https://github.com/marcelotduarte/cx_Freeze/pull/2943), but runtime success is G7 | openshot-qt owner; base EXE PE scan, hooks, freeze/startup |
| PyOpenGL 3.1.10 | PyPI pure-Python wheel locked with upstream SHA-256 | BSD; omit optional `PyOpenGL-accelerate` on Arm because only an unproven sdist exists; this changes optimization only, not OpenGL API availability | openshot-qt owner; OpenGL import and software/offscreen startup |
| Windows system DLLs, SDK tools, Inno Setup, MSIX Packaging Tool, SignTool | Maintainer-pinned Arm-capable builder image | Redistributable/system inputs only; exact tool versions and image digest enter lock metadata | release-infrastructure owner; package/signing gates |

FFmpeg’s complete `-buildconf`, OpenCV’s build information, Qt build key, `python -VV`, compiler version, and `pacman -Q` are immutable build artifacts. Any BOM drift creates a new contract revision and reruns all downstream gates. The open [opencv-python#806](https://github.com/opencv/opencv-python/issues/806) is not used as a blocker because this design consumes the MSYS2 native package, not `opencv-python`; it remains risk evidence for why G1/G5 cannot be skipped.

Every produced or bundled `.exe`, `.dll`, and `.pyd` is enumerated recursively. `llvm-readobj --file-headers --coff-imports` must report ARM64 and all non-system imports must resolve inside the package. Duplicate basenames with different hashes, unresolved imports, absolute build-prefix references, and x86/x64 machine types fail. A runtime module inventory from the launched process is compared to the static inventory.

## Recursive production graph and artifact contract

```text
OpenShot Arm64 Inno/MSIX candidate                         [openshot-qt GitLab]
|-- frozen MSYS2 CPython 3.14.7 Arm64 process
|   |-- PyQt6 6.11.0 + sip 13.12 + Qt 6.11.2             [same package lock]
|   |-- cx_Freeze Arm64 base executable                   [source-built, G7]
|   `-- openshot.py + _openshot.pyd                       [PR B artifact]
|       `-- libopenshot 1.0.0 / SO 31 Arm64
|           |-- exact same Qt 6.11.2 DLLs
|           |-- FFmpeg 9.0.1 libraries
|           |-- OpenCV 5.0.0 + Protobuf 35.1
|           |-- OpenMP, ZeroMQ/cppzmq, babl, ImageMagick
|           `-- OpenShotAudio 1.0.0 / SO 10 Arm64         [PR A artifact]
|               |-- bundled JUCE modules
|               `-- Windows SDK/system WASAPI dependencies
|-- Inno architecture/manifest/signature                  [openshot-qt]
`-- MSIX identity/manifest/signature                      [openshot-qt]
```

Each producer ZIP contains:

- `artifact-contract.json` with schema version, repository, commit SHA, source version, SO version, target triplet, PE machine, Python SOABI, Qt build/version, compiler/CRT, package-lock digest, feature flags, producing pipeline/job, and SHA-256 for every payload file;
- the install tree under `install-arm64`;
- test reports, build configuration, package inventory, PE/import inventory, licenses/notices, and SBOM.

Consumers accept an explicit artifact URL/job ID and expected payload digest. The current branch-then-`develop` fallback (`libopenshot\.gitlab-ci.yml:101-103`; `.gitlab-ci.yml:120-122`) is forbidden for Arm64: missing or mismatched producer metadata fails. Artifact names are versioned and immutable; `windows-builder-arm64` is the stable GitLab job name, while the ZIP filename carries version/SO/SHA.

## Exact change surface and ownership

### PR A - `OpenShot/libopenshot-audio`

| File/symbol | Required change |
| --- | --- |
| `.gitlab-ci.yml` | Add production `windows-builder-arm64`, exact package-lock install, CLANGARM64/Ninja configuration, CTest, artifact metadata, PE/import scan, and immutable artifact. Trigger libopenshot only after success. |
| `.github\workflows\ci.yml` | Optional native Arm presubmit using the same lock; never substitute its output for GitLab release artifacts. |
| `ci\windows-arm64-packages.lock` and validation scripts | New lock/provenance and reusable architecture/import validator. |
| `CMakeLists.txt` | No planned product change. Change only for a reproduced Arm compile/device defect; retain WASAPI and optional ASIO semantics at `:152-230`. |
| Tests | Add/extend audio-device-independent buffer/resampling tests if absent; physical devices remain G13. |

### PR B - `OpenShot/libopenshot`

| File/symbol | Required change |
| --- | --- |
| `.gitlab-ci.yml` | Add production `windows-builder-arm64`; consume PR A by exact contract/digest; configure locked CLANGARM64 dependencies; run all CTest and integration tests; publish versioned artifact. |
| `.github\workflows\ci.yml` | Optional same-lock native Arm presubmit. |
| `ci\windows-arm64-packages.lock` and validation scripts | Same lock digest and contract validator as PR A. |
| `bindings\python\CMakeLists.txt:23-35,91-106` | Replace legacy unpaired Python discovery with `FindPython3` Interpreter + Development.Module only if the configure spike confirms it cannot enforce CPython 3.14 Arm64. Assert interpreter, headers, import library, and SOABI from one prefix. |
| `bindings\python\openshot.i:140-202,252-258` | No planned pointer rewrite. Add QWidget interoperability test; change this symbol only if G5 reproduces a defect. |
| `src\CMakeLists.txt:224-230,358-419,421-610` | No feature removal. Pass explicit roots/options and fail if required pinned Qt, FFmpeg, OpenMP, ZeroMQ, OpenCV/Protobuf, babl, or ImageMagick is absent. |
| `tests\FFmpegWriter.cpp`, `tests\Timeline.cpp`, new binding smoke | Add the deterministic native render and QWidget pointer smoke described below. |

### PR C - `OpenShot/openshot-qt`

| File/symbol | Required change |
| --- | --- |
| `.gitlab-ci.yml` | Add `win-arm64`, `windows:msix:package:arm64`, and `win-sign-arm64`; consume exact PR B artifact; force PyQt6; run source/native, frozen, package, architecture, and render gates before signing. |
| `freeze.py:142-153,357-443,787-810` | Add canonical `arm64/install-arm64/clangarm64` mapping; remove warning-shaped fallbacks from Arm release closure; harvest only lock-owned dependencies/plugins; fail on missing required DLL. |
| `installer\windows.manifest` | Generate processor architecture `arm64`; inspect the embedded manifest after `mt.exe`. |
| `installer\windows-installer.iss:7-53,129-158` | Map Inno values to `arm64`; keep the existing AppId and default directory for in-place x64-to-Arm64 upgrade; preserve signed uninstaller and cleanup behavior. |
| `installer\package_msix.ps1:178-208,270-382` | Parameterize architecture and source name, select only `OpenShot-*-arm64.exe`, set/inspect manifest architecture `arm64`, reject any captured installer or wrong-machine payload. |
| `installer\build_server.py:575-598,640-685` | Replace Boolean 32-bit selection with canonical architecture enum; support `install-arm64`, `-arm64.exe/.msix`, Arm signing, and fail-closed metadata. |
| `installer\deploy.py:45-46,94-102,153-161` | Parse and publish `arm64`; read architecture-specific metadata without changing x64/x86 behavior. |
| `installer\openshot-msix-template.xml` if present on selected baseline | Generate/validate processor architecture, identity, publisher, executable, and capabilities for Arm64. PR #6075 already touches this file, so rebase rather than duplicate its changes. |
| `src\tests\test_export_golden.py` and package-smoke scripts | Add the semantic golden render and installed/frozen launch tests. |
| `src\qt_api.py`, `src\windows\export.py` | Reference-only unless a gate reproduces a product defect. Existing selector and writer loop remain stable (`export.py:1176-1309`). |

Builder provisioning is owned outside product source by release infrastructure: a physical or virtual native Windows Arm64 GitLab runner tagged `windows-arm64`, pinned MSYS2 mirror/image, package cache, Inno/MSIX/Windows SDK tools, and signing access. Provisioning evidence is the runner-image digest and tool inventory attached to G1. Lack of this runner blocks production CI, not source design.

## Bottom-up implementation and validation sequence

1. **G0 - baseline freeze (release maintainers):** merge or supersede #6075/#1082/#170; record three exact `develop` SHAs, OpenShot/lib versions and SO values in a cross-repo lock; update #5853 with links to three separate draft PRs. Re-run source-line and dependency evidence against these SHAs.
2. **G1 - dependency lock (release infrastructure):** archive the signed MSYS2 snapshot, populate every BOM checksum/license/dependency, build cx_Freeze from the pinned sdist, and emit the runner-image/tool inventory. Stop on unavailable or wrong-machine input; do not substitute another ABI.
3. **PR A / G4:** build `libopenshot-audio` natively, run CTest and PE/import scans, publish its immutable artifact and contract. Retain existing x64/x86 jobs unchanged.
4. **PR B / G5-G6:** consume only PR A’s digest, build libopenshot/SWIG, run all CTest, native import, QWidget, dependency-feature, and golden-native tests, then publish PR B’s immutable artifact.
5. **PR C / G7-G11:** consume only PR B’s digest, run source integration, freeze, inspect closure, launch offscreen, render golden output, build and inspect Inno/MSIX, install-launch-render-uninstall test candidates, and only then hand artifacts to signing.
6. **G12 (release maintainers):** verify production signatures and migration/failure scenarios using a prerelease identity and candidate. Publish only a prerelease Arm64 asset.
7. **G13 (hardware QA owner):** execute the physical-device matrix. Stable release promotion requires all mandatory rows and attached logs; performance numbers are reported only from these runs.

No consumer PR is merged until its producer artifact exists and its contract is accepted. PRs may be developed concurrently, but validation and landing remain ordered A, B, C.

## Automated acceptance

### G2-G3 - ABI, Qt provenance, and architecture purity

- Before QWidget use, native Arm64 Python imports `openshot`, `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, and `PyQt6.sip`; reports CPython 3.14, Arm64, Qt 6.11.2, PyQt 6.11.0, and the expected SOABI.
- Construct `QApplication` with `QT_QPA_PLATFORM=offscreen`, create a `QWidget`, pass it through the real libopenshot QWidget-accepting API, exercise `QtPlayer` renderer-object round-trip, and destroy it without exception, truncation, or crash.
- Static PE/import scan reports ARM64 for launcher, CLI launcher, Python executable/extensions, `_openshot.pyd`, OpenShot DLLs, Qt DLLs/plugins, cx_Freeze base, FFmpeg/OpenCV and every bundled PE.
- Runtime module inventory from the frozen and installed process contains no x86/x64 module, no module outside the package/System32 allowlist, and exactly one `Qt6Core.dll` hash. Process architecture is read with `IsWow64Process2`: process machine is ARM64 and native machine is ARM64; `x86`, `x64`, `ARM64EC`, or emulation fails.

### G8 - source/native and frozen application

- Source tree runs its existing targeted tests plus native import, binding, Qt image load (`PNG`, `JPEG`, `SVG`), platform plugin load, babl, ImageMagick, OpenCV, ZeroMQ, and FFmpeg decode smoke.
- Frozen `openshot-qt.exe` starts with an isolated profile and offscreen Qt, reaches an explicit ready marker, opens a tiny project, loads images/plugins, performs the golden render, and exits cleanly within 60 seconds. `launch.py -V` alone is not acceptance.
- Missing Qt platform/image plugin, missing DLL, wrong architecture, wrong binding, duplicate Qt, and removed codec each produce a nonzero test result and actionable log.

### G9 - semantic golden render and failures

The oracle is generated in memory: 64x36 RGBA frames for exactly 60 frames at 30/1 fps, with frame number encoded in deterministic color blocks, plus exactly 96,000 stereo samples per channel at 48,000 Hz generated from integer PCM values. It uses no fonts, clocks, random values, filesystem media, hardware decoder, or external assets.

Encode with `FFmpegWriter` to Matroska using software-only `ffv1`, `rgba` (or one contract-pinned lossless supported pixel format), `pcm_s16le`, 48 kHz stereo, one encoder thread, fixed stream time bases, and empty/fixed title/comment/creation-time fields. Hardware acceleration is disabled for this oracle. Decode with the locked FFmpeg/OpenShot reader and assert:

- exactly 60 frames, monotonically exact expected PTS values, dimensions/pixel format, and SHA-256 of each decoded pixel plane;
- exactly 96,000 samples per channel, expected audio PTS/count/format, and SHA-256 of normalized little-endian signed 16-bit interleaved PCM;
- stream count, codec IDs, time bases, frame rate, sample rate, and channel layout;
- two independent exports produce identical semantic hashes and normalized stream metadata.

Container byte equality, muxer writing-library strings, file timestamps, offsets, and container-level volatile metadata are explicitly ignored. CI stores expected semantic hashes in the test source and stores the produced file/report on failure.

Negative cases invoke the real writer path and assert cleanup/nonzero failure: unavailable codec, `Open()` failure, first/midstream `WriteFrame()` failure, `Close()` failure, and cancellation after a fixed frame. Each case must leave no success-shaped output, release the writer, stop progress, and propagate the repository’s normal error/cancel signal. Existing mock helper coverage remains, but cannot satisfy G9 (`src\tests\test_export_clips.py:74-104`).

### G10-G12 - package identity, migration, and failure

Canonical mappings are:

| Surface | Arm64 value |
| --- | --- |
| CI lane / dependency job | `win-arm64` / `windows-builder-arm64` |
| install prefix | `build\install-arm64` |
| MSYS2 environment / prefix | `CLANGARM64` / `C:\msys64\clangarm64` |
| PE and application manifest | `arm64` / ARM64 machine `0xAA64` |
| Inno `ArchitecturesAllowed` and `ArchitecturesInstallIn64BitMode` | `arm64` (never `x64compatible`) |
| Inno artifact | `OpenShot-<version>-arm64.exe` |
| MSIX manifest / artifact | `ProcessorArchitecture="arm64"` / `OpenShot-<version>-arm64.msix` |
| release architecture token | `arm64` |

Inno keeps AppId `{4BB0DCDC-BC24-49EC-8937-72956C33A470}` and the current default directory so an Arm64 installer **upgrades/replaces** an emulated x64 installation; side-by-side x64/Arm64 machine-wide installs are unsupported because shared file associations, firewall rule, directory, and AppId would conflict (`windows-installer.iss:23-53,124-158`). The installer must detect an existing newer version and refuse downgrade. Upgrade preserves user projects/preferences, removes old x64 program files before installing Arm64, re-registers `.osp`, and leaves one uninstall entry. Rollback after failed replacement restores a launchable prior x64 installation or leaves the prior installation untouched; partial mixed-architecture directories fail acceptance.

MSIX retains the maintainer-approved package family/identity from the post-#6075 baseline so Windows performs architecture replacement under one identity. Publisher must exactly match the signing certificate subject. Side-by-side testing is limited to an explicitly different prerelease identity; production identities do not coexist.

On physical Arm64 Windows, test both signed formats:

1. Inspect Inno directives, embedded application manifest, every payload PE, unpacked `AppxManifest.xml`, package identity/version/architecture, and file hashes.
2. `Get-AuthenticodeSignature` and `signtool verify /pa /all /v` succeed for installer, launcher/DLL signing policy, signed uninstaller, and MSIX; timestamp chain is valid.
3. Clean install, silent install, normal launch, `.osp` association launch, firewall opt-in creation, golden export, and uninstall leave no install directory, uninstall entry, association, task, package registration, or firewall rule.
4. Upgrade the latest signed x64 release to Arm64, launch/render, then uninstall. Test same-version repair, newer-version upgrade, and downgrade refusal.
5. Inject and assert safe failure for unsigned/wrong-publisher package, altered payload, unavailable timestamp service, signing tool without Arm/MSIX support, denied elevation, locked destination file, low disk, interrupted installer, malformed architecture metadata, and MSIX registration failure. No failed candidate is uploaded or reported successful.

## Physical Windows Arm64 matrix - G13

Run on at least two physical devices: one Qualcomm Snapdragon X-class Windows 11 device and one older supported Arm64 device. Record device model/SoC, firmware, RAM, GPU/driver, audio devices, Windows build, power mode, thermal/power state, artifact and three source SHAs, toolchain-lock digest, and whether each process/module is native Arm64.

| Area | Procedure | Pass threshold |
| --- | --- | --- |
| Launch/GUI | Ten cold launches and ten warm launches; create/open/save project; exercise dialogs, SVG/PNG/JPEG thumbnails and effects UI | 20/20 reach interactive UI within 30 s; 0 crashes/hangs; all modules Arm64 |
| Preview/playback | Play a 1080p30 H.264/AAC reference timeline for 10 min; seek 20 fixed positions; scrub and pause/resume | 0 crashes/deadlocks; A/V remains within 100 ms after each settle; no persistent blank frames |
| Audio output | Enumerate devices, switch default output during playback, unplug/replug where supported | Devices enumerate; audio resumes within 5 s; no crash; WASAPI path logged |
| Audio input | Enumerate microphone, record 30 s, play result, deny permission and retry | Successful recording has expected 48 kHz channels/duration within 100 ms; denial is actionable and non-crashing |
| Software export | Run G9 and three 2-minute 1080p30 H.264/AAC software exports | 3/3 complete; decoded frame/audio counts and duration valid; no corruption/crash |
| Hardware codecs | Inventory FFmpeg encoders/decoders; test each available Windows Arm path; request one unavailable codec | Available paths export/decode correctly; unavailable path visibly falls back to the pinned software codec or errors before writing, never silently creates corrupt output |
| Sleep/resume | Suspend for 2 min during idle, playback, and paused export; resume and repeat export | UI responsive within 10 s; playback can restart; export either resumes correctly or fails explicitly with no success artifact |
| Paths/projects | Open/save/render under >240-character and non-ASCII/emoji user/project/media paths | All operations succeed with exact path/content; no mojibake or missing media |
| Memory pressure | Run preview/export with system committed memory raised to 85%, then force a controlled allocation/export failure | No system/app hang; success is valid or failure is explicit and leaves no success artifact |
| Repetition | 25 launch-open-preview-export-exit cycles | 25/25 complete; 0 crash/hang; working-set growth from cycle 5 to 25 is <20% after idle |
| Install lifecycle | Execute G10-G12 clean install, x64 upgrade, downgrade refusal, repair, association/firewall, uninstall for Inno and MSIX | Every mandatory assertion passes; no mixed architecture or stale registration |

Performance results record median and range from three cold and three warm runs, but there is no fixed performance claim or x64 comparison threshold in this port. Hosted CI and emulation cannot satisfy G13. Hardware QA owns results; release maintainers own waiver decisions, and no stable Arm64 asset may ship with a waived crash, architecture, render, audio-output, upgrade, signature, or uninstall failure.

## Migration, rollback, gates, and no-go rules

The source/artifact lane is additive and does not change project formats or user data. Existing x64/x86 jobs, names, prefixes, generators, signing, and release assets remain unchanged. Architecture parsing becomes an enum with explicit legacy mappings, not a changed Boolean default.

Rollback before publication disables only Arm64 trigger/package/sign jobs and retains failed artifacts/logs. Rollback after prerelease removes only Arm64 prerelease assets and package availability; it does not revoke x64/x86. An installed Arm64-to-x64 rollback is a deliberate uninstall/reinstall unless installer migration tests prove a signed higher-version x64 replacement; automatic architecture downgrade is not promised.

| Gate | Owner | Required artifact/evidence | Blocks |
| --- | --- | --- | --- |
| G0 baseline | Three release maintainers | SHA/version/SO lock after 4.0-series selection | All production implementation |
| G1 dependency/toolchain | Release infrastructure | Signed snapshot, checksummed BOM, licenses, image digest | Native builds |
| G2 architecture/import | CI owners | Static PE/import reports | Artifact publication |
| G3 Qt ABI/provenance | libopenshot + app owners | Qt paths/hashes/version and no-fallback report | QWidget test/package |
| G4 audio build | audio owner | Native CTest and PR A contract | PR B |
| G5 library/binding | libopenshot owner | CTest, import, QWidget, feature smokes | PR B artifact |
| G6 native golden | libopenshot owner | Semantic render report | PR C |
| G7 cx_Freeze | app owner | Arm64 base build/freeze/hook/startup evidence | Package creation |
| G8 frozen startup | app owner | Ready marker, image/plugin/native-module report | Installers |
| G9 packaged golden | app owner | Frozen semantic hashes and negative cases | Signing |
| G10 package metadata | packaging owner | Inno/MSIX manifests, PE closure, identities | Signing |
| G11 installed smoke | packaging owner | Installed native launch/render/uninstall | Prerelease |
| G12 migration/signing | release maintainer | Signature and failure/migration reports | Prerelease/stable |
| G13 hardware | Hardware QA | Completed two-device matrix and logs | Stable release |

No-go conditions are: baseline versions/SO values disagree; a package or producer digest is mutable/missing; Python, SWIG extension, or any bundled module is not ARM64; more than one Qt runtime/provenance appears; QWidget interop fails; a required current feature was silently disabled; dependency closure or license inventory is incomplete; source, frozen, installed, or golden tests fail; package identity cannot safely upgrade x64; signing or uninstall cleanup fails; or G13 mandatory rows lack evidence.

The MSVC/official-Qt stack is the only architectural fallback. It requires a new contract revision rebuilding CPython-extension/native dependencies consistently against MSVC and the exact Qt distribution used by the selected binding; it may not be mixed into this lane. PySide6, cross-compilation, and x64 emulation are not automatic fallbacks.

## Scope and open assumptions

In scope are the locked native dependency assembly, production GitLab lanes, optional matching GitHub presubmits, artifact contracts, SWIG/Qt proof, source/frozen/installed semantic rendering, Inno/MSIX/signing/migration, release naming, and physical hardware protocol.

Out of scope are repository consolidation, Qt selector redesign, Qt source rebuilding without a separately approved contract, unrelated FFmpeg/OpenCV feature work, macOS/Linux Arm, ASIO certification, and unsupported performance promises.

Open runtime assumptions are deliberately gated:

- MSYS2 CPython 3.14 and cx_Freeze 8.7 can produce a working native Arm64 base executable: G7, owned by openshot-qt.
- OpenCV 5.0.0 and Protobuf 35.1 satisfy the selected post-4.0 libopenshot source while preserving all enabled algorithms: G5, owned by libopenshot.
- The production GitLab environment can be provisioned as native CLANGARM64 and the signing/MSIX tools accept the candidate: G1/G12, owned by release infrastructure/maintainers.
- The locked FFmpeg build exposes required software codecs/devices and valid Windows Arm behavior: G5/G9/G13, owned by libopenshot and hardware QA.
- Inno/MSIX retain a recoverable x64-to-Arm64 upgrade under the selected production identities: G12, owned by the packaging/release maintainer.

confidence: high

The design is freeze-ready because it selects one pinned ABI, assigns every dependency and production edge, defines exact change surfaces and measurable source/package/hardware acceptance, and converts every unproven Arm64 runtime claim into an explicit blocking gate with an owner.
