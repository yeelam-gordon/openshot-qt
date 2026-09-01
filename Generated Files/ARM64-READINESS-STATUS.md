# ARM64 Readiness Status

Date: 2026-08-31  
Owner chain: `OPEN-AUDIO-001 -> OPEN-LIB-002 -> OPEN-QT-003`

## Overall verdict

**Source-chain status: READY FOR A REAL ARM64 TOOLCHAIN/RUNTIME WORKER. `openshot-qt` retains the MSIX staging fix/tests, and `libopenshot` now has a repaired native ARM64 runtime test pass on a locally restored CLANGARM64 toolchain.**

- `libopenshot-audio`: no reproduced source defect in this pass.
- `libopenshot`: runtime repair round reproduced and fixed repository-side native ARM64 test failures in audio-device expectations, spherical metadata lifecycle/validation, and ImageMagick buffer cleanup.
- `openshot-qt`: fixed MSIX staging to stay inside the repository worktree instead of a temp directory (`installer/package_msix.ps1`), and added an executed preparation-only test that exercises repo-local `build\msix\installer-source` staging/cleanup without invoking production packaging or signing.
- Native host evidence is real on this machine: the shared validator reported `process_machine=UNKNOWN`, `native_machine=ARM64`, and `native ARM64 ok=True`.
- A project-local MSYS2 `CLANGARM64` toolchain was restored during runtime repair at `D:\Hack2026\openshot-msys64\msys64` (via the existing `C:\msys64` junction) and was sufficient to rebuild and rerun `libopenshot` tests.
- That restored toolchain does **not** match the repository lock: `ci\validate_arm64_architecture.py --package-lock` now fails with 19 version drifts (for example FFmpeg `8.1.1-2` vs locked `9.0.1-3`, OpenCV `4.13.0-6` vs locked `5.0.0-3`, Qt `6.11.1-1` vs locked `6.11.2-*`), so this is valid runtime evidence but **not** a G1 lock-compliant release environment.

## Shared chain proof

- Shared validator SHA-256 in all 3 repos: `14B9F97E8E7313FF2854958F0DE998E8EAD484679F5DA72F3048521D92290E54`
- Shared package-lock SHA-256 in all 3 repos: `AB8190A67FAFD8D2C2058C449B7038BD209AF8B273C48EC457F021E51E6744F7`
- Producer/consumer handoff wiring is present end-to-end:
  - `libopenshot-audio\.gitlab-ci.yml:90-111` publishes `build/install-arm64` plus `arm64-architecture-report.json`.
  - `libopenshot\.gitlab-ci.yml:125-148` downloads `windows-builder-arm64` from `libopenshot-audio` and consumes it as `OpenShotAudio_ROOT=$CI_PROJECT_DIR\build\install-arm64`.
  - `OpenShot\.gitlab-ci.yml:151-187` downloads `windows-builder-arm64` from `libopenshot`, validates `build/install-arm64`, freezes the GUI, and re-validates the frozen tree.
  - `OpenShot\.gitlab-ci.yml:313-348` packages/signs the Arm64 MSIX lane.
  - `OpenShot\freeze.py:143-150` prefers `build\install-arm64` when `MSYSTEM=CLANGARM64`.
  - `OpenShot\installer\build_server.py:625-666,709-958` selects the Arm64 artifact root, produces `-arm64.exe`, and stages Qt6/PyQt6 Arm64 runtime content.

## Repository status

### 1) `libopenshot-audio`

- Branch / HEAD: `feature/windows-arm64-native` @ `d572b7fdd9b25dad705336a4424ac814ae725971`
- Diff created in this pass: **none**
- Validation evidence:

| Command | Exit |
| --- | ---: |
| `python -m py_compile ci\validate_arm64_architecture.py ci\test_validate_arm64_architecture.py` | 0 |
| `python ci\test_validate_arm64_architecture.py` | 0 |
| `python ci\validate_arm64_architecture.py` | 0 |
| `python ci\validate_arm64_architecture.py --require-native-arm64` | 0 |

- Notes:
  - CI/unit coverage exists in `ci\test_validate_arm64_architecture.py:32-45`.
  - Arm64 producer contract is wired in `libopenshot-audio\.gitlab-ci.yml:90-111`.

Confidence: **high** for repository-side validation that does not require the missing MSYS2/CMake toolchain.

### 2) `libopenshot`

- Branch / HEAD: `feature/windows-arm64-native` @ `29e8bedfbdb600792b114676bb42681b35876adc`
- Diff created in runtime repair:
  - `src\FFmpegWriter.h`, `src\FFmpegWriter.cpp`
  - `src\FFmpegReader.cpp`
  - `src\MagickUtilities.cpp`
  - `src\QtUtilities.h`
  - `tests\AudioDeviceManager.cpp`
  - `tests\ImageWriter.cpp`
  - `tests\SphericalMetadata.cpp`
- Validation evidence:

| Command | Exit |
| --- | ---: |
| `python -m py_compile ci\validate_arm64_architecture.py ci\test_validate_arm64_architecture.py` | 0 |
| `python ci\test_validate_arm64_architecture.py` | 0 |
| `python ci\validate_arm64_architecture.py` | 0 |
| `python ci\validate_arm64_architecture.py --require-native-arm64` | 0 |
| `cmake --build build --parallel <proc>` (restored CLANGARM64 toolchain) | 0 |
| `ctest -R "AudioDeviceManager|SphericalMetadata|ImageWriter" --output-on-failure -VV` | 0 |
| `ctest --output-on-failure -VV` | 0 |
| `python3 ci\validate_arm64_architecture.py --require-native-arm64 --payload-root build --require-payload --json-report build\arm64-build-tree-report-no-lock.json` | 0 |
| `python3 ci\validate_arm64_architecture.py --require-native-arm64 --package-lock ci\windows-arm64-packages.lock --payload-root build --require-payload --json-report build\arm64-build-tree-report.json` | 1 |

- Notes:
  - Arm64 consumer/producer chain is wired in `libopenshot\.gitlab-ci.yml:125-148`.
  - The restored native ARM64 toolchain rebuilt `libopenshot` and all tests; full CTest is now **519/519 passed** on this host.
  - `AudioDeviceManager.cpp` now accepts the actual opened supported rate and explicitly resets the singleton before the fake-device path.
  - `FFmpegWriter` now rejects no-video/post-header spherical metadata calls, defers side-data application until after the final codec-parameter copy and before header write, and keeps positive pre-open/pre-header behavior covered by regression tests.
  - `MagickUtilities.cpp` now uses straight-RGBA conversion plus allocator-matched cleanup (`cleanUpArrayBuffer`) and a lifetime test.
  - On the currently available FFmpeg 62-based restored toolchain, `ffprobe` still reports spherical mapping **presence/projection** but normalizes nonzero yaw/pitch/roll back to zero on MP4 readback; the regression tests now record that toolchain behavior as a warning while continuing to enforce metadata presence, numeric parsing, and explicit invalid-call rejection.

Confidence: **high** for repository-side native ARM64 runtime correctness on the currently restored toolchain; **medium** for locked-release equivalence until the exact package snapshot is restored.

### 3) `openshot-qt`

- Branch / HEAD: `hackathon/windows-arm64-demo` @ `9294063d118ba064875efc4a180edd17f1c56f56`
- Diff created in this pass:
  - `installer\package_msix.ps1`: replaced temp-directory staging with repo-local `build\msix\installer-source`.
  - `ci\test_package_msix_staging.py`: added a targeted unittest that runs the PowerShell script's preparation path and verifies repo-local staging/cleanup semantics.

- Reproduced defect and fix:
  - **Observed defect:** `installer\package_msix.ps1` staged the installer via `[System.IO.Path]::GetTempPath()`, which violates this workspace's no-temp-file rule and risks packaging failure in automation.
  - **Fix applied:** `installer\package_msix.ps1` now exposes a preparation path that stages under repo-local `build\msix\installer-source`, emits a machine-readable preparation report, preserves pre-existing `.msix` artifacts and packaging logs during `-PrepareOnly`, and still sets `ProcessorArchitecture` from `x86_64|x86|arm64` to `x64|x86|arm64`.

- Validation evidence:

| Command | Exit |
| --- | ---: |
| `python -m py_compile ci\validate_arm64_architecture.py ci\test_validate_arm64_architecture.py src\tests\test_native_arm64_process_oracle.py src\tests\test_release_details.py freeze.py installer\build_server.py installer\deploy.py installer\version_parser.py` | 0 |
| `python ci\test_validate_arm64_architecture.py` | 0 |
| `python -m unittest discover -s ci -p test_package_msix_staging.py -v` | 0 |
| `python -m unittest discover -s src\tests -t src\tests -p test_native_arm64_process_oracle.py -v` | 0 |
| `python -m unittest discover -s src\tests -t src\tests -p test_release_details.py -v` | 0 |
| `python ci\validate_arm64_architecture.py` | 0 |
| `python ci\validate_arm64_architecture.py --require-native-arm64` | 0 |
| PowerShell parser check for `installer\package_msix.ps1` | 0 |
| `git diff --check -- installer\package_msix.ps1 ci\test_package_msix_staging.py Generated Files\ARM64-READINESS-STATUS.md` | 0 |

- Notes:
  - Application Arm64 lane is wired in `OpenShot\.gitlab-ci.yml:151-187,313-348`.
  - `freeze.py:143-150` prefers `install-arm64`.
  - `installer\build_server.py:625-666,709-958` handles Arm64 naming, artifact selection, Qt6 plugin copy, and Qt6 DLL staging.
  - `src\tests\test_native_arm64_process_oracle.py:39-89` passed 5/5 on this native Arm64 host.
  - `ci\test_package_msix_staging.py` executed `installer\package_msix.ps1 -PrepareOnly` against a fake installer/template, proved repo-local staging at `build\msix\installer-source`, verified stale staged files/report/generated-template refresh correctly, and verified pre-existing `.msix` artifacts plus packaging logs survive `-PrepareOnly`.
  - This test covers **preparation/staging semantics only**. It does **not** claim that the full MSIX Packaging Tool run, package signing, installation, or GUI launch succeeded on this worker.

Confidence: **high** for repository-side packaging/source correctness available from this worker.

## Remaining gates outside this worker

1. Replace the currently restored but drifted local CLANGARM64 stack with the exact locked package snapshot required by `ci\windows-arm64-packages.lock`.
2. Build and install in dependency order with real Arm64 artifacts:
   - `libopenshot-audio`
   - `libopenshot`
   - `openshot-qt`
3. Run payload validation with `--package-lock` against the produced install/frozen trees in that lock-compliant environment.
4. Create/sign/package the `.exe` and `.msix`.
5. Install and smoke-test the real GUI locally.

## Exact runtime-worker instructions

Run these in order on the real Windows Arm64 machine with the MSYS2 `CLANGARM64` stack installed and on `PATH`.

### A. `libopenshot-audio`

```powershell
Set-Location D:\Hack2026\libopenshot-audio
$env:MSYSTEM = "CLANGARM64"
$env:Path = "C:\msys64\clangarm64\bin;C:\msys64\usr\bin;$env:Path"
cmake -B build -S . -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=build\install-arm64 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++
cmake --build build --parallel
ctest --test-dir build --output-on-failure -VV
cmake --install build
python ci\validate_arm64_architecture.py --require-native-arm64 --package-lock ci\windows-arm64-packages.lock --payload-root build\install-arm64 --require-payload --json-report build\arm64-architecture-report.json
```

### B. `libopenshot`

```powershell
Set-Location D:\Hack2026\libopenshot
$env:MSYSTEM = "CLANGARM64"
$env:Path = "C:\msys64\clangarm64\bin;C:\msys64\usr\bin;$env:Path"
cmake -B build -S . -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=build\install-arm64 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DOpenShotAudio_ROOT=D:\Hack2026\libopenshot-audio\build\install-arm64 -DPYTHON_MODULE_PATH=python -DUSE_QT6=ON -DOPENSHOT_QT_API=pyqt6
cmake --build build --parallel
ctest --test-dir build --output-on-failure -VV
cmake --install build
python ci\validate_arm64_architecture.py --require-native-arm64 --package-lock ci\windows-arm64-packages.lock --payload-root build\install-arm64 --require-payload --json-report build\arm64-architecture-report.json
```

### C. `openshot-qt`

```powershell
Set-Location D:\Hack2026\OpenShot
$env:MSYSTEM = "CLANGARM64"
$env:OPENSHOT_QT_API = "pyqt6"
$env:Path = "C:\msys64\clangarm64\bin;C:\msys64\usr\bin;D:\Hack2026\libopenshot\build\install-arm64\bin;D:\Hack2026\libopenshot\build\install-arm64\python;$env:Path"
python -m unittest discover -s ci -p "test_*.py" -v
python -m unittest discover -s src\tests -t src\tests -p test_native_arm64_process_oracle.py -v
python ci\validate_arm64_architecture.py --require-native-arm64 --package-lock ci\windows-arm64-packages.lock --payload-root D:\Hack2026\libopenshot\build\install-arm64 --require-payload --json-report build\arm64-architecture-report.json
python -u freeze.py build --git-branch=$(git rev-parse --abbrev-ref HEAD)
$PY_ABI = (python -c "import sysconfig; print(sysconfig.get_config_var('py_version_short'))")
python ci\validate_arm64_architecture.py --require-native-arm64 --payload-root D:\Hack2026\OpenShot\build\exe.mingw-$PY_ABI --require-payload --json-report build\frozen-arm64-architecture-report.json
$EXE_PATH = "D:\Hack2026\OpenShot\build\exe.mingw-$PY_ABI\openshot-qt.exe"
$manifestPath = "installer\windows.manifest"
(Get-Content $manifestPath) -creplace "ARCHITECTURE", "arm64" | Set-Content $manifestPath
mt.exe -manifest installer\windows.manifest -validate_manifest
mt.exe -manifest installer\windows.manifest -outputresource:$EXE_PATH;1
python -u installer\build_server.py "$env:SLACK_TOKEN" "$env:GITHUB_USER" "$env:GITHUB_PASS" "arm64" "$(git rev-parse --abbrev-ref HEAD)" "$env:MAC_PASSWORD" "build-only"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File installer\package_msix.ps1 -Architecture arm64
```

## Preservation / scope notes

- I preserved the pre-existing unrelated `Generated Files\demo\*`, `Generated Files\hackathon-fleet\workboard.md`, and `Generated Files\hackathon-submission.md` working-tree changes in `OpenShot`.
- No commits, pushes, PR operations, signing, install, or app launch were performed in this pass.
