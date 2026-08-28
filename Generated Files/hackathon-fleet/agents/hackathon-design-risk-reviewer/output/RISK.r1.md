# RISK r1 independent review

verdict: REVISE

The Windows Arm64 direction is feasible, but the proposed design is not implementation-ready. It does not select one ABI-compatible Python/Qt/C++ toolchain, omits the production native-library CI definitions, leaves the required dependency closure unowned, and does not define acceptance evidence capable of proving that the packaged process is native Arm64 and operational.

## RISK-001 - No coherent Python/Qt/C++ ABI contract

- severity: critical
- location/evidence: `Generated Files\design-spec.md:28-35,39-41,45-47`; `OpenShot\.gitlab-ci.yml:120-144`; `OpenShot\freeze.py:357-388`; `libopenshot\.gitlab-ci.yml:94-118`; `libopenshot-audio\.gitlab-ci.yml:60-77`; `libopenshot\bindings\python\openshot.i:140-202,252-258`.
- observed: The design aligns only the Qt *major*. The shipping Windows stack is one MinGW64 ecosystem (`MSYSTEM=MINGW64`, `MinGW Makefiles`, MSYS2 Python/PyQt paths), while current native Windows Arm Qt is available through materially different distributions. Qt's supported-platform table identifies Windows ARM64 with MSVC 2022 ([Qt for Windows - Building from Source](https://doc.qt.io/qt-6/windows-building.html); retrieved 2026-08-27). MSYS2 has CLANGARM64 packages, while PyPI's current `PyQt6` and `PyQt6-Qt6` Arm64 wheels bundle their own Windows Qt runtime. Passing a `QWidget *` extracted by sip/shiboken into `libopenshot` makes exact Qt runtime/compiler compatibility a correctness requirement, not merely a Qt5/Qt6 choice.
- expected: One explicit end-to-end contract must identify CPython version and architecture, compiler/CRT, Qt distribution and exact version, binding and binding runtime, SWIG extension ABI, and the compiler/runtime used for every linked native library. The process must load one compatible Qt runtime.
- reproduction/source evidence: `Select-String` over the three `.gitlab-ci.yml` files shows `C:\msys64\mingw64`, `MSYSTEM=MINGW64`, and `-G "MinGW Makefiles"`; `Invoke-RestMethod https://pypi.org/pypi/PyQt6/6.11.0/json` returns `pyqt6-6.11.0-cp310-abi3-win_arm64.whl`, and `https://pypi.org/pypi/PyQt6-Qt6/json` returns `pyqt6_qt6-6.11.2-py3-none-win_arm64.whl`; [MSYS2 environments](https://www.msys2.org/docs/environments/) documents CLANGARM64 separately from MINGW64.
- required design correction: Choose and document either an all-compatible MSVC stack (including the exact Qt SDK matching the selected binding runtime) or an all-compatible CLANGARM64/MSYS2 stack (including how the Python Qt binding is built/obtained against that Qt). Pin versions, prohibit auto-fallback to an ABI-incompatible binding in packaged builds, and add DLL provenance/architecture checks before QWidget interop is exercised.

## RISK-002 - Production CI owners are omitted and the proposed landing order is dependency-inverted

- severity: high
- location/evidence: `Generated Files\files-to-update.md:18-32`; `Generated Files\design-spec.md:72-78`; `OpenShot\.gitlab-ci.yml:120-123,205-232`; `libopenshot\.gitlab-ci.yml:94-118`; `libopenshot-audio\.gitlab-ci.yml:60-77`.
- observed: The file map assigns Arm work in both native repositories to GitHub Actions, but OpenShot consumes artifacts named `windows-builder-x64` from each repository's GitLab pipeline. Both native repositories' `.gitlab-ci.yml` files contain the actual MinGW/x64 build and `install-x64` artifact contracts, yet neither is listed for its PR. The recommended order starts packaging before either Arm64 native artifact exists, although the packaging job downloads `libopenshot`, which in turn downloads `libopenshot-audio`.
- expected: The plan must cover the production artifact chain and land/build from the bottom up: audio library, libopenshot/SWIG, then openshot-qt freeze/installer. GitHub Actions may be an additional presubmit gate but is not a substitute for the release-producing GitLab jobs.
- reproduction/source evidence: `Select-String -Path libopenshot\.gitlab-ci.yml -Pattern 'windows-builder|mingw64|install-x64'` identifies lines 94-118; the same command on `libopenshot-audio\.gitlab-ci.yml` identifies lines 60-77; `OpenShot\.gitlab-ci.yml:120-123` downloads the former job by name.
- required design correction: Add both native repositories' `.gitlab-ci.yml` files and builder provisioning/configuration to the file/ownership map. Define versioned Arm64 artifact names and compatibility metadata, then reverse the landing/validation order so each consumer is tested against an available producer artifact before packaging.

## RISK-003 - The native dependency closure is not a plan

- severity: high
- location/evidence: `Generated Files\design-spec.md:37-47`; `libopenshot\src\CMakeLists.txt:224-230,421-510,542-579`; `OpenShot\freeze.py:373-443`.
- observed: “Only widen the supported architecture” accounts for neither acquisition nor ABI compatibility of FFmpeg (`avcodec`, `avdevice`, `avformat`, `avutil`, `swscale`, resampler), OpenMP, ZeroMQ/cppzmq, OpenCV, Protobuf, optional ImageMagick/babl, Qt, and OpenShotAudio. The freezer additionally harvests MSYS2 babl/image-format/OpenCV DLLs from architecture-specific directories. Current PyPI queries show native Arm64 wheels for PyQt6/PySide6, NumPy, and pyzmq, but no current `opencv-python` or `cx-Freeze` win_arm64 wheel. OpenCV's request remains open: [opencv-python#806](https://github.com/opencv/opencv-python/issues/806), with a 2026-07-03 report that OpenCV 5 source builds fail on missing Windows Arm FFmpeg. cx_Freeze labels Windows Arm support experimental in merged [cx_Freeze#2943](https://github.com/marcelotduarte/cx_Freeze/pull/2943).
- expected: Every required native input must have a pinned producer, target triplet, license/configuration, artifact checksum/provenance, and smoke test. Optional features must have an explicit ship/disable decision and corresponding UI/profile behavior.
- reproduction/source evidence: On 2026-08-27, `Invoke-RestMethod https://pypi.org/pypi/<package>/json` found no `win_arm64` artifact in current `opencv-python 5.0.0.93` or `cx-Freeze 8.7.0`; MSYS2 package pages for `mingw-w64-clang-aarch64-{ffmpeg,opencv,qt6-base,protobuf,zeromq}` all returned HTTP 200, demonstrating one possible ecosystem but not compatibility with the unselected Python/Qt stack.
- required design correction: Add a dependency bill of materials and choose one source for each dependency under the RISK-001 ABI contract. Include FFmpeg configure options/codecs/devices, OpenCV+Protobuf feature policy, OpenMP runtime, ZeroMQ, babl/ImageMagick, cx_Freeze source-build support, redistribution licenses, and automated PE-machine/import-closure validation.

## RISK-004 - The proposed CI gate cannot prove a native packaged application

- severity: high
- location/evidence: `Generated Files\design-spec.md:56-70`; `Generated Files\files-to-update.md:14-16`; `OpenShot\.gitlab-ci.yml:134-144`; `OpenShot\src\tests\test_export_clips.py:33-104`; `OpenShot\src\windows\export.py:1176-1309`.
- observed: The current Windows job runs `launch.py -V` and freezes but does not run the source test suite or launch the frozen GUI. Existing export tests use dummy writers and do not encode media. A golden FFmpegWriter render can validate part of libopenshot, but by itself cannot detect x64 emulation, wrong-machine `_openshot.pyd`/DLLs, duplicate Qt runtimes, missing Qt plugins, freezer failures, or a package that installs but does not start.
- expected: Acceptance must separately prove source/native integration, frozen application startup, and installed artifacts, all as Arm64 processes with Arm64 dependency closure.
- reproduction/source evidence: `OpenShot\.gitlab-ci.yml:134-144` contains no test discovery or packaged launch; `test_export_clips.py:86-103` supplies lambda mocks for writer methods; the real writer loop is only in `export.py:1176-1309`.
- required design correction: Add gates for PE `Machine=ARM64` on the launcher, `_openshot.pyd`, and every bundled DLL; native `import openshot`; binding creation plus QWidget pointer interop; offscreen frozen-app launch; Qt image/plugin loading; deterministic software encode/decode; installer and MSIX install-launch-uninstall; and a check that no x64 process/module is used. Run these before hardware performance tests.

## RISK-005 - Golden determinism is underspecified and may reject valid FFmpeg outputs

- severity: high
- location/evidence: `Generated Files\design-spec.md:56-64`; `OpenShot\src\windows\export.py:1180-1238`; `libopenshot\src\CMakeLists.txt:421-487`.
- observed: “Repeat-run determinism” does not define whether equality means container bytes, decoded frames, audio PCM, stream metadata, or tolerances. Container timestamps, encoder versions/threading, and codec metadata can change bytes without changing media. Conversely, checking only frame count/duration/codec can miss pixel or sample corruption. The export UI exposes multiple codec and hardware branches, while the proposal names one unspecified golden path.
- expected: A reproducible oracle must distinguish semantic media correctness from byte reproducibility and pin the encoder/settings used by CI.
- reproduction/source evidence: `export.py:1180-1201` selects codecs dynamically and `:1213-1238` applies codec/muxer options; FFmpeg libraries are externally supplied by `libopenshot\src\CMakeLists.txt:423-457`, so output details vary with the selected build.
- required design correction: Define a tiny synthetic timeline with no external nondeterministic assets; pin a software codec, pixel/sample formats, thread count and metadata policy; assert decoded per-frame hashes and PCM hashes plus exact counts/timestamps; normalize or explicitly ignore container-volatile fields. Add negative tests for unavailable codec, failed writer open/write/close, and cancellation.

## RISK-006 - Installer architecture, upgrade, signing, and coexistence failure paths lack acceptance criteria

- severity: high
- location/evidence: `Generated Files\design-spec.md:49-54,66-70`; `OpenShot\installer\windows-installer.iss:23-53,135-158`; `OpenShot\installer\package_msix.ps1:178-208,270-355`; `OpenShot\installer\build_server.py:575-598,640-685`.
- observed: The design proposes generated architecture values but does not specify valid mappings or verify the generated package identity/payload. The MSIX script validates source-installer absence, not manifest architecture or PE architecture. The Inno installer reuses one AppId/default directory and machine-wide file associations/firewall rule; no test covers upgrading an emulated x64 install to Arm64, downgrade, side-by-side behavior, rollback, uninstall cleanup, or signed-uninstaller/MSIX publisher failures.
- expected: Architecture mappings and migration policy must be explicit, and both package formats must be inspected and exercised on Windows Arm64, including failures.
- reproduction/source evidence: [Inno Setup architecture identifiers](https://jrsoftware.org/ishelp/topic_archidentifiers.htm) defines `arm64` separately from `x64compatible`; Microsoft package identity permits `arm64` ([Package identity overview](https://learn.microsoft.com/en-us/windows/apps/desktop/modernize/package-identity-overview)). `package_msix.ps1:277-280` still selects `OpenShot-*-x86_64.exe` and contains no architecture assertion.
- required design correction: Specify filename/folder/Inno/manifest/MSIX architecture mappings, package identity and AppId policy, x64-to-Arm64 upgrade behavior, and signing tool compatibility. Require manifest inspection, signature verification, clean install, upgrade, rollback/failure, launch, file association, firewall cleanup, and uninstall tests on physical Arm64 Windows.

## RISK-007 - Current upstream release and issue state is not incorporated

- severity: medium
- location/evidence: `Generated Files\appendix-references.md:13-23`; [openshot-qt#5853](https://github.com/OpenShot/openshot-qt/issues/5853); [openshot-qt#6075](https://github.com/OpenShot/openshot-qt/pull/6075); [libopenshot#1082](https://github.com/OpenShot/libopenshot/pull/1082); [libopenshot-audio#170](https://github.com/OpenShot/libopenshot-audio/pull/170).
- observed: No existing OpenShot Arm implementation PR was found, and issue #5853 remains open, so the work is not already solved. However, the design targets the current develop versions without acknowledging the coordinated open OpenShot 4.0/libopenshot 1.0/libopenshot-audio 1.0 release PRs. Those PRs change minimum library versions and libopenshot SO version and were still active on 2026-08-27.
- expected: The plan must state its target release baseline and rebase/compatibility policy so the three PRs do not produce artifacts against superseded ABI/version contracts.
- reproduction/source evidence: `gh issue view 5853 --repo OpenShot/openshot-qt` returned OPEN; `gh pr view` returned OPEN for #6075, #1082, and #170, all from `release-20260725` into `develop`. Latest published releases queried through `gh api` were openshot-qt v3.5.1, libopenshot v0.7.0, and libopenshot-audio v0.6.0.
- required design correction: Coordinate with issue #5853, choose either the current release branch or post-merge develop as the baseline, pin cross-repository versions/SO expectations in artifact metadata, and re-run dependency and packaging evidence after that baseline is selected.

## RISK-008 - Windows Arm hardware behavior coverage is too narrow

- severity: medium
- location/evidence: `Generated Files\design-spec.md:66-70`; `OpenShot\src\windows\export.py:514-531,696-716`; `libopenshot-audio\CMakeLists.txt:152-230`.
- observed: Physical validation covers install and export performance only. It does not require preview/playback, audio output/input device enumeration, WASAPI behavior, unavailable hardware encoder fallback, suspend/resume, long-path/non-ASCII projects, low-memory handling, or crash-free repeated launch/export. The export UI probes VAAPI/NVENC/DXVA2/VideoToolbox/QSV but has no Windows Arm codec/fallback matrix.
- expected: Hardware acceptance must cover the user-visible native stack and failure paths, not only a successful benchmark.
- reproduction/source evidence: `export.py:514-531` enumerates hardware codec families and `:696-716` performs audio codec fallback; `libopenshot-audio\CMakeLists.txt:152-230` builds JUCE audio-device modules and Windows system links. None appears in the proposed hardware checklist.
- required design correction: Add a physical-device matrix covering GUI preview, timeline playback, audio output and recording, software export, available/unavailable hardware codec behavior, sleep/resume, repeat runs, representative file paths, install/upgrade/uninstall, logs, and explicit pass/fail thresholds. Record CPU architecture/process/module evidence alongside performance numbers.

confidence: high
The findings are based on the specified clones and generated artifacts, exact release-build source lines, current GitHub issues/PRs/releases, and live upstream package/support data collected on 2026-08-27.