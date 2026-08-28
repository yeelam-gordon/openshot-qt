# DESIGN r3 - Windows Arm64 native release lane

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
| RISK-004 | Resolved by a pinned Qt platform/image/icon/media plugin inventory and identical explicit probes at source, frozen-directory, Inno-installed, and MSIX-installed stages, including loaded-path/module architecture checks. | Qt/plugin and packaged-native gates G3/G8/G11. |
| RISK-005 | Resolved by one fully specified lossless FFV1/BGRA/PCM oracle with numeric formulas, options, time bases/PTS, independently fixed hashes, exact no-padding behavior, and retained writer failure/cancel tests. | Golden-render gate G9. |
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
| Qt ABI | MSYS2 Qt 6.11.2 (`qt6-base` 6.11.2-2; `qt6-svg`, `qt6-imageformats`, `qt6-multimedia`, and `qt6-multimedia-ffmpeg` 6.11.2-1) |
| Binding ABI | MSYS2 `python-pyqt6` 6.11.0-1 and `python-pyqt6-sip` 13.12.0-1; `OPENSHOT_QT_API=pyqt6` |
| libopenshot configuration | `USE_QT6=ON`, `PYTHON_MODULE_PATH=python`, same Python executable/include/import library, Release configuration |
| C runtime rule | Only the CLANGARM64/UCRT runtime closure may be bundled; no MSVC, MINGW64, MINGW32, x64, or PyPI-bundled Qt DLL |
| Generator | Ninja for all Arm jobs; existing generators stay unchanged in x64/x86 lanes |

MSYS2 documents CLANGARM64 as a distinct Clang/UCRT/libc++ environment at [MSYS2 environments](https://www.msys2.org/docs/environments/). The package versions above and plugin ownership below were retrieved from the signed `clangarm64.files` repository database and `https://packages.msys2.org/package/mingw-w64-clang-aarch64-<name>` on 2026-08-27; package pages link the signed repository artifacts and source packages. `python-pyqt6` declares dependencies on CLANGARM64 `cc-libs`, Python, `python-pyqt6-sip`, and `qt6-base`, keeping the binding in that Qt distribution.

### Lock and provenance

The implementation creates `ci\windows-arm64-packages.lock` in each native repository from one frozen MSYS2 `clangarm64.db` snapshot. It records package filename, exact version-release, source URL, binary URL, SHA-256, license/SPDX expression, and direct dependencies. The same lock digest is embedded as `TOOLCHAIN_LOCK_SHA256` in both producer metadata files and the application metadata.

Package installation is by exact cached artifact filename after `Get-FileHash -Algorithm SHA256`; a live `pacman -Syu` or unversioned `pacman -S` in a release job is forbidden. MSYS2 repository signatures and each cached package hash must both verify. The platform maintainer owns the mirror and lock regeneration. G1 blocks implementation promotion until every BOM row and its transitive PE-producing dependency has a checksum; this is a named gate, not an assertion that today’s moving repository will remain unchanged.

The Qt provenance test records `QLibraryInfo::path(QLibraryInfo.LibrariesPath)`, `QLibraryInfo::path(QLibraryInfo.PluginsPath)`, `QtCore.qVersion()`, the loaded path for every required plugin and Qt DLL, and imports of `PyQt6.sip`. At source stage, all non-system paths must be lock-owned files below `C:\msys64\clangarm64`; at frozen, Inno-installed, and MSIX-installed stages they must be below that candidate's application root. Packaged auto-fallback is prohibited: absence or failure of PyQt6 is a hard startup/test failure, not permission to load PySide6 or PyQt5. `src\qt_api.py` already accepts the environment override (`src\qt_api.py:2284-2486`) and does not require architecture work.

## Dependency BOM and ownership

| Input / exact pin | Source and target | Feature/license policy | Owner and proof |
| --- | --- | --- | --- |
| CPython 3.14.7-1 | MSYS2 CLANGARM64 package | PSF; package only native stdlib/extensions | openshot-qt packaging owner; `platform.machine()`, `sysconfig`, PE scan |
| PyQt6 6.11.0-1, sip 13.12.0-1 | MSYS2 CLANGARM64, against Qt below | GPL-3/commercial compatibility reviewed by maintainer under existing distribution policy | openshot-qt; binding and QWidget interop |
| Qt 6.11.2 packages | MSYS2 CLANGARM64 `qt6-base` 6.11.2-2; `qt6-svg`, `qt6-imageformats`, `qt6-multimedia`, `qt6-multimedia-ffmpeg` 6.11.2-1 | LGPL/GPL components; required deployed inventory is `platforms\qoffscreen.dll`, `platforms\qwindows.dll`, `imageformats\qgif.dll`, `imageformats\qico.dll`, `imageformats\qjpeg.dll`, `imageformats\qsvg.dll`, `iconengines\qsvgicon.dll`, `multimedia\ffmpegmediaplugin.dll`, `Qt6Multimedia.dll`, and their locked runtime closure. `qt6-base` owns platform/GIF/ICO/JPEG, `qt6-svg` owns SVG image/icon, `qt6-multimedia` owns the DLL, and `qt6-multimedia-ffmpeg` owns the media plugin. `qt6-imageformats` remains pinned for existing TIFF/WebP/application behavior but adds no required acceptance-plugin filename. Deploy notices. | libopenshot + openshot-qt; exact plugin inventory, provenance, icon/image/media probes |
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
|   |   `-- qwindows/qoffscreen, GIF/ICO/JPEG/SVG, SVG-icon,
|   |       and FFmpeg media plugins                       [exact locked files]
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
- test reports, build configuration, exact Qt plugin inventory, package inventory, PE/import inventory, licenses/notices, and SBOM.

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
| `src\tests\test_export_golden.py`, an independent stdlib-only oracle generator, four-stage Qt probe fixtures, and package-smoke scripts | Add the exact semantic golden render and source/frozen/Inno/MSIX plugin/native launch tests specified in G8-G9. |
| `src\qt_api.py`, `src\windows\export.py` | Reference-only unless a gate reproduces a product defect. Existing selector and writer loop remain stable (`export.py:1176-1309`). |

Builder provisioning is owned outside product source by release infrastructure: a physical or virtual native Windows Arm64 GitLab runner tagged `windows-arm64`, pinned MSYS2 mirror/image, package cache, Inno/MSIX/Windows SDK tools, and signing access. Provisioning evidence is the runner-image digest and tool inventory attached to G1. Lack of this runner blocks production CI, not source design.

## Bottom-up implementation and validation sequence

1. **G0 - baseline freeze (release maintainers):** merge or supersede #6075/#1082/#170; record three exact `develop` SHAs, OpenShot/lib versions and SO values in a cross-repo lock; update #5853 with links to three separate draft PRs. Re-run source-line and dependency evidence against these SHAs.
2. **G1 - dependency lock (release infrastructure):** archive the signed MSYS2 snapshot, populate every BOM checksum/license/dependency, build cx_Freeze from the pinned sdist, and emit the runner-image/tool inventory. Stop on unavailable or wrong-machine input; do not substitute another ABI.
3. **PR A / G4:** build `libopenshot-audio` natively, run CTest and PE/import scans, publish its immutable artifact and contract. Retain existing x64/x86 jobs unchanged.
4. **PR B / G5-G6:** consume only PR A’s digest, build libopenshot/SWIG, run all CTest, native import, QWidget, dependency-feature, and exact golden-native tests, then publish PR B’s immutable artifact.
5. **PR C / G7-G11:** consume only PR B’s digest, run the full Qt platform/image/icon/media probe at source, freeze and repeat it, inspect closure, render exact golden output, build and inspect Inno/MSIX, independently install and repeat the same probe plus render/uninstall for each candidate, and only then hand artifacts to signing.
6. **G12 (release maintainers):** verify production signatures and migration/failure scenarios using a prerelease identity and candidate. Publish only a prerelease Arm64 asset.
7. **G13 (hardware QA owner):** execute the physical-device matrix. Stable release promotion requires all mandatory rows and attached logs; performance numbers are reported only from these runs.

No consumer PR is merged until its producer artifact exists and its contract is accepted. PRs may be developed concurrently, but validation and landing remain ordered A, B, C.

## Automated acceptance

### G2-G3 - ABI, Qt provenance, and architecture purity

- Before QWidget use, native Arm64 Python imports `openshot`, `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, and `PyQt6.sip`; reports CPython 3.14, Arm64, Qt 6.11.2, PyQt 6.11.0, and the expected SOABI.
- Construct `QApplication` with `QT_QPA_PLATFORM=offscreen`, create a `QWidget`, pass it through the real libopenshot QWidget-accepting API, exercise `QtPlayer` renderer-object round-trip, and destroy it without exception, truncation, or crash.
- Before testing, compare the candidate to the required BOM inventory: the ten exact plugin/DLL paths named in the Qt BOM row and every lock-declared dependency must exist; no alternate media backend is accepted. Static PE/import scan reports ARM64 for launcher, CLI launcher, Python executable/extensions, `_openshot.pyd`, OpenShot DLLs, every required Qt DLL/plugin, cx_Freeze base, FFmpeg/OpenCV, and every bundled PE.
- Runtime module inventory from each of source, frozen, Inno-installed, and MSIX-installed processes contains no x86/x64 module, no module outside the stage root/System32 allowlist, and exactly one hash/path each for `Qt6Core.dll`, `Qt6Gui.dll`, and `Qt6Multimedia.dll`. Process architecture is read with `IsWow64Process2`: process machine is ARM64 and native machine is ARM64; `x86`, `x64`, `ARM64EC`, or emulation fails.

### G8 - source/native and frozen application

- One probe program and the same committed fixtures run unchanged from the source interpreter, frozen directory, clean Inno installation, and clean MSIX installation. Run once with `QT_QPA_PLATFORM=offscreen` and once with normal `qwindows`; set `QT_DEBUG_PLUGINS=1`, install a Qt message handler, clear inherited `QT_PLUGIN_PATH`, and capture plugin-loader output, `QCoreApplication.libraryPaths()`, loaded PE paths/hashes, package-lock owners, and `IsWow64Process2`.
- The image probe opens committed 2x2 lossless PNG, JPEG, GIF, ICO, and SVG fixtures through `QImageReader`; each reader must report its expected format, return a non-null 2x2 image, and match its committed canonical RGBA8888 pixel digest. This explicitly loads `qjpeg.dll`, `qgif.dll`, `qico.dll`, and `qsvg.dll`; PNG is retained as a built-in format probe.
- The icon probe constructs `QIcon` from the SVG fixture, requests a 32x32 pixmap, renders it into a transparent `QImage.Format_RGBA8888`, and requires a non-null pixmap plus the committed pixel digest. `QT_DEBUG_PLUGINS` must show `iconengines\qsvgicon.dll` loaded from the expected stage root.
- The media fixture is a committed RIFF/WAVE PCM file containing exactly 4,800 stereo `s16le` sample frames at 48,000 Hz, with left/right values from the G9 formulas for `i=0..4799`; its canonical interleaved PCM SHA-256 is `2eefef4340ebac7010fd20389a475c6086faa0fe7acb8f4ab118df4eee3a3704`. A `QMediaPlayer` with `QAudioBufferOutput` and no audio device loads it from a local file URL, reaches `LoadedMedia`, plays to `EndOfMedia` within 10 seconds, emits exactly 4,800 decoded stereo frames in signed 16-bit little-endian format, and matches that hash. `QT_DEBUG_PLUGINS` must show `multimedia\ffmpegmediaplugin.dll` loaded from the stage root.
- Source stage additionally runs existing targeted tests plus native import, binding, babl, ImageMagick, OpenCV, ZeroMQ, and FFmpeg decode smoke. Frozen and both installed launchers use isolated profiles, reach an explicit ready marker, open a tiny project, run all probes and G9, and exit cleanly within 60 seconds; `launch.py -V` alone is not acceptance.
- Every stage fails nonzero with an actionable report on absent probe output, missing required file/DLL, unsupported fixture, timeout, fallback outside the stage root (outside the locked CLANGARM64 prefix at source), duplicate Qt provenance, any `Cannot load library`/`not a plugin`/dependency/plugin-loader warning, hash mismatch, wrong binding, non-ARM64 loaded module, or removed codec. Inno and MSIX results are separate mandatory reports; a frozen-directory pass cannot satisfy either installed stage.

### G9 - semantic golden render and failures

The oracle uses no fonts, clocks, random values, filesystem input media, hardware decoder, or external assets. For video frame `n=0..59`, row `y=0..35`, and column `x=0..63`, define `R=(3*x+5*y+7*n) mod 256`, `G=(11*x+13*y+17*n) mod 256`, `B=(19*x+23*y+29*n) mod 256`, and `A=255`. The only canonical decoded pixel format is FFmpeg `bgra`, byte order `B,G,R,A`, tightly packed with stride 256, rows top-to-bottom and no row padding. There are exactly 60 64x36 frames; source video time base is `1/30`, frame rate is `30/1`, start PTS is 0, and input frame `n` has PTS `n`.

For audio sample-frame index `i=0..95999`, define signed values `L=((257*i+12345) mod 65536)-32768` and `R=((911*i+23456) mod 65536)-32768`. Canonical audio is exactly 96,000 stereo sample frames, interleaved `L,R` as two's-complement little-endian `s16`, 48,000 Hz, stereo channel layout, source time base `1/48000`, start PTS 0, and sample `i` has PTS `i`. Feed audio in 1,024-sample frames with PTS `0,1024,...,94208`, followed by one 768-sample frame at PTS 95,232. PCM has no codec delay: the decoder must return exactly indexes `0..95999`; no leading/trailing padding, priming, insertion, truncation, or tolerance is allowed.

`FFmpegWriter` writes Matroska with exactly one video and one audio stream. Explicit video settings are codec `ffv1`, pixel format `bgra`, `level=3`, `coder=1` (range coder), `context=1`, GOP size `1`, `slices=4`, `slicecrc=1`, and `threads=1`; hardware acceleration is disabled. Explicit audio settings are codec `pcm_s16le`, sample format `s16`, 48,000 Hz, stereo, and no resampling/dither. Explicit muxer settings are format `matroska`, `fflags=+bitexact`, `flush_packets=1`, `avoid_negative_ts=disabled`, start at zero, and metadata dictionary exactly `title=OpenShot Arm64 Golden`, `comment=oracle-v1`, with no `creation_time`; chapters and attachments are absent. The writer passes the numeric source time bases/PTS above without wall-clock substitution. The Matroska muxer-selected output stream time base is asserted as exactly `1/1000`; expected video timestamps in that time base are `round_nearest_ties_away(n*1000/30)`, yielding `0,33,67,...,1967`, and decoded audio begins at output PTS 0 and covers exactly 2,000 ms. Packet partitioning and individual audio packet PTS are not semantic assertions because valid Matroska/PCM muxing may repartition packets.

An independent reference generator in the openshot-qt test tree must be a stdlib-only program that does not import OpenShot, FFmpeg, Qt, NumPy, or production oracle helpers. It implements the formulas literally, writes raw canonical BGRA and interleaved PCM bytes, calculates one SHA-256 per frame and the PCM SHA-256, and compares its output to the committed manifest before any writer test. The committed fixed outputs are:

- raw concatenated video SHA-256: `a3602aa3a3e5316d9456c97eb8bafe5c97a692ed5c10f3409db763bfb331b83a`;
- interleaved PCM SHA-256: `fb240a5aa9dad1572ba742e9a98cd4d33dc078d57c6d2d7cdbfb077df8cb7cd2`;
- manifest SHA-256, calculated over the 60 lowercase frame hashes each followed by LF, then the lowercase PCM hash followed by LF: `be4c2c85757437afa5861ff92c121af4ec38ef7fd222371881c92511e5e5b1de`.

The 60 committed per-frame hashes, in frame order, are:

```text
7aca7dad93170ab65ac6ab5189ac0047ae6d1b5ba92eabb408bdd1bf5096c999
157e95749f0a2aa27f9833b4fee417142607b7622589a9a2e9dc5cead1c18ab8
bd31d1ffd5fe745c72e0c5cf55dbc4cb4ad9538dfa6b019c8781df0e80a1ae26
c015dc09114dae69c187e48bae5ce0145fe0d1df10999c1773f3a60e5feefbce
d8f7e5dd0dd58ddebca4835aab7080bd96c0b1c6cf9129230017654a6bb8b5f5
aa2f0bfa9ccf688c71002dc4a0911ae0fd3249ecb21766ecece3a129a2b2f273
fd623eeddc1708f20627a51c501676b624419972c266536cf856ef718c70a541
38ffc721d935afb064eb8419a23d9c46f612c77d8ea25afd6672ba046af23086
d6d287f9a6f8155a28c83cc569f22eb0d8d0be70324555bffe31b6be84b21e4c
c343e437d13b5ba1627c9a25da10324645452d27ffab20b86be76e22296b7e7e
6c83707b0d1f5e8ee280b5c34880a251ae0658d97ad9d5c3bb4eb93122885133
2c7c7323db3fa7c8923611c01e5f9ffc2c819fc80bedce349a68436c588d1cf9
23064b31565f9beb82ba9d038b397890f36b472e20e0700f34a9d957e088ee06
719ad0720b15bf77d7aca2ba2f138d7ed7e361df0e481e12783a7efebe264864
01de462136bb768877767abf14cd7efb8b016952be5ebc8cdaecb1fed30c355e
2bb697623b8a0ac4f3d713e44f62de6d160c977d660d0c788301a0980e45e1bf
533e6c67612fe04ff68b2389ac7f71ea4c67abc1e19c681d818f409eb5a6927a
9a99a2cb947209cf024378687990902952856598f24186a4668271df55faf63f
c33f87a732dbbaf2dd45817c391f7073ad76dfdb1c511acc79705665eb8c8c21
48056a4968e3a8dd03d265203689e9467bc4ab4eb135522c618a2ffd0b046897
2d3bdc35e058d682f7c1f5d1bcf83b46fc571be834ae807aeddbe99a8b84cc5c
5250299f22e987169dcf2ffdaf05b0e415c369bc7a530ddf1e748108a455dc3e
975844ece04465d7ad45dac921fcb8126059ceaf40b153b7d28871da49e6f8f5
7d8a8ca09580a91012430f7a535b3dea27237779ce18d7f9b3755c68a9e60e9e
4bbea339da2f90b69119afc31d40c5528b328a0235103390a4d8139f927ab407
53bd8419c2e717ddd2e27c6eea4af2c1b1bdcaad1f4c8bedba16d78967835e63
39708aeaae617ad71758b0f0a38e5c5068d87a8ce7bd4b31326d03f3ef718ef8
07a20e6a8b9b232b3e5d5771463983d18ca1f49fefe74034045a71b5150d0536
2f732b3ec23fdff9ea820e3816ab4845dc05be8837b295fdf62386e3082b09b6
66f8e8b8e9c838f07c1bc699c96a7c9ac2475a957db2238336e116ef7df64b5a
6e31b2ed38fbf69d5bf1b8e634572b6f04cd706d8fdcdf0e03ccf61ac0b195f2
89b38fbacfaf6355a5c32a233725aa07cedd6040dc95c045d71b875bb8d17bbd
6674724495e6a4d68a85ae204331abe7080cee9f2aea315011ee15150db9d3c2
7dc7e75a40c5f13ce4e5552282df9df834c329bacfab52a44454653f6fa92379
62c46fb178c28b982e4d09a9f6dcbaafc51ed3bf85862ff7273c77477cdfd763
71b6d90af7e6d099143e75b04a3afdf15865063e84725964ce96d89fe7d35a83
97256fb17b6947a2b3b2bfe320c5a5fff14ff3ef79eb028813e248e9869849c8
20f99727755a090dae05993494072d8fe7fe64a18eb06ae775b813143d145ebf
29624465055fed82935583b502ddc94b9f65d5c93b440d62b3919802e0c2c4bf
de1849d13f9edfd20bcb440c81db7d6e9167776be8608725a76e920488def46e
c354350a82c70c49b2d7372b899329d9fd910631435b86c5229f41de398edc1f
0affad1cdebe86fcf091b690cf43e5d7cb1e268ee03187f9a6921ffe3cdddffd
cfc9ea1267f6a28863f8d83b4a30f69d92839459f7ceb16f1477f8cb579d9f61
e66528c8186f477635aaed7373117de957d719719b7c785e1491df21d1ee80fc
b09e7482be957d8a4f5eba8d98d7e51645de429127af07bb5f846db3c2c97085
9fe7e9c1a57f7ae8633de7f09debb3d9162c23d196f191150baff9655523107b
2b1635672a2910bf94dd7b4e08441b5f84899a126ac98f9dc4433d6441fa1c5c
b051f1f20fb44534e9ade416bf35185bea81b5534d9e8ff86bd810a88bacc9b6
035e33eb703b869d3414ef2b09ecc675c2bcec5554556a25d2795b0296ee8b57
116b8f5ac9817838e5703d8835bf2123250f9f9d3080adb5e349014eebb71358
e2b0732e7688a12b545b582d50009544c05a2274029cac1dcbf2719b412ec1f7
e93e95a6a9fb6b96d7017dc99c0e6470eafc3b2d349456ffc88a075ae84554f0
472eb8c7eef76322c756ab7acd522e56f5fbfb5543ac9d623c927252e15b8346
fb0d49651fe70d577d0d38e4365d3179eb82dadae7adafc0d44a21157dda2904
cb8613f8a0b04c92a9cce65e028fe7061e67ce2bc9e766f05f2864894b2d5b17
55d9dc84e5d7b0dbe6bd6684fcdb86422bca8b2b37039d6b814bb88bc5f236ed
e01d51a469b9466d7bdc9cf07ca7f0ce6d8e34324e497a7292754e7f5d2daf2f
f4fc9652f23d7e157e9d55eafe3a98cb046ee27f6e8f494cfe2bf3cb595b6e25
1adb0707719432627a3df01b0c3d878c5e6818bd161c3b6a11ca887831cfeb3b
74ae9027e48f7a82ec6597cf2e4437019285c7367b66c5d0ed5e34ff6c7e293e
```

Decode through the locked OpenShot/FFmpeg reader to canonical BGRA and interleaved `s16le`; assert the 60 individual frame hashes, both aggregate hashes, counts, formulas, input/output PTS rules, dimensions, formats, stream count, codec IDs, time bases, frame rate, sample rate, channel layout, and exact no-padding rule. Two independent exports must produce identical semantic hashes and normalized stream metadata.

Container byte equality, muxer writing-library strings, file timestamps, cluster offsets, packet partitioning, and other container-level volatile metadata are explicitly ignored. CI stores the manifest/reference generator in test source and stores the produced file/report on failure. The generator and manifest may change only through an explicitly reviewed oracle-version change; output from the implementation under test can never update or bless them.

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
| G3 Qt ABI/provenance | libopenshot + app owners | Exact plugin/DLL inventory, paths/hashes/version, four-stage load logs, and no-fallback report | QWidget test/package |
| G4 audio build | audio owner | Native CTest and PR A contract | PR B |
| G5 library/binding | libopenshot owner | CTest, import, QWidget, feature smokes | PR B artifact |
| G6 native golden | libopenshot owner | Semantic render report | PR C |
| G7 cx_Freeze | app owner | Arm64 base build/freeze/hook/startup evidence | Package creation |
| G8 source/frozen startup | app owner | Ready marker and exact platform/image/icon/media/native-module reports | Installers |
| G9 packaged golden | app owner | Frozen semantic hashes and negative cases | Signing |
| G10 package metadata | packaging owner | Inno/MSIX manifests, PE closure, identities | Signing |
| G11 installed smoke | packaging owner | Separate Inno/MSIX native launch, exact plugin probes, render, and uninstall reports | Prerelease |
| G12 migration/signing | release maintainer | Signature and failure/migration reports | Prerelease/stable |
| G13 hardware | Hardware QA | Completed two-device matrix and logs | Stable release |

No-go conditions are: baseline versions/SO values disagree; a package or producer digest is mutable/missing; Python, SWIG extension, or any bundled module is not ARM64; a required Qt plugin is absent, warns, loads outside its stage root, or has wrong/duplicate provenance; more than one Qt runtime appears; QWidget interop fails; a required current feature was silently disabled; dependency closure or license inventory is incomplete; source, frozen, either installed stage, or golden tests fail; package identity cannot safely upgrade x64; signing or uninstall cleanup fails; or G13 mandatory rows lack evidence.

The MSVC/official-Qt stack is the only architectural fallback. It requires a new contract revision rebuilding CPython-extension/native dependencies consistently against MSVC and the exact Qt distribution used by the selected binding; it may not be mixed into this lane. PySide6, cross-compilation, and x64 emulation are not automatic fallbacks.

## Scope and open assumptions

In scope are the locked native dependency assembly, production GitLab lanes, optional matching GitHub presubmits, artifact contracts, SWIG/Qt proof, source/frozen/installed semantic rendering, Inno/MSIX/signing/migration, release naming, and physical hardware protocol.

Out of scope are repository consolidation, Qt selector redesign, Qt source rebuilding without a separately approved contract, unrelated FFmpeg/OpenCV feature work, macOS/Linux Arm, ASIO certification, and unsupported performance promises.

Open runtime assumptions are deliberately gated:

- MSYS2 CPython 3.14 and cx_Freeze 8.7 can produce a working native Arm64 base executable: G7, owned by openshot-qt.
- OpenCV 5.0.0 and Protobuf 35.1 satisfy the selected post-4.0 libopenshot source while preserving all enabled algorithms: G5, owned by libopenshot.
- The production GitLab environment can be provisioned as native CLANGARM64 and the signing/MSIX tools accept the candidate: G1/G12, owned by release infrastructure/maintainers.
- The locked FFmpeg build exposes required software codecs/devices and valid Windows Arm behavior: G5/G9/G13, owned by libopenshot and hardware QA.
- The locked Qt FFmpeg media plugin loads and decodes the fixed WAV probe at all four stages without an external backend: G3/G8/G11, owned by openshot-qt packaging.
- Inno/MSIX retain a recoverable x64-to-Arm64 upgrade under the selected production identities: G12, owned by the packaging/release maintainer.

confidence: high

The design is freeze-ready because the accepted ABI, production flow, BOM, packaging, baseline, hardware matrix, and gates remain intact while exact four-stage Qt plugin probes and an independently fixed, byte-exact golden oracle close the final two findings without implementation invention.
