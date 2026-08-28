# OpenShot Windows Arm64 implementation and acceptance specification

## Baseline, ABI, and production graph

G0 freezes a post-4.0-release-merge `develop` baseline across all three repositories, including exact SHAs, OpenShot/lib/SO versions, and the common toolchain lock. No production artifact starts before that freeze. Any changed SHA, version, SO value, dependency, or BOM input creates a new contract revision and reruns affected downstream gates.

The immutable contract is `windows-arm64-clangarm64-v1`: Windows 11 Arm64, PE machine `0xAA64`, MSYS2 `CLANGARM64` at `C:\msys64\clangarm64`, `aarch64-w64-mingw32`, Clang/LLVM 22.1.8-2, libc++ 22.1.8-1, compiler-rt 22.1.8-2, UCRT, libwinpthread 14.0.0.r302.gd7f3c5201-1, CMake 4.4.2-2, Ninja 1.13.2-1, and SWIG 4.5.0-1.

Use only MSYS2 Arm64 CPython 3.14.7-1, PyQt6 6.11.0-1/sip 13.12.0-1, and Qt 6.11.2 from the same snapshot. Force `OPENSHOT_QT_API=pyqt6`, `USE_QT6=ON`, and one paired Python executable/include/import library/SOABI in Release mode. Official Python, debug/release mixing, PyPI Qt, MSVC Qt, MINGW32/MINGW64, MSVC runtimes, x64, ARM64EC, and emulation are forbidden. Ninja is required only for new Arm jobs.

```text
OpenShot Arm64 Inno/MSIX candidate                         [openshot-qt GitLab]
|-- frozen MSYS2 CPython 3.14.7 Arm64
|   |-- PyQt6/sip + Qt 6.11.2 and exact plugins           [same lock]
|   |-- source-built cx_Freeze Arm64 base
|   `-- openshot.py + _openshot.pyd                       [PR B artifact]
|       `-- libopenshot 1.0.0 / SO 31 Arm64
|           |-- Qt, FFmpeg, OpenCV/Protobuf, OpenMP,
|           |   ZeroMQ, babl, ImageMagick                 [same lock]
|           `-- OpenShotAudio 1.0.0 / SO 10 Arm64         [PR A artifact]
|-- Inno manifest/identity/signature
`-- MSIX manifest/identity/signature
```

Every bundled `.exe`, `.dll`, and `.pyd` is recursively inventoried with `llvm-readobj --file-headers --coff-imports`. All must be ARM64, all non-system imports must resolve within the stage, and static inventory must match runtime modules. Duplicate basenames with different hashes, unresolved imports, foreign architecture/prefix, and absolute build paths fail.

## Implementation sequence

1. **G0:** Release maintainers merge or supersede #6075/#1082/#170, freeze the three-repository SHA/version/SO lock, link three draft PRs from #5853, and refresh source/dependency evidence.
2. **G1:** Release infrastructure archives the signed MSYS2 snapshot, completes checksums/licenses/dependencies, builds pinned cx_Freeze, and emits runner-image/tool inventory. No ABI substitution is allowed.
3. **PR A / G4:** Build/test/scan `libopenshot-audio`, preserve x64/x86, and publish its immutable contract artifact.
4. **PR B / G5-G6:** Consume only PR A's digest, build libopenshot/SWIG, run CTest/import/QWidget/feature/native-golden gates, and publish its immutable contract artifact.
5. **PR C / G7-G11:** Consume only PR B's digest; test source, freeze, inspect, render, package, independently install Inno and MSIX, repeat probes/render/uninstall, then hand candidates to signing.
6. **G12:** Release maintainers prove signatures and migration/failure behavior with a prerelease identity and publish only a prerelease Arm64 asset.
7. **G13:** Hardware QA runs the two-device matrix. Stable promotion requires all mandatory logs and assertions.

## G2-G3: architecture, Qt provenance, and QWidget ABI

Before QWidget use, native Python imports `openshot`, PyQt6 Core/Gui/Widgets, and `PyQt6.sip`; reports CPython 3.14, Arm64, Qt 6.11.2, PyQt 6.11.0, and expected SOABI; creates an offscreen `QApplication`/`QWidget`; passes it through the real libopenshot QWidget API; round-trips the `QtPlayer` renderer object; and destroys it without crash, exception, or pointer truncation.

Require the ten Qt DLL/plugin paths and complete locked closure in `appendix-references.md`. At source, every non-system load is lock-owned below `C:\msys64\clangarm64`; at frozen/Inno/MSIX stages every load is below the application root. For native Arm64 execution, `IsWow64Process2` must report `pProcessMachine == IMAGE_FILE_MACHINE_UNKNOWN` and `pNativeMachine == IMAGE_FILE_MACHINE_ARM64`; any nonzero process-machine value indicates WOW/emulation and fails. Prove the payload itself is Arm64 independently through the recursive PE scan requiring machine `0xAA64`. Each stage has one hash/path for Qt6Core, Qt6Gui, and Qt6Multimedia and no foreign or duplicate runtime.

## G8: one unchanged four-stage native/plugin probe

Run one probe and committed fixtures unchanged from source interpreter, frozen directory, clean Inno installation, and clean MSIX installation, once with `QT_QPA_PLATFORM=offscreen` and once with normal `qwindows`. Enable `QT_DEBUG_PLUGINS=1`, install a Qt message handler, clear inherited `QT_PLUGIN_PATH`, and capture plugin logs, `QCoreApplication.libraryPaths()`, loaded PE paths/hashes/owners, and process/native architecture.

At every stage:

- Read the fixed 2x2 PNG/JPEG/GIF/ICO/SVG fixtures with `QImageReader`, assert format/non-null/dimensions/canonical RGBA8888 digest, and prove the required image plugins.
- Render the SVG through `QIcon` to transparent 32x32 RGBA8888, assert its digest, and prove `qsvgicon.dll`.
- Decode the fixed 4,800-frame stereo WAV through `QMediaPlayer` and `QAudioBufferOutput` with no device, reaching `EndOfMedia` within 10 seconds and exactly matching its signed `s16le` digest; prove `ffmpegmediaplugin.dll`.
- Use isolated profiles; reach an explicit ready marker; open a tiny project; run G9; and exit cleanly within 60 seconds. Source also runs targeted import, binding, babl, ImageMagick, OpenCV, ZeroMQ, and FFmpeg decode smokes. `launch.py -V` is insufficient.

Fail nonzero with an actionable report on missing output/file/DLL, unsupported fixture, timeout, out-of-root fallback, duplicate Qt, any plugin/dependency warning, hash mismatch, wrong binding, foreign module, or removed codec. Source, frozen, Inno, and MSIX reports are separate and mandatory.

## G9: semantic golden render and writer failures

The normative formulas, exact frame hashes, aggregate hashes, fixture values, formats, dimensions, counts, PTS/time bases, FFV1/PCM/Matroska options, metadata, semantic exclusions, and independent-generator rules are in `appendix-references.md`. They are immutable oracle input.

Decode through the locked OpenShot/FFmpeg reader to canonical BGRA and interleaved `s16le`. Assert all 60 frame hashes, both aggregate payload hashes, formula-derived bytes, counts, formats, stream count, codec IDs, source/output PTS and time bases, frame/sample rates, channel layout, 2,000 ms coverage, and exact no-padding behavior. Two independent exports must have identical semantics and normalized stream metadata.

The stdlib-only oracle validates the committed manifest before invoking the writer and cannot use product or production-oracle code. The implementation under test can never generate or bless expected values. Store generated file/report on failure. An oracle version changes only by explicit review.

Exercise the real writer for unavailable codec, open failure, first/midstream write failure, close failure, and fixed-frame cancellation. Assert nonzero/normal cancellation signaling, cleanup, writer release, stopped progress, and no success-shaped partial output. Mock helper tests remain useful but cannot satisfy G9.

## G10-G12: package identity, migration, signing, and failure

| Surface | Required Arm64 value |
| --- | --- |
| CI / producer job | `win-arm64` / `windows-builder-arm64` |
| install prefix | `build\install-arm64` |
| environment / prefix | `CLANGARM64` / `C:\msys64\clangarm64` |
| PE/application manifest | `arm64` / machine `0xAA64` |
| Inno allowed/64-bit mode | `arm64`, never `x64compatible` |
| Inno artifact | `OpenShot-<version>-arm64.exe` |
| MSIX manifest/artifact | `ProcessorArchitecture="arm64"` / `OpenShot-<version>-arm64.msix` |
| release token | `arm64` |

Inno retains AppId `{4BB0DCDC-BC24-49EC-8937-72956C33A470}` and the current default directory. Production Arm64 upgrades/replaces emulated x64; side-by-side machine-wide installation is unsupported. Refuse downgrade; preserve user projects/preferences; remove x64 program files before Arm files; re-register `.osp`; leave one uninstall entry. Failed replacement restores or leaves a launchable prior install and never leaves a mixed directory.

MSIX retains the maintainer-approved post-#6075 identity so architecture replacement occurs under one family. Publisher exactly matches the certificate subject. Only a distinct prerelease identity may coexist.

On physical Arm64, for both signed formats:

1. Inspect directives, embedded application manifest, every PE, unpacked Appx manifest, identity/version/architecture, and hashes.
2. Require successful `Get-AuthenticodeSignature` and `signtool verify /pa /all /v`, including timestamp chain, installer, applicable launcher/DLL policy, signed uninstaller, and MSIX.
3. Prove clean/silent install, launch, `.osp` association, firewall opt-in, golden export, and complete uninstall cleanup.
4. Prove latest signed x64-to-Arm64 upgrade/render/uninstall, same-version repair, newer upgrade, and downgrade refusal.
5. Inject unsigned/wrong publisher, altered payload, timestamp outage, unsupported signing tool, denied elevation, locked file, low disk, interruption, malformed architecture, and MSIX registration failure. Never upload or report a failed candidate as successful.

## G13: physical Windows Arm64 matrix

Run on a Snapdragon X-class Windows 11 device and an older supported Arm64 device. Record model/SoC, firmware, RAM, GPU/driver, audio devices, Windows build, power/thermal state, artifact, all source SHAs, lock digest, and native architecture evidence.

| Area | Procedure and pass threshold |
| --- | --- |
| Launch/GUI | 10 cold + 10 warm launches and core project/dialog/image/effects work; 20/20 interactive within 30 s, zero crash/hang, all modules Arm64. |
| Preview/playback | 10-minute 1080p30 H.264/AAC playback, 20 seeks, scrub/pause/resume; no crash/deadlock/blank frame and A/V within 100 ms after settle. |
| Audio output | Enumerate/switch/unplug outputs; audio resumes within 5 s, no crash, WASAPI logged. |
| Audio input | Enumerate mic, record/play 30 s, deny/retry; 48 kHz channels/duration within 100 ms or actionable non-crashing denial. |
| Software export | G9 plus three 2-minute 1080p30 H.264/AAC exports; 3/3 valid with no corruption/crash. |
| Hardware codecs | Inventory/test available Windows Arm paths and unavailable request; valid output or visible pinned-software fallback/early error, never corrupt output. |
| Sleep/resume | Suspend 2 minutes during idle/playback/paused export; UI within 10 s, playback restart, and correct resume or explicit no-success failure. |
| Paths/projects | Open/save/render under >240-character and non-ASCII/emoji paths; exact content, no missing media/mojibake. |
| Memory pressure | Preview/export at 85% committed memory and force controlled failure; no hang, valid success or explicit failure with no success artifact. |
| Repetition | 25 launch/open/preview/export/exit cycles; 25/25, no crash/hang, cycle 5-to-25 post-idle working-set growth <20%. |
| Install lifecycle | Execute all G10-G12 Inno/MSIX scenarios; no mixed architecture or stale registration. |

Report median and range for three cold and three warm performance runs, with no predetermined x64 comparison. Hosted CI/emulation cannot satisfy G13. No stable asset may waive crash, architecture, render, audio-output, upgrade, signature, or uninstall failure.

## Gate ownership and release blocks

| Gate | Owner | Evidence | Blocks |
| --- | --- | --- | --- |
| G0 baseline | Three release maintainers | Post-4.0 SHA/version/SO lock | Production implementation |
| G1 dependency/toolchain | Release infrastructure | Signed snapshot, BOM/checksums/licenses, image digest | Native builds |
| G2 architecture/import | CI owners | Static PE/import reports | Artifact publication |
| G3 Qt ABI/provenance | Library/app owners | Exact inventory, four-stage load logs, no-fallback report | QWidget/package |
| G4 audio | Audio owner | Native CTest and PR A contract | PR B |
| G5 library/binding | libopenshot owner | CTest/import/QWidget/feature smokes | PR B artifact |
| G6 native golden | libopenshot owner | Semantic render report | PR C |
| G7 cx_Freeze | App owner | Arm base/freeze/hooks/startup | Package creation |
| G8 source/frozen | App owner | Ready marker and exact probe/module reports | Installers |
| G9 packaged golden | App owner | Semantic hashes and real failure cases | Signing |
| G10 package metadata | Packaging owner | Manifests, PE closure, identities | Signing |
| G11 installed smoke | Packaging owner | Separate Inno/MSIX probes/render/uninstall | Prerelease |
| G12 migration/signing | Release maintainer | Signatures and migration/failure reports | Prerelease/stable |
| G13 hardware | Hardware QA | Completed two-device matrix and logs | Stable |

## Rollback and gated assumptions

Before publication, disable only Arm trigger/package/sign jobs and retain logs. After prerelease, remove only Arm assets/availability; x64/x86 remain. Arm64-to-x64 rollback is deliberate uninstall/reinstall unless signed migration tests prove a higher-version x64 replacement.

Open assumptions remain explicit gates: cx_Freeze/CPython native base (G7), OpenCV/Protobuf compatibility without feature loss (G5), native GitLab and signing/MSIX tooling (G1/G12), locked FFmpeg codecs/devices/behavior (G5/G9/G13), Qt FFmpeg plugin four-stage decoding (G3/G8/G11), and recoverable Inno/MSIX x64 replacement (G12). None is a success claim in this workspace.
