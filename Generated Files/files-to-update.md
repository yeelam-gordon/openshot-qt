# Exact change surface and ownership

Implementation is split into three upstream PRs and lands in dependency order A, B, C. PRs may be developed concurrently, but no consumer merges until its producer artifact and contract are accepted. Existing x64/x86 lanes and separate repository ownership remain intact.

## PR A - `OpenShot/libopenshot-audio`

| File/symbol | Required change |
| --- | --- |
| `.gitlab-ci.yml` | Add production `windows-builder-arm64`; install the exact lock under CLANGARM64/Ninja, run CTest and PE/import scans, emit contract/SBOM/reports, publish an immutable versioned artifact, and trigger libopenshot only after success. |
| `.github\workflows\ci.yml` | Optionally add a native Arm presubmit using the same lock; never use its output as a release artifact. |
| `ci\windows-arm64-packages.lock` and validation scripts | Add the shared checksummed package/provenance lock and reusable architecture/import validator. |
| `CMakeLists.txt:61-230` | No planned product change. Change only for a reproduced Arm compile/device defect; preserve the JUCE module graph, required WASAPI, and optional/excluded-baseline ASIO semantics. |
| Tests | Add or extend device-independent audio buffer/resampling tests if absent; physical device behavior remains G13. |

Artifact: `libopenshot-audio-1.0.0-so10-windows-arm64-<sha>.zip`, with install tree under `install-arm64`.

## PR B - `OpenShot/libopenshot`

| File/symbol | Required change |
| --- | --- |
| `.gitlab-ci.yml` | Add production `windows-builder-arm64`; consume PR A by exact contract and digest, configure locked dependencies, run all CTest/integration gates, and publish the immutable versioned artifact. |
| `.github\workflows\ci.yml` | Optionally add a same-lock native Arm presubmit. |
| `ci\windows-arm64-packages.lock` and validation scripts | Use the same lock digest and artifact/architecture validator as PR A. |
| `bindings\python\CMakeLists.txt:23-35,91-106` | Replace legacy unpaired Python discovery with `FindPython3` Interpreter + Development.Module only if the configure spike proves it cannot enforce CPython 3.14 Arm64. Assert executable, headers, import library, and SOABI share one prefix. |
| `bindings\python\openshot.i:140-202,252-258` | No planned pointer rewrite. Add the real QWidget interoperability test; edit the bridge only if G5 reproduces a defect. |
| `src\CMakeLists.txt:224-230,358-419,421-610` | Remove no features. Pass explicit roots/options and fail if pinned Qt, FFmpeg, OpenMP, ZeroMQ, OpenCV/Protobuf, babl, or ImageMagick is absent. |
| `tests\FFmpegWriter.cpp`, `tests\Timeline.cpp`, and a new binding smoke | Add native deterministic render and QWidget pointer coverage. |

Artifact: `libopenshot-1.0.0-so31-cp314-qt6.11-windows-arm64-<sha>.zip`, with install tree under `install-arm64`.

## PR C - `OpenShot/openshot-qt`

| File/symbol | Required change |
| --- | --- |
| `.gitlab-ci.yml:106-257` | Add `win-arm64`, `windows:msix:package:arm64`, and `win-sign-arm64`; consume only PR B's exact digest, force PyQt6, and run source/native, frozen, package, architecture, and render gates before signing. |
| `freeze.py:142-153,357-443,787-810` | Add canonical `arm64` / `install-arm64` / `clangarm64` mapping; remove warning-shaped Arm release fallbacks; harvest only lock-owned dependencies/plugins and fail on missing required DLLs. |
| `installer\windows.manifest:1-12` | Generate processor architecture `arm64` and inspect the embedded manifest after `mt.exe`. |
| `installer\windows-installer.iss:7-53,129-158` | Map Inno architecture values to `arm64`; retain AppId/default directory for replacement, signed uninstaller, and cleanup behavior. |
| `installer\package_msix.ps1:178-208,270-382` | Parameterize architecture/source name, accept only `OpenShot-*-arm64.exe`, set and inspect manifest `arm64`, and reject captured installers or wrong-machine payloads. |
| `installer\build_server.py:575-598,640-685` | Replace Boolean bitness with a canonical architecture enum; support `install-arm64`, Arm artifact suffixes/signing, and fail-closed metadata. |
| `installer\deploy.py:45-46,94-102,153-161` | Parse/publish `arm64` and architecture-specific metadata without changing x64/x86 behavior. |
| `installer\openshot-msix-template.xml` if present after baseline selection | Generate and validate Arm64 architecture, identity, publisher, executable, and capabilities. Rebase onto #6075 rather than duplicating it. |
| `src\tests\test_export_golden.py`, independent stdlib-only oracle generator, four-stage Qt fixtures, and package-smoke scripts | Add the exact G8/G9 semantic render and source/frozen/Inno/MSIX native/plugin probes. |
| `src\qt_api.py:2284-2486`, `src\windows\export.py:1176-1309` | Reference only unless a gate reproduces a product defect; preserve the selector and writer loop. |
| `src\tests\test_export_clips.py:74-104` | Retain existing mock helper coverage, but do not count it as G9. |

## Required artifact contents

Each producer ZIP contains `artifact-contract.json` with schema version, repository/SHA, source and SO versions, target triplet and PE machine, Python SOABI, Qt build/version, compiler/CRT, package-lock digest, feature flags, pipeline/job, and every payload SHA-256. It also contains the `install-arm64` tree, test/configuration reports, exact Qt plugin and package inventories, PE/import inventory, licenses/notices, and SBOM.

Consumers take an explicit artifact URL/job ID and expected digest. Branch-to-`develop` fallback is forbidden for Arm64. `windows-builder-arm64` is the stable job name; artifact filenames carry version/SO/SHA.

## Release-infrastructure surface

Outside product source, release infrastructure owns a native physical or virtual Windows Arm64 GitLab runner tagged `windows-arm64`, a pinned MSYS2 mirror/image and cache, Inno/MSIX/Windows SDK tools, and signing access. Its G1 evidence is the runner-image digest and tool inventory. Missing infrastructure blocks production CI; it does not justify source redesign.

Canonical values are: `win-arm64`, `windows-builder-arm64`, `build\install-arm64`, `CLANGARM64`, `C:\msys64\clangarm64`, manifest/Inno/MSIX/release token `arm64`, Inno `OpenShot-<version>-arm64.exe`, and MSIX `OpenShot-<version>-arm64.msix`.
