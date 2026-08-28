# DESIGN r1 — Windows Arm64 native stack

investigated_at: 2026-08-27T14:35:29Z

## Decision

Implement Windows Arm64 as a third, native architecture lane across the three existing repositories, using one coherent MSYS2 `CLANGARM64`/Qt 6/PyQt6 dependency prefix. Keep PR ownership separate and merge in dependency order: `libopenshot-audio`, `libopenshot`, then `openshot-qt`. Do not redesign `qt_api`, combine repositories, use x64 emulation as acceptance evidence, or call the platform/vendor stack blocked.

This is the smallest credible architecture because native Arm64 packages are currently published for CPython, PyQt6/Qt6, FFmpeg, and OpenCV, and GitHub publishes Arm64 Windows runner labels. The unimplemented work is OpenShot's architecture lane, artifact contract, and validation. Evidence: HTTP 200 responses on 2026-08-27 for [MSYS2 Python](https://packages.msys2.org/package/mingw-w64-clang-aarch64-python), [PyQt6](https://packages.msys2.org/package/mingw-w64-clang-aarch64-python-pyqt6), [Qt6 base](https://packages.msys2.org/package/mingw-w64-clang-aarch64-qt6-base), [FFmpeg](https://packages.msys2.org/package/mingw-w64-clang-aarch64-ffmpeg), and [OpenCV](https://packages.msys2.org/package/mingw-w64-clang-aarch64-opencv); PyPI JSON lists `win_arm64` wheels for PySide6 6.11.2 and PyQt6 6.11.0; Python's Windows download page lists native Arm64 installers; GitHub's hosted-runner reference lists `windows-11-arm` and `windows-11-vs2026-arm`.

## Current-state evidence

- The investigated commits are `openshot-qt` `9cd2b3f3ee9024c3496487a2de30a402515ed659`, `libopenshot` `eac81cf91555438c54fbadef7fdd05bf803f26ee`, and `libopenshot-audio` `48516e0b64b9f3ddf2ab79975a42ba2f37023703`, all on `develop` (`git branch --show-current; git log -1 --format=%H` in each clone).
- Latest releases are [openshot-qt v3.5.1](https://github.com/OpenShot/openshot-qt/releases/tag/v3.5.1), [libopenshot v0.7.0](https://github.com/OpenShot/libopenshot/releases/tag/v0.7.0), and [libopenshot-audio v0.6.0](https://github.com/OpenShot/libopenshot-audio/releases/tag/v0.6.0) (`gh api repos/OpenShot/<repo>/releases/latest`). The v3.5.1 assets contain Windows `x86.exe` and `x86_64.exe`, but no Arm64 artifact.
- Windows Arm64 is still requested by open issue [openshot-qt#5853](https://github.com/OpenShot/openshot-qt/issues/5853). Older requests [#5094](https://github.com/OpenShot/openshot-qt/issues/5094) and [#5227](https://github.com/OpenShot/openshot-qt/issues/5227) were closed by inactivity, not by a shipped native build.
- The UI already selects `pyqt6`, `pyside6`, or `pyqt5` via `OPENSHOT_QT_API`; auto mode tries them in that order (`src\qt_api.py:2284-2289,2411-2486`). Documentation already requires Qt-major alignment (`README.md:96-105`; `doc\developers.rst:112-116`). This part is already solved.
- `libopenshot` already selects Qt 6 or Qt 5 through `USE_QT6=AUTO|ON|OFF` (`libopenshot\src\CMakeLists.txt:358-398`), builds `_openshot` through SWIG (`bindings\python\CMakeLists.txt:11-32,91-106,108-140`), and supports sip/shiboken QWidget pointer extraction without narrowing the pointer (`bindings\python\openshot.i:140-202,252-266`). History also contains Arm64 pointer fixes `c7b36d92` and `0c10dc516` (`git log --all -i --grep='arm64\|aarch64'`). Do not duplicate that work.
- The actual Windows build graph is only MinGW x64/x86. `libopenshot-audio\.gitlab-ci.yml:60-103` uses `MINGW64`/`MINGW32` and `install-x64`/`install-x86`; `libopenshot\.gitlab-ci.yml:94-153` consumes those exact jobs and prefixes; `openshot-qt\.gitlab-ci.yml:106-257` consumes `windows-builder-x64/x86`, patches only `amd64`/`x86`, and signs only `*-x86_64.exe`/`*-x86.exe`.
- GitHub CI is not an Arm64 fallback: all three matrices are Ubuntu-only (`openshot-qt\.github\workflows\ci.yml:4-29`; `libopenshot\.github\workflows\ci.yml:9-25`; `libopenshot-audio\.github\workflows\ci.yml:4-20`). Their latest `develop` runs were green, but therefore prove Linux behavior only: [openshot-qt run 29976537220](https://github.com/OpenShot/openshot-qt/actions/runs/29976537220), [libopenshot run 29952077875](https://github.com/OpenShot/libopenshot/actions/runs/29952077875), and [audio run 23364446188](https://github.com/OpenShot/libopenshot-audio/actions/runs/23364446188).
- Packaging independently excludes Arm64: `freeze.py:142-153` discovers only `install-x64/x86`; `installer\windows-installer.iss:7-41` defaults architecture to `x64`; `installer\package_msix.ps1:178-208,270-280,379-382` locates and renames from an `x86_64` installer; `installer\build_server.py:575-598,640-685,938-947` describes x64 signing, locates x64/x86 prefixes, and emits x86/x86_64 names; `installer\deploy.py:45-46,94-102,153-161` parses x86 names and reads `install-x64`.
- The user-visible render path is native: it constructs `openshot.FFmpegWriter`, configures streams, writes `timeline.GetFrame(frame)`, and closes the writer (`src\windows\export.py:1176-1242,1255-1309`). Current app tests only mock export helpers (`src\tests\test_export_clips.py:74-104`); native writer tests exist in `libopenshot\tests\FFmpegWriter.cpp:46-132`.
- Local execution cannot reproduce native Arm64: `PROCESSOR_ARCHITECTURE`, .NET OS/process architecture, and Python `platform.machine()` all returned AMD64/X64; Python 3.12.10 is an MSC AMD64 build. Therefore this record source-proves the absent lane but does not claim a successful Arm64 build, import, install, render, or performance result.

## Root cause

There is no demonstrated Arm-specific UI defect. The root cause is an architecture value that is implicit and duplicated across the release graph:

1. Audio CI produces only `windows-builder-x64/x86`.
2. Library CI requests those names, binds to `mingw64/mingw32`, and publishes only `install-x64/x86`.
3. Application CI requests the x64/x86 library job, binds to the same prefixes, and hardcodes manifest, installer, MSIX, signing, upload, and release names.
4. No native lane executes the SWIG/Qt/FFmpeg boundary or a real export.

Thus an Arm64 artifact cannot enter the graph even though core upstream packages exist. Remaining uncertainty is dependency-version compatibility and packaging behavior, not basic vendor availability.

## Recursive dependency graph and control boundary

```text
OpenShot Arm64 installer/MSIX                         [openshot-qt]
├─ frozen native Arm64 CPython application           [openshot-qt + upstream runtime]
│  ├─ OPENSHOT_QT_API=pyqt6                          [already implemented]
│  │  └─ MSYS2 CLANGARM64 PyQt6 + matching Qt6       [upstream packages]
│  ├─ cx_Freeze and Python dependencies              [upstream; compatibility gate]
│  └─ openshot.py + _openshot.pyd                    [libopenshot]
│     ├─ Arm64 libopenshot DLL                       [libopenshot]
│     │  ├─ same Qt6 DLL family as PyQt6             [upstream; must not mix Qt builds]
│     │  ├─ FFmpeg libraries/codecs                  [upstream package]
│     │  ├─ OpenCV                                   [upstream package; exact version gate]
│     │  ├─ protobuf/ZeroMQ/jsoncpp/babl/etc.        [upstream; closure gate]
│     │  └─ Arm64 libopenshot-audio DLL              [libopenshot-audio]
│     │     ├─ bundled JUCE modules                  [repository source]
│     │     ├─ optional ASIO SDK                     [vendor/optional]
│     │     └─ winmm/ws2_32/wininet/version/Shlwapi  [Windows SDK]
│     └─ SWIG + matching Arm64 Python import library [upstream toolchain]
├─ Inno Setup/MSIX architecture metadata             [openshot-qt/tool vendors]
└─ signing certificate, publishing, hardware QA      [maintainers/hardware owner]
```

`libopenshot-audio\CMakeLists.txt:152-167,183-230` shows the JUCE target and Windows system links. The MSYS2 package pages prove several major nodes, not the complete closure; every produced PE file must therefore be machine-checked before claiming closure.

## Proposed changes by repository

### PR A — `libopenshot-audio`

- Add a `windows-builder-arm64` job to `.gitlab-ci.yml` using `C:\msys64\clangarm64`, `MSYSTEM=CLANGARM64`, and `build\install-arm64`; preserve the current x64/x86 jobs.
- Add `windows-11-arm` to `.github\workflows\ci.yml` as independent native compile/install evidence, with CLANGARM64 package names instead of the currently dormant x86_64 package list.
- Leave `CMakeLists.txt` and JUCE source unchanged unless the native compile identifies a concrete failure. Its `WIN32` branch has no x86-size assumption in the inspected code (`CMakeLists.txt:211-230`).
- Publish `libopenshot-audio.env`, the DLL/import library, and a machine-header inventory from `llvm-readobj --file-headers`.

### PR B — `libopenshot`

- Add `windows-builder-arm64` to `.gitlab-ci.yml`, consuming only PR A's `windows-builder-arm64` artifact and using `install-arm64`, `clangarm64`, `OpenShotAudio_ROOT`, and an Arm64 OpenCV prefix.
- Add a native Arm64 job to `.github\workflows\ci.yml`; remove neither Linux coverage nor existing GitLab lanes.
- Configure `-DUSE_QT6=ON`, `-DPYTHON_MODULE_PATH=python`, and the same CLANGARM64 Python/PyQt6/Qt6 prefix. Keep `bindings\python\openshot.i` unchanged unless the QWidget smoke test demonstrates a regression. Do not mix PyPI-bundled Qt DLLs with an unrelated MSYS2 Qt build.
- Change `bindings\python\CMakeLists.txt` only if configure evidence shows its legacy `FindPythonInterp/FindPythonLibs` selects a non-Arm interpreter or library; the required correction would be a targeted `FindPython3` interpreter/development-module pairing, not architecture casts.
- Extend `tests\FFmpegWriter.cpp` (and reuse timeline helpers in `tests\Timeline.cpp`) with a small synthetic audio/video render whose decoded properties are stable across architectures.

### PR C — `openshot-qt`

- Introduce one canonical architecture mapping in `.gitlab-ci.yml`: lane `arm64`, dependency job `windows-builder-arm64`, prefix `install-arm64`, MSYS environment/prefix `CLANGARM64`/`clangarm64`, manifest processor `arm64`, release suffix `arm64`, and Inno architecture `arm64`.
- Thread that value through `freeze.py` artifact discovery and OpenCV DLL closure; `installer\windows-installer.iss` architecture defines; `installer\package_msix.ps1` installer discovery, source-installer exclusion, and output name; `installer\build_server.py` artifact discovery/name/signing; and `installer\deploy.py` release regex/share paths. Preserve existing x64/x86 defaults for rollback.
- Add `src\tests\test_export_golden.py` as an integration test requiring the native `openshot` module. Build a tiny synthetic timeline, execute the same `FFmpegWriter`/`GetFrame`/`WriteFrame`/`Close` sequence anchored at `src\windows\export.py:1176-1309`, then inspect the output through `openshot.FFmpegReader`.
- Do not change `src\qt_api.py`; set `OPENSHOT_QT_API=pyqt6` in the Arm lane and assert the selected binding/version in logs.

## Alternatives

| Alternative | Tradeoff | Decision |
| --- | --- | --- |
| Coherent MSYS2 CLANGARM64 Python + PyQt6 + Qt6 + native libraries | Closest extension of current MinGW packaging and major packages exist; full package/version closure still needs a CI spike. | Chosen. |
| Official CPython/PyQt6 wheels plus MSVC/vcpkg-built native stack | Strong Microsoft ABI/tooling story, but replaces the established MSYS2 dependency and packaging path and risks loading two different Qt distributions. | Fallback only if CLANGARM64 fails with captured evidence. |
| PySide6 | Native wheel exists and selector/interop already support it, but changes the binding while changing architecture and does not remove the matching-Qt requirement. | Keep as contingency after PyQt6 lane. |
| Cross-compile on x64 | Useful for compile coverage, but cannot validate import, Qt loading, render, install, or device behavior. | Supplemental only. |
| Ship x64 under Windows Arm emulation | Lowest engineering cost but is not native Arm64 and cannot satisfy the objective or performance claims. | No-go. |

## Implementation and ownership sequence

1. Open a tracking comment on [#5853](https://github.com/OpenShot/openshot-qt/issues/5853) linking three separately owned draft PRs and the chosen dependency versions.
2. Run a non-release CLANGARM64 dependency spike. Record package versions and machine headers. Stop if any required runtime has no Arm64 build; decide package substitution or source build explicitly rather than silently mixing architectures.
3. Land PR A and retain its immutable Arm64 artifact/SHA.
4. Rebase PR B onto current `develop`, consume PR A's exact artifact, and land only after native CTest, `_openshot.pyd` import, and QWidget interoperability pass.
5. Rebase PR C, consume PR B's exact artifact, then run freeze, installer, MSIX, launch, and golden export.
6. Maintainers sign and publish a prerelease candidate. A hardware owner performs clean install/uninstall and performance runs on physical Windows Arm64.

Coordinate target branches before implementation: active release PRs [openshot-qt#6075](https://github.com/OpenShot/openshot-qt/pull/6075), [libopenshot#1082](https://github.com/OpenShot/libopenshot/pull/1082), and [libopenshot-audio#170](https://github.com/OpenShot/libopenshot-audio/pull/170) change the three-repository version contract. The Windows bootstrap PR [openshot-qt#6002](https://github.com/OpenShot/openshot-qt/pull/6002) is source-build setup, touches only a new helper tree, and explicitly disclaims release packaging; coordinate package names but do not duplicate or absorb it. None of the open PR lists returned by `gh pr list --state open` implements Windows Arm64 release lanes.

## Test, migration, rollback, and acceptance design

### Automated gates

1. **Architecture purity:** `llvm-readobj --file-headers` reports AArch64 for every project-produced `.exe`, `.dll`, and `.pyd`; dependency scanning finds no x86/x64 DLL in the frozen directory.
2. **Native import:** native Arm64 Python prints `platform.machine() == "ARM64"`, imports `openshot`, imports the selected PyQt6 modules, and constructs/destroys the libopenshot QWidget-facing object without pointer truncation.
3. **Library tests:** PR A compiles/installs on native Arm64; PR B runs CTest including `FFmpegWriter` and the synthetic render. No `|| true` is allowed on the Arm acceptance job (the existing GitHub workflow masks coverage failure at `libopenshot\.github\workflows\ci.yml:130-135`).
4. **Golden render:** two independent 2-second, 30-fps, 48-kHz stereo exports each decode to exactly 60 video frames and 96,000 samples per channel (or a documented codec-padding bound); width, height, fps, channel count, sample rate, and codecs match. Compare decoded per-frame hashes and normalized PCM hashes, not container bytes or wall-clock metadata.
5. **Package smoke:** frozen app launches natively; Inno and MSIX metadata report Arm64; file names end in `-arm64`; clean install, launch, sample export, uninstall, and absence of stale install files pass.
6. **Regression:** unchanged x64 and x86 jobs retain their prior names, prefixes, installer suffixes, tests, and signing behavior.

### Maintainer/hardware gates

- Signing credentials, production MSIX identity, upload, release notes, and final publication remain maintainer-controlled.
- Native CI can establish compatibility, but performance acceptance requires physical Arm64 Windows hardware. Record device/SoC, RAM, Windows build, power mode, artifact SHA, source media, codec settings, three cold exports, three repeat exports, elapsed time, and failures. Make no performance claim from this AMD64 host, emulation, or hosted CI alone.
- Optional ASIO hardware/SDK behavior is a vendor/hardware gate; WASAPI/default-output functionality is the release baseline. Absence of ASIO must not be mislabeled as absence of Windows Arm support (`libopenshot-audio\CMakeLists.txt:211-218` makes ASIO optional).

### Migration and rollback

The Arm64 lane is additive. Use architecture-specific job names, artifact prefixes, caches, installer names, and release assets so it cannot overwrite x64/x86 output. Rollback consists of disabling the Arm64 release/sign jobs and withdrawing only the Arm64 prerelease asset; no project format, user data, API, or existing artifact changes are required. Keep failed Arm jobs available as non-blocking experimental jobs only during the dependency spike; promotion to release must make all six automated gates blocking.

## Scope and no-go gates

- In scope: native dependency assembly, three CI lanes, architecture-safe artifact flow, SWIG import proof, deterministic render proof, installer/MSIX/signing integration, and hardware validation protocol.
- Out of scope: Qt source rebuild without package evidence, repository consolidation, unrelated Qt-selector refactoring, unrelated FFmpeg feature PRs, macOS/Linux Arm work, and performance promises.
- Do not merge if any binary is not AArch64, Python and `_openshot.pyd` use different ABIs, PyQt6 and libopenshot load incompatible Qt builds, the dependency inventory is incomplete, native import/render fails, or the new variables alter existing x64/x86 artifacts.
- Do not publish a stable Arm64 asset until signing, clean install/uninstall, and physical-device export pass. Lack of maintainer credentials or hardware blocks release evidence, not implementation or CI.

## Open assumptions and risks

- The inspected MSYS2 pages establish package existence, not that the current OpenShot-pinned combination (notably OpenCV 4.13 paths in `libopenshot\.gitlab-ci.yml:104-110` and `openshot-qt\.gitlab-ci.yml:125-133`) resolves unchanged. Pin and archive the successful manifest.
- `cx-Freeze` 8.7.0 publishes a `py3-none-any` wheel and source archive, while app GitHub CI pins 7.0.0 (`openshot-qt\.github\workflows\ci.yml:23-24`); neither fact proves its generated base executable and hooks work under CLANGARM64. Freeze is an explicit spike gate.
- The self-hosted GitLab `windows` runner's CPU and installed CLANGARM64 environment are not visible from repository source. GitHub Arm runners can prove native builds; maintainers must provision/label the production signing path.
- Inno Setup and the Microsoft MSIX Packaging Tool are architecture metadata/package gates that require an actual candidate; source inspection alone cannot prove their end-to-end Arm64 output.
- Active 4.0/1.0 release PRs may change dependency versions before implementation. Rebase and regenerate evidence rather than coding against v3.5.1 paths blindly.

confidence: medium

The source and upstream inventories establish the missing architecture flow and a viable native toolchain, but no Arm64 build, package, render, or physical-hardware run was possible on the available AMD64 host.
