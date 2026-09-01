# ARM64 Readiness Status

Date: 2026-09-01  
Owner chain: `OPEN-AUDIO-001 -> OPEN-LIB-002 -> OPEN-QT-003`

## Overall verdict

**Source-chain status: READY FOR A REAL ARM64 TOOLCHAIN/RUNTIME WORKER. `openshot-qt` retains the MSIX staging fix/tests plus a hardened, isolated teardown for that test suite, and `libopenshot` now has a repaired native ARM64 runtime test pass on a locally restored CLANGARM64 toolchain.**

- `libopenshot-audio`: no reproduced source defect in this pass.
- `libopenshot`: runtime repair round reproduced and fixed repository-side native ARM64 test failures in audio-device expectations, spherical metadata lifecycle/validation, and ImageMagick buffer cleanup.
- `openshot-qt`: fixed MSIX staging to stay inside the repository worktree instead of a temp directory (`installer/package_msix.ps1`); the preparation-only test (`ci/test_package_msix_staging.py`) exercises repo-local `build\msix\installer-source` staging/cleanup without invoking production packaging or signing, and its `setUp`/`tearDown` now touch only the exact fixture paths they own instead of recursively deleting `build\msix`, with a regression test proving an unrelated pre-existing `build\msix` artifact survives the suite.
- Native host evidence is real on this machine: the shared validator reported `process_machine=UNKNOWN`, `native_machine=ARM64`, and `native ARM64 ok=True`.
- A project-local MSYS2 `CLANGARM64` toolchain was restored during runtime repair at `D:\Hack2026\openshot-msys64\msys64` (via the existing `C:\msys64` junction) and was sufficient to rebuild and rerun `libopenshot` tests.
- Re-run in this pass, on the documented `PATH` (`C:\msys64\clangarm64\bin;C:\msys64\usr\bin`) with `MSYSTEM=CLANGARM64`: `ci\validate_arm64_architecture.py --package-lock ci\windows-arm64-packages.lock` now **passes** (`RESULT: PASS`, exit 0) with **24 packages verified** and zero package-lock failures against `ci\windows-arm64-packages.lock`, in both `openshot-qt` and `libopenshot`. The previously reported 19 version drifts were a stale, superseded observation from an earlier pass and did not reflect the currently restored toolchain; that earlier wording has been corrected here. Package-lock compliance is therefore now demonstrated, but **signing, final MSIX packaging/install, and a real GUI launch remain unproven** on this worker (see "Remaining gates" below).

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

- Branch / HEAD at time of this recapture: `feature/windows-arm64-native` @ `cbdc9e821997909c5a58d247739a5fc480a40d2b` (supersedes the previously recorded `29e8bedf...`, which is now an ancestor/parent commit; this repo is developed independently of `openshot-qt` and its tip may advance further after this pass).
- Diff created in runtime repair (as of the previously recorded pass; not re-audited in this `openshot-qt`-scoped follow-up):
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
| `python3 ci\validate_arm64_architecture.py --require-native-arm64 --package-lock ci\windows-arm64-packages.lock --payload-root build --require-payload --json-report build\arm64-build-tree-report.json` (recaptured in this pass on the documented `PATH`) | 0 |

- Notes:
  - Arm64 consumer/producer chain is wired in `libopenshot\.gitlab-ci.yml:125-148`.
  - The restored native ARM64 toolchain rebuilt `libopenshot` and all tests; full CTest is now **519/519 passed** on this host.
  - `AudioDeviceManager.cpp` now accepts the actual opened supported rate and explicitly resets the singleton before the fake-device path.
  - `FFmpegWriter` now rejects no-video/post-header spherical metadata calls, defers side-data application until after the final codec-parameter copy and before header write, and keeps positive pre-open/pre-header behavior covered by regression tests.
  - `MagickUtilities.cpp` now uses straight-RGBA conversion plus allocator-matched cleanup (`cleanUpArrayBuffer`) and a lifetime test.
  - On the currently available FFmpeg 62-based restored toolchain, `ffprobe` still reports spherical mapping **presence/projection** but normalizes nonzero yaw/pitch/roll back to zero on MP4 readback; the regression tests now record that toolchain behavior as a warning while continuing to enforce metadata presence, numeric parsing, and explicit invalid-call rejection.
  - **Recaptured in this pass** (OSQT-DOC-EXITCODE-003): re-running the package-lock + payload validation above on the documented `PATH` (`C:\msys64\clangarm64\bin;C:\msys64\usr\bin`, `MSYSTEM=CLANGARM64`) against `payload-root build` now returns **exit 0**, with **72 files scanned** and **24 packages verified**, zero payload or package-lock failures (`RESULT: PASS`). The previously recorded exit 1 was stale/superseded and did not reflect the currently restored, now lock-compliant toolchain; that stale result has been corrected here rather than left standing.

Confidence: **high** for repository-side native ARM64 runtime correctness on the currently restored toolchain; **high** for package-lock compliance now that a freshly reproduced run passes with 24/24 packages verified and 72 payload files scanned; **medium** overall until the exact locked snapshot is independently re-verified by a full clean-room rebuild (signing/packaging/install/GUI are separate, still-unproven gates — see below).

### 3) `openshot-qt`

- Branch: `hackathon/windows-arm64-demo`. Parent/baseline commit verified and pushed prior to this follow-up: `6d9b8ce4aad0cc31fd6ed93901048cf27c0cd157` (supersedes the previously recorded `9294063d1...`, which is now an earlier ancestor). This document is itself updated as part of a narrow follow-up commit on top of that baseline; that follow-up commit's own SHA is intentionally not asserted here to avoid an unverifiable, self-referential claim — confirm the current tip with `git log --oneline -1` on this branch.
- Diff created in this pass:
  - `installer\package_msix.ps1`: replaced temp-directory staging with repo-local `build\msix\installer-source`.
  - `ci\test_package_msix_staging.py`: added a targeted unittest that runs the PowerShell script's preparation path and verifies repo-local staging/cleanup semantics.

- Reproduced defect and fix:
  - **Observed defect:** `installer\package_msix.ps1` staged the installer via `[System.IO.Path]::GetTempPath()`, which violates this workspace's no-temp-file rule and risks packaging failure in automation.
  - **Fix applied:** `installer\package_msix.ps1` now exposes a preparation path that stages under repo-local `build\msix\installer-source`, emits a machine-readable preparation report, preserves pre-existing `.msix` artifacts and packaging logs during `-PrepareOnly`, and still sets `ProcessorArchitecture` from `x86_64|x86|arm64` to `x64|x86|arm64`.

- Follow-up fix in this pass (OSQT-MSIX-TEARDOWN-001):
  - **Observed defect:** `ci\test_package_msix_staging.py`'s `tearDown()` recursively removed `build\msix` in its entirety (`shutil.rmtree`), which would destroy any unrelated, real packaging output left in that directory by an actual (non-test) packaging run.
  - **Fix applied:** `setUp`/`tearDown` now share an explicit `OWNED_PATHS` tuple and only ever create/remove those exact fixture paths (the report, generated template, staged installer, `installer-source` dir, stale `.msix`, stale packaging log, and the test's own fixture dir); `MSIX_DIR` is only removed afterwards if it is empty, never wiped wholesale. The previously verified path-format resolution at `ci\test_package_msix_staging.py:128` (`self.assertEqual(report["output_dir"], str(MSIX_DIR))`) is unchanged and was not weakened.
  - **Regression test added:** `test_teardown_preserves_unrelated_preexisting_build_msix_output` seeds an unrelated sentinel file/subdirectory under `build\msix`, invokes `tearDown()`, and asserts the sentinel survives byte-for-byte while owned fixture paths are removed. A separate manual reproduction (a hand-created `build\msix\manual-sentinel-real-output.msix` present before running the full suite) also confirmed survival after a full `python -m unittest discover -s ci -p test_package_msix_staging.py -v` run.

- Validation evidence:

| Command | Exit |
| --- | ---: |
| `python -m py_compile ci\validate_arm64_architecture.py ci\test_validate_arm64_architecture.py src\tests\test_native_arm64_process_oracle.py src\tests\test_release_details.py freeze.py installer\build_server.py installer\deploy.py installer\version_parser.py` | 0 |
| `python -m py_compile ci\test_package_msix_staging.py` | 0 |
| `python ci\test_validate_arm64_architecture.py` | 0 |
| `python -m unittest discover -s ci -p test_package_msix_staging.py -v` (2 tests: prepare-only staging + tearDown sentinel-preservation regression) | 0 |
| `python -m unittest discover -s src\tests -t src\tests -p test_native_arm64_process_oracle.py -v` | 0 |
| `python -m unittest discover -s src\tests -t src\tests -p test_release_details.py -v` | 0 |
| `python ci\validate_arm64_architecture.py` | 0 |
| `python ci\validate_arm64_architecture.py --require-native-arm64` | 0 |
| `python ci\validate_arm64_architecture.py --package-lock ci\windows-arm64-packages.lock --json-report build\arm64-package-lock-report.json` (documented `PATH`, `MSYSTEM=CLANGARM64`) | 0 |
| PowerShell AST parse (`[System.Management.Automation.Language.Parser]::ParseFile`) for `installer\package_msix.ps1` | 0 |
| `git diff --check -- ci\test_package_msix_staging.py "Generated Files\ARM64-READINESS-STATUS.md"` | 0 |

- Notes:
  - Application Arm64 lane is wired in `OpenShot\.gitlab-ci.yml:151-187,313-348`.
  - `freeze.py:143-150` prefers `install-arm64`.
  - `installer\build_server.py:625-666,709-958` handles Arm64 naming, artifact selection, Qt6 plugin copy, and Qt6 DLL staging.
  - `src\tests\test_native_arm64_process_oracle.py:39-89` passed 5/5 on this native Arm64 host.
  - `ci\test_package_msix_staging.py` executed `installer\package_msix.ps1 -PrepareOnly` against a fake installer/template, proved repo-local staging at `build\msix\installer-source`, verified stale staged files/report/generated-template refresh correctly, and verified pre-existing `.msix` artifacts plus packaging logs survive `-PrepareOnly`; it now also proves, via a dedicated regression test, that unrelated pre-existing `build\msix` content survives a full `tearDown()`.
  - This test covers **preparation/staging semantics only**. It does **not** claim that the full MSIX Packaging Tool run, package signing, installation, or GUI launch succeeded on this worker.
  - Package-lock validation freshly reproduced on the documented `PATH` in this pass (OSQT-DOC-LOCKDRIFT-002): **24 packages verified**, zero failures, `RESULT: PASS`, exit 0.

Confidence: **high** for repository-side packaging/source correctness available from this worker, including the corrected test-isolation behavior and the freshly reproduced, passing package-lock check; signing, final packaging/install, and GUI launch remain unproven on this worker.

## Remaining gates outside this worker

1. ~~Replace the currently restored but drifted local CLANGARM64 stack with the exact locked package snapshot required by `ci\windows-arm64-packages.lock`.~~ **Resolved for package versions in this pass:** a freshly reproduced `--package-lock ci\windows-arm64-packages.lock` run now passes with 24/24 packages verified in both `openshot-qt` and `libopenshot` on the documented `PATH`. Signing, final packaging/install, and GUI launch (gates 4-5 below) remain outstanding.
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

- This follow-up pass preserved the pre-existing, unrelated `Generated Files\demo\*`, `Generated Files\hackathon-fleet\workboard.md`, and `Generated Files\hackathon-submission.md` working-tree changes in `OpenShot`; none of that pre-existing demo content is part of this commit.
- This pass makes one narrow, non-rewriting follow-up commit on top of the previously pushed `6d9b8ce4aad0cc31fd6ed93901048cf27c0cd157` and pushes it to the existing `hackathon/windows-arm64-demo` branch. No history rewrite, amend, rebase, force-push, or PR was performed.
- Signing, final MSIX packaging/install, and a real GUI launch were **not** performed or claimed in this pass; those remain the outstanding gates listed above.
