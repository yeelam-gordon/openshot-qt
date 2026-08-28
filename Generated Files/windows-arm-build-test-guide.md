# Windows Arm64 build, test, package, and release guide

## Authority, scope, and current stop condition

This is the executable runbook for the `windows-arm64-clangarm64-v1`
contract. Run it only against the G0-pinned post-4.0 revisions of
`OpenShot/libopenshot-audio`, `OpenShot/libopenshot`, and
`OpenShot/openshot-qt`, in that dependency order. Existing x64/x86 jobs remain
unchanged. GitLab produces release artifacts; matching GitHub jobs are
presubmits only.

**Current verdict: NOT READY.** G0 is not frozen, the signed dependency/toolchain
lock and native GitLab runner are not provisioned, and no Arm64 candidate exists.
Do not publish an Arm64 artifact or mark any downstream gate passed.

**2026-08-28 update — implementation landed (see ARM-READY.r2.md /
IMPLEMENT.r3.md):** the user explicitly authorized product-code
implementation. The Arm64 lanes and acceptance probes described below are no
longer only specified here — they now exist as real, additive, uncommitted
working-tree changes in all three repositories:

- `ci/windows-arm64-packages.lock` and `ci/validate_arm64_architecture.py`
  (byte-identical in all three repos) implement the architecture oracle and
  recursive PE payload check described in this section. The validator has
  been run genuinely on the AMD64 development host: it honestly reports
  `process_machine=UNKNOWN, native_machine=AMD64, native_arm64_ok=False` on
  this non-Arm64 host. With `--require-native-arm64` it rejects this host,
  and it correctly fails closed when pointed at a non-Arm64 payload.
- `windows-builder-arm64` (libopenshot-audio, libopenshot), `win-arm64` /
  `windows:msix:package:arm64` / `win-sign-arm64` (openshot-qt) GitLab CI jobs
  now exist, additive and `allow_failure: true`, tagged `windows-arm64` /
  `code-sign-arm64`. They cannot execute in this workspace because no such
  runner exists and `gitlab.openshot.org` is unreachable — this remains the
  **sole** blocker to running this runbook for real, not missing
  implementation.
- GitHub-hosted `windows-11-arm` presubmits now build the dependency repos
  using `msys2/setup-msys2@v2` with `CLANGARM64`. They are supplemental and
  never supply production release artifacts.
- `libopenshot/tests/NativeArm64ProcessOracle.cpp` and
  `openshot-qt/src/tests/test_native_arm64_process_oracle.py` implement the
  oracle as executable tests. The Python test genuinely passes (5/5) on this
  host; the C++ test is reviewed but unbuilt (no compiler/CMake here).

None of the above changes the NOT-READY verdict for a native release claim —
they change it from "not implemented" to "implemented, blocked only on
external Arm64 infrastructure (runner, signed toolchain snapshot, signing
credentials, physical devices)". See `IMPLEMENT.r3.md`, `IMPL-REVIEW.r4.md`,
and `ARM-READY.r3.md` under `hackathon-fleet/agents/` for full evidence.

### Approved native-process architecture oracle

The design owner approved these diagnostic semantics on 2026-08-28:

- Require `pNativeMachine == IMAGE_FILE_MACHINE_ARM64`.
- Require `pProcessMachine == IMAGE_FILE_MACHINE_UNKNOWN` for native
  execution.
- Treat every nonzero process-machine value as WOW/emulated execution and
  fail.
- Report host/native machine, process machine, WOW/emulation state, and payload
  PE machine as separate fields.
- Continue to require every candidate EXE, DLL, and PYD to have PE machine
  `IMAGE_FILE_MACHINE_ARM64` (`0xAA64`), and retain runtime-module provenance,
  allowlist, duplicate-hash, and import-closure checks.

This resolves IMPL-001. The oracle is executable once a native candidate exists;
it is not evidence that G2, G3, G8, or G11 has passed.

## Required infrastructure and inputs

Use a native Windows 11 Arm64 GitLab runner tagged `windows-arm64`. Emulation,
cross-compilation, ARM64EC, MINGW32/MINGW64, official CPython, PyPI Qt wheels,
MSVC-built Qt, and automatic binding fallback are prohibited.

Required immutable inputs:

- G0 lock with exact repository SHAs, OpenShot/lib/SO versions, producer
  artifact URLs/job IDs, and digests.
- Signed and archived MSYS2 snapshot with a complete checksummed/license BOM.
- `CLANGARM64` at `C:\msys64\clangarm64`, target
  `aarch64-w64-mingw32`, Clang/LLVM 22.1.8-2, libc++ 22.1.8-1,
  compiler-rt 22.1.8-2, UCRT, libwinpthread 14.0.0.r302.gd7f3c5201-1,
  CMake 4.4.2-2, Ninja 1.13.2-1, and SWIG 4.5.0-1.
- MSYS2 Arm64 CPython 3.14.7-1, PyQt6 6.11.0-1, sip 13.12.0-1, Qt
  6.11.2, and source-built cx_Freeze 8.7.0 from SHA-256
  `3d6aed189f96fb6d13182bbc6f33f73d14526fc6fec934286d0456e31faf1543`.
- Locked FFmpeg 9.0.1-3, OpenCV 5.0.0-3, Protobuf 35.1-2, ZeroMQ
  4.3.5-5, cppzmq 4.11.0-1, babl 0.1.128-1, ImageMagick
  7.1.2.30-1, jsoncpp 1.9.8-1, and all transitive native dependencies.
- Windows SDK tools (`mt.exe`, `makeappx.exe`, `signtool.exe`), Inno Setup,
  production signing credentials, timestamp service, and separate prerelease
  package identity.
- Two physical Windows Arm64 devices for G13: one Snapdragon X-class device
  and one older supported Arm64 device.

Start PowerShell from the native Arm64 runner:

```powershell
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
$Root = "C:\build\openshot-arm64"
$Audio = "$Root\libopenshot-audio"
$Lib = "$Root\libopenshot"
$Qt = "$Root\openshot-qt"
$Evidence = "$Root\evidence"
$env:MSYSTEM = "CLANGARM64"
$env:Path = "C:\msys64\clangarm64\bin;C:\msys64\usr\bin;$env:Path"
$env:OPENSHOT_QT_API = "pyqt6"
$env:QT_QPA_PLATFORM = "offscreen"
$env:QT_PLUGIN_PATH = $null
New-Item -ItemType Directory -Force $Evidence | Out-Null
Start-Transcript -Path "$Evidence\run-transcript.txt"
```

Record, then compare to the G0/G1 lock. Any mismatch is a hard stop:

```powershell
Get-CimInstance Win32_OperatingSystem |
  Format-List Caption,Version,BuildNumber,OSArchitecture |
  Out-File "$Evidence\host.txt"
[System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture |
  Out-File "$Evidence\host.txt" -Append
[System.Runtime.InteropServices.RuntimeInformation]::ProcessArchitecture |
  Out-File "$Evidence\host.txt" -Append
cmake --version | Tee-Object "$Evidence\cmake-version.txt"
ninja --version | Tee-Object "$Evidence\ninja-version.txt"
clang --version | Tee-Object "$Evidence\clang-version.txt"
llvm-readobj --version | Tee-Object "$Evidence\llvm-version.txt"
swig -version | Tee-Object "$Evidence\swig-version.txt"
python -VV | Tee-Object "$Evidence\python-version.txt"
pacman -Q | Sort-Object | Out-File "$Evidence\pacman-Q.txt"
```

## Gate sequence

### G0 -- coordinated baseline

After the 4.0 release PRs are merged or superseded, pin all three revisions.
The currently observed evidence SHAs are not production pins.

```powershell
foreach ($Repo in @($Audio, $Lib, $Qt)) {
  Push-Location $Repo
  git status --porcelain
  git rev-parse HEAD
  git describe --tags --always
  Pop-Location
}
```

Expected: clean trees and exact equality with the reviewed G0 lock, including
OpenShot 4.0.0, libopenshot 1.0.0/SO 31, and
libopenshot-audio 1.0.0/SO 10. A changed SHA/version/SO/BOM input creates a new
contract revision and invalidates affected downstream evidence.

### G1 -- dependency and builder lock

Verify repository signatures and every cached package/source/producer SHA-256
before use. Do not run live `pacman -Syu` or an unversioned install. Build
cx_Freeze with the locked native Python/toolchain. Save the signed snapshot
identity, image digest, complete package graph, licenses/notices, compiler
inventory, `python -VV`, FFmpeg `-buildconf`, OpenCV build information, and Qt
build key. Any missing, mutable, foreign-architecture, or unlicensed input
fails G1.

### G4 / PR A -- libopenshot-audio

Use the existing repository CMake build form with the Arm contract:

```powershell
Set-Location $Audio
cmake -B build-arm64 -S . -G Ninja `
  -DCMAKE_BUILD_TYPE:STRING=Release `
  -DCMAKE_INSTALL_PREFIX:PATH="$Audio\build\install-arm64" `
  -DAUTO_INSTALL_DOCS=0
cmake --build build-arm64 --parallel $env:NUMBER_OF_PROCESSORS
ctest --test-dir build-arm64 --output-on-failure -C Release
cmake --install build-arm64 --config Release
```

Expected: exit 0 throughout, required WASAPI support retained, no silent
feature removal, and artifact
`libopenshot-audio-1.0.0-so10-windows-arm64-<sha>.zip`. The artifact contract
must include repository/SHA, version/SO, triplet, PE machine, compiler/CRT,
toolchain-lock digest, feature flags, pipeline/job, payload hashes, tests,
configuration, PE/import inventory, licenses/notices, and SBOM. G4 blocks PR B.

### G2 static architecture/import closure -- run for every stage

Run this after each install/freeze/unpack and before artifact publication:

```powershell
function Test-Arm64PE([string]$Stage, [string]$Report) {
  $files = Get-ChildItem $Stage -Recurse -File |
    Where-Object Extension -in ".exe", ".dll", ".pyd"
  if (-not $files) { throw "No PE payloads found under $Stage" }
  Remove-Item $Report -ErrorAction SilentlyContinue
  foreach ($file in $files) {
    "### $($file.FullName)" | Out-File $Report -Append
    $headers = & llvm-readobj --file-headers --coff-imports $file.FullName 2>&1
    $headers | Out-File $Report -Append
    if ($LASTEXITCODE -ne 0) { throw "llvm-readobj failed: $($file.FullName)" }
    if ($headers -notmatch "IMAGE_FILE_MACHINE_ARM64|Machine:\s*0xAA64") {
      throw "Non-Arm64 PE: $($file.FullName)"
    }
  }
}
```

The implemented gate validator must additionally resolve every non-system
import inside the stage, reject absolute build paths, inventory wheels after
unpacking, reject duplicate basenames with different hashes, compare static
inventory with runtime-loaded modules, and allow only the stage root plus the
reviewed System32 allowlist. Save file path, machine, imports, owner,
provenance, and SHA-256. No candidate PE, wheel, or package may be omitted.

G2 remains unexecuted because no Arm64 candidate or evidence bundle exists.

### G5-G6 / PR B -- libopenshot and Python binding

Consume only PR A's exact URL/job ID and expected digest; branch fallback is
forbidden.

```powershell
Set-Location $Lib
$env:CMAKE_PREFIX_PATH = "$Audio\build\install-arm64;C:\msys64\clangarm64"
cmake -B build-arm64 -S . -G Ninja `
  -DCMAKE_BUILD_TYPE:STRING=Release `
  -DCMAKE_INSTALL_PREFIX:PATH="$Lib\build\install-arm64" `
  -DOpenShotAudio_ROOT="$Audio\build\install-arm64" `
  -DUSE_QT6=ON `
  -DENABLE_MAGICK=ON `
  -DENABLE_OPENCV=ON `
  -DUSE_SYSTEM_JSONCPP=ON `
  -DPYTHON_MODULE_PATH=python `
  -DRUBY_MODULE_PATH=ruby
cmake --build build-arm64 --parallel $env:NUMBER_OF_PROCESSORS
ctest --test-dir build-arm64 --output-on-failure -VV -C Release
cmake --install build-arm64 --config Release
```

Expected: exit 0; all required FFmpeg, OpenCV/Protobuf, OpenMP, ZeroMQ, babl,
ImageMagick, Qt 6, jsoncpp, SWIG, and audio features enabled. Run the
implemented native import, paired CPython executable/header/import-library/
SOABI check, real QWidget/QtPlayer round-trip, and G6 native semantic golden
tests. Those required tests do not exist on the assessed baseline, so their
absence is a failure, not a skip. Publish only
`libopenshot-1.0.0-so31-cp314-qt6.11-windows-arm64-<sha>.zip` with the complete
contract and G2 reports.

### G3 -- imports, Qt ABI, plugins, and runtime provenance

With native CPython, import `openshot`, `PyQt6.QtCore`, `PyQt6.QtGui`,
`PyQt6.QtWidgets`, and `PyQt6.sip`; require CPython 3.14, Arm64, Qt 6.11.2,
PyQt 6.11.0, expected SOABI, and one binding. Create an offscreen
`QApplication` and `QWidget`, pass it through the real libopenshot QWidget API,
round-trip the `QtPlayer` renderer object, and destroy it cleanly.

Require these paths and their locked closure:

```text
platforms\qoffscreen.dll
platforms\qwindows.dll
imageformats\qgif.dll
imageformats\qico.dll
imageformats\qjpeg.dll
imageformats\qsvg.dll
iconengines\qsvgicon.dll
multimedia\ffmpegmediaplugin.dll
Qt6Multimedia.dll
```

The specification calls this the ten-item inventory but names nine paths;
resolve that count discrepancy through design review rather than inventing a
file. Source loads must be lock-owned under `C:\msys64\clangarm64`; packaged
loads must be under the application root. Require one path/hash each for
Qt6Core, Qt6Gui, and Qt6Multimedia and no loader warning, duplicate Qt,
alternate backend, out-of-root non-system module, or unresolved import.

G3 remains unexecuted because no native source or packaged candidate exists.

### G7-G9 / PR C -- source, freeze, plugin, and render acceptance

Consume only PR B's exact artifact and digest. Use the existing app test and
freeze commands:

```powershell
Set-Location $Qt
$env:Path = "$Lib\build\install-arm64\bin;$Lib\build\install-arm64\python;$env:Path"
$env:PYTHONPATH = "$Lib\build\install-arm64\python"
$env:OPENSHOT_QT_API = "pyqt6"
$env:QT_QPA_PLATFORM = "offscreen"
python -m unittest discover -s src/tests -t src/tests --quiet
python -u freeze.py build --git-branch=$env:CI_COMMIT_REF_NAME
```

The Arm implementation must map only `arm64`, `install-arm64`, and
`clangarm64`, build cx_Freeze with native CPython, and fail closed on missing
inputs/plugins. `launch.py -V` is not acceptance.

Run one committed probe and identical fixtures, unchanged, at source, frozen,
clean Inno install, and clean MSIX install, once with
`QT_QPA_PLATFORM=offscreen` and once with normal `qwindows`. Set
`QT_DEBUG_PLUGINS=1`, clear inherited `QT_PLUGIN_PATH`, install the Qt message
handler, use isolated profiles, require an explicit ready marker, open a tiny
project, and exit within 60 seconds.

At each stage require:

- 2x2 PNG/JPEG/GIF/ICO/SVG reads with format, dimensions, canonical RGBA8888
  hashes, and required plugin provenance.
- SVG `QIcon` render to transparent 32x32 RGBA8888 with its fixed hash and
  `qsvgicon.dll`.
- Exactly 4,800 stereo `s16le` frames at 48 kHz from the fixed WAV,
  SHA-256 `2eefef4340ebac7010fd20389a475c6086faa0fe7acb8f4ab118df4eee3a3704`,
  `LoadedMedia` and `EndOfMedia` within 10 seconds, and locked
  `ffmpegmediaplugin.dll`.
- Source-only import, binding, babl, ImageMagick, OpenCV, ZeroMQ, and FFmpeg
  decode smokes.

The G8 probe/fixtures are not present on the assessed baseline. Their absence
fails the gate.

For G9, first run the stdlib-only oracle. It must reproduce all 60 ordered
frame hashes and these values before invoking product code:

```text
video:    a3602aa3a3e5316d9456c97eb8bafe5c97a692ed5c10f3409db763bfb331b83a
PCM:      fb240a5aa9dad1572ba742e9a98cd4d33dc078d57c6d2d7cdbfb077df8cb7cd2
manifest: be4c2c85757437afa5861ff92c121af4ec38ef7fd222371881c92511e5e5b1de
```

Run two independent FFV1/PCM/Matroska exports and compare decoded semantic
bytes, stream count, codecs, formats, dimensions, counts, rates, time bases,
PTS, 2,000 ms coverage, metadata, and exact no-padding behavior. Do not compare
volatile container bytes. Exercise the real writer for unavailable codec,
open failure, first/midstream write failure, close failure, and fixed-frame
cancellation; require normal nonzero/cancel signaling, writer release, stopped
progress, and no success-shaped output. Existing mock tests do not satisfy G9.

### G10 -- package metadata and closure

The Arm jobs must be named `win-arm64`, `windows:msix:package:arm64`, and
`win-sign-arm64`; their dependency producer is `windows-builder-arm64`.
Required outputs are `OpenShot-<version>-arm64.exe` and
`OpenShot-<version>-arm64.msix`.

Require:

- Embedded application manifest and every PE report `arm64`/`0xAA64`.
- Inno `ArchitecturesAllowed=arm64` and
  `ArchitecturesInstallIn64BitMode=arm64`, never `x64compatible`.
- Inno AppId `{4BB0DCDC-BC24-49EC-8937-72956C33A470}` and the current default
  directory.
- Unpacked `AppxManifest.xml` has `ProcessorArchitecture="arm64"`, reviewed
  identity, exact publisher/certificate-subject match, executable, version,
  and capabilities.

```powershell
makeappx unpack /p "$Root\OpenShot-<version>-arm64.msix" /d "$Root\msix-unpacked"
Test-Arm64PE "$Root\msix-unpacked" "$Evidence\g10-msix-pe.txt"
Select-String "$Root\msix-unpacked\AppxManifest.xml" 'ProcessorArchitecture="arm64"'
```

Inspect the pre-Inno stage with `Test-Arm64PE`; inspect installer directives
and embedded manifests after build. A package is not accepted from filename or
manifest architecture alone.

### G11 -- independent installed-stage acceptance

Use clean snapshots for Inno and MSIX; do not install both into one test state.

```powershell
& "$Root\OpenShot-<version>-arm64.exe" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART `
  /LOG="$Evidence\inno-clean-install.log"
if ($LASTEXITCODE -ne 0) { throw "Inno install failed: $LASTEXITCODE" }

Add-AppxPackage -Path "$Root\OpenShot-<version>-arm64.msix"
Get-AppxPackage -Name "<G0-approved-package-name>" |
  Format-List * | Out-File "$Evidence\msix-package.txt"
```

For each isolated install, rerun unchanged G2/G3/G8/G9 checks, normal launch,
`.osp` association launch, firewall opt-in, render, and uninstall. Verify no
install directory, uninstall entry, association, task, package registration,
or firewall rule remains. Save before/after inventories. G11 is currently
G11 remains unexecuted because no Inno or MSIX Arm64 candidate exists.

### G12 -- signing, migration, failure, and rollback

Run only on physical Arm64 with production-equivalent credentials:

```powershell
Get-AuthenticodeSignature "$Root\OpenShot-<version>-arm64.exe" |
  Format-List * | Out-File "$Evidence\inno-authenticode.txt"
signtool verify /pa /all /v "$Root\OpenShot-<version>-arm64.exe" `
  *> "$Evidence\inno-signtool.txt"
Get-AuthenticodeSignature "$Root\OpenShot-<version>-arm64.msix" |
  Format-List * | Out-File "$Evidence\msix-authenticode.txt"
signtool verify /pa /all /v "$Root\OpenShot-<version>-arm64.msix" `
  *> "$Evidence\msix-signtool.txt"
```

Require valid payload/uninstaller policy and timestamp chains. Test clean and
silent install, latest signed x64-to-Arm64 replacement, same-version repair,
newer upgrade, downgrade refusal, launch/render, and complete uninstall for
both formats. Preserve projects/preferences, remove x64 program files before
Arm files, re-register `.osp`, and leave one uninstall entry.

Inject unsigned/wrong publisher, altered payload, timestamp outage,
unsupported signing tool, denied elevation, locked file, low disk,
interruption, malformed architecture, and MSIX registration failure. A failed
replacement must restore or preserve a launchable prior install and never
leave a mixed directory. Never upload a failed candidate.

Before publication, rollback disables only Arm trigger/package/sign jobs and
retains evidence. After prerelease, remove only Arm prerelease assets/package
availability. Installed Arm64-to-x64 rollback is explicit uninstall/reinstall
unless a separately tested signed higher-version x64 replacement is approved.

### G13 -- physical-device acceptance

Hosted CI and emulation cannot satisfy G13. On both required devices, record
model/SoC, firmware, RAM, GPU/driver, audio devices, Windows build, power mode,
thermal state, artifact hashes, all three source SHAs, lock digest, and native
process/module evidence.

| Area | Required workload and threshold |
| --- | --- |
| Launch/GUI | 10 cold + 10 warm launches and core project/dialog/image/effects work; 20/20 interactive within 30 s, no crash/hang, all modules Arm64. |
| Preview | 10-minute 1080p30 H.264/AAC playback, 20 fixed seeks, scrub/pause/resume; no crash/deadlock/blank frame and A/V within 100 ms after settling. |
| Audio output | Enumerate/switch/unplug outputs; resume within 5 s, no crash, WASAPI logged. |
| Audio input | Enumerate mic, record/play 30 s, deny/retry; correct 48 kHz channels/duration within 100 ms or actionable non-crashing denial. |
| Software export | G9 plus three 2-minute 1080p30 H.264/AAC exports; 3/3 valid, no corruption/crash. |
| Hardware codecs | Inventory and test every available Windows Arm path plus one unavailable request; valid output or visible pinned-software fallback/early failure. |
| Sleep/resume | Suspend 2 minutes during idle/playback/paused export; UI within 10 s, playback restart, correct resume or explicit no-success failure. |
| Paths/projects | Open/save/render at >240-character and non-ASCII/emoji paths; exact content, no missing media/mojibake. |
| Memory pressure | Preview/export at 85% committed memory and controlled failure; no hang, valid success or explicit failure without success artifact. |
| Repetition | 25 launch/open/preview/export/exit cycles; 25/25, no crash/hang, cycle 5-to-25 post-idle working-set growth <20%. |
| Lifecycle | All G10-G12 Inno/MSIX scenarios; no mixed architecture or stale registration. |

For native-versus-x64-emulated correctness, use the identical immutable G8/G9
fixtures and record separate reports. Both must meet the same semantic hashes,
counts, timestamps, plugin behavior, and failure assertions. Do not merge
module inventories or infer native readiness from the x64 run. Report median
and range for three cold and three warm runs for each architecture; there is no
predetermined performance superiority threshold and no unsupported
performance/power claim.

Stable promotion is forbidden with any missing mandatory hardware row or a
waived crash, architecture, render, audio-output, upgrade, signature, or
uninstall failure.

## Failure triage and evidence bundle

Every command must preserve command line, start/end UTC, exit code, stdout,
stderr, host/device inventory, source SHAs, toolchain-lock digest, and artifact
SHA-256. A nonzero exit, timeout, missing report, warning-producing required
plugin, missing feature, wrong machine, unresolved import, mutable dependency,
out-of-root load, duplicate Qt, hash mismatch, partial success output, or
cleanup residue fails its gate.

Minimum evidence tree:

```text
evidence\
  host.txt
  source-lock.txt
  toolchain\
  g1-bom\
  g2-pe-import\
  g3-qt-runtime\
  g4-audio\
  g5-lib-binding\
  g6-native-golden\
  g7-freeze\
  g8-source-frozen\
  g9-render-failures\
  g10-package\
  g11-inno\
  g11-msix\
  g12-signing-migration\
  g13-device-new\
  g13-device-old\
```

End the run with:

```powershell
Get-ChildItem $Evidence -Recurse -File |
  Get-FileHash -Algorithm SHA256 |
  Sort-Object Path |
  Format-Table -AutoSize |
  Out-File "$Evidence\evidence-sha256.txt"
Stop-Transcript
```

No gate is `PASS` without its owner-produced raw evidence. A producer failure
blocks every consumer; do not substitute a branch artifact, another ABI,
emulation, or an unreviewed fallback.
