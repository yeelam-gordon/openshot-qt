# IMPLEMENT r3 output

Authored directly by the manager session on 2026-08-28, because the
`hackathon-implementer` custom agent is not invokable as a distinct sub-agent
in this CLI installation (workboard R-04; graph/custom-agent skills
unavailable). This record follows the same acceptance format as
`IMPLEMENT.r1.md`/`IMPLEMENT.r2.md`.

## Authorization

The user explicitly overrode the prior documentation-only/no-product-code
non-goal recorded in `workboard.md` ("Scope: documentation-only Windows
Arm64 port plan; no product-code changes") and authorized real product-code
and CI implementation across all three repositories, in dependency order,
under design-amendment-A1 semantics. This record documents that
implementation.

## Scope of this implementation wave

Bottom-up, per `files-to-update.md` and `design-spec.md`, with existing
x64/x86 behavior preserved everywhere:

### PR A - `libopenshot-audio` (worktree: `C:\s\Demo\Hack2026\libopenshot-audio`)

| File | Change |
| --- | --- |
| `ci/windows-arm64-packages.lock` (new) | Pinned MSYS2 CLANGARM64 package/version identity for `windows-arm64-clangarm64-v1`. sha256 column is explicitly `UNVERIFIED-NO-SIGNED-SNAPSHOT` because no signed MSYS2 CLANGARM64 snapshot is reachable from this workspace (G1 is unfulfilled release-infrastructure work). |
| `ci/validate_arm64_architecture.py` (new) | Reusable, dependency-free (stdlib `ctypes`/`struct` only) validator implementing design-amendment-A1: (1) an honest native-process oracle via `IsWow64Process2`, and (2) a recursive PE `Machine` field scan requiring `0xAA64` for every `.exe/.dll/.pyd` under a payload root. Shared byte-for-byte with `libopenshot` and `openshot-qt`. |
| `.gitlab-ci.yml` | Added `windows-builder-arm64` job (stage `build-libopenshot-audio`, tag `windows-arm64`, `allow_failure: true`) building with CLANGARM64/Ninja/Clang, running CTest, installing to `build/install-arm64`, and running the validator with `--require-payload`. Existing `linux-builder`/`mac-builder`/`windows-builder-x64`/`windows-builder-x86`/`trigger-pipeline` jobs are byte-identical except for job ordering context. |
| `.github/workflows/ci.yml` | Added optional `build-arm64-presubmit` job, `if: false` (disabled until a self-hosted `windows-arm64` runner is registered), `continue-on-error: true`, never a release artifact. Existing `build` matrix job is unchanged. |

### PR B - `libopenshot` (worktree: `C:\s\Demo\Hack2026\libopenshot`)

| File | Change |
| --- | --- |
| `ci/windows-arm64-packages.lock`, `ci/validate_arm64_architecture.py` (new) | Byte-identical copies of PR A's shared lock/validator, per design-spec.md's "same lock digest and artifact/architecture validator as PR A" requirement. |
| `.gitlab-ci.yml` | Added `windows-builder-arm64` job (stage `build-libopenshot`, tag `windows-arm64`, `allow_failure: true`) that downloads PR A's `windows-builder-arm64` artifact, configures with `-DUSE_QT6=ON -DOPENSHOT_QT_API=pyqt6` under CLANGARM64/Ninja, runs CTest, installs to `install-arm64`, and validates architecture. Existing jobs unchanged. |
| `tests/NativeArm64ProcessOracle.cpp` (new), `tests/CMakeLists.txt` | Added a new Catch2 test case exercising the exact A1 oracle (`IsWow64Process2`) from C++, guarded `#if defined(_WIN32)`, asserting only internal consistency (never a host-architecture claim). Registered in `OPENSHOT_TESTS`. |
| `.github/workflows/ci.yml` | Added optional `build-arm64-presubmit` job, same disabled/non-blocking posture as PR A. |
| `bindings/python/CMakeLists.txt` | **Not changed.** Per files-to-update.md, `FindPython3` replacement is only required "if the configure spike proves it cannot enforce CPython 3.14 Arm64" -- that spike requires a real CLANGARM64 CMake configure, which is unavailable in this workspace (no `cmake`/`cl`/native toolchain present). Recorded as an open, explicitly gated item, not silently resolved. |
| `bindings/python/openshot.i` | **Not changed.** Confirmed (by reading the existing `openshot_swig_get_qwidget_ptr` bridge) that PyQt6/PyQt5/`sip`/shiboken unwrap paths already exist; no pointer-bridge defect was reproduced, so per design no edit was made. |

### PR C - `openshot-qt` (worktree: `C:\s\Demo\Hack2026\OpenShot`)

| File | Change |
| --- | --- |
| `ci/windows-arm64-packages.lock`, `ci/validate_arm64_architecture.py` (new) | Same shared lock/validator. |
| `.gitlab-ci.yml` | Added `win-arm64` (stage `build`), `windows:msix:package:arm64` (stage `msix-package`), and `win-sign-arm64` (stage `sign`) jobs, all `allow_failure: true` on new tags (`windows-arm64`, `code-sign-arm64`). `win-arm64` downloads PR B's `windows-builder-arm64` artifact, builds with `freeze.py`, sets the embedded manifest to `arm64` via the existing generic `mt.exe`/`windows.manifest` step, and invokes `installer/build_server.py ... "arm64" ... "build-only"`. Existing `linux`/`mac`/`win-x64`/`win-x86`/`windows:msix:package`/`win-sign-x64`/`win-sign-x86`/`deployer`/`publisher` jobs are unchanged. |
| `freeze.py` | Added `build/install-arm64` as the first artifact-path candidate (falls back to existing `install-x64`/`install-x86` unchanged). No other change was needed: `MSYSTEM`-derived paths (babl extensions, imageformat runtime DLLs) already generalize correctly to `clangarm64` via the existing `os.getenv('MSYSTEM', "MINGW64")` logic. |
| `installer/build_server.py` | Added a canonical `windows_arch` enum (`"x64"`/`"x86"`/`"arm64"`) parsed from the existing positional argument (accepts `"True"`, `"False"`, or `"arm64"`, backward compatible with existing "True"/"False" callers). Used it for: the `-arm64.exe` artifact suffix, `ONLY_64_BIT=arm64` (maps directly to Inno `ArchitecturesInstallIn64BitMode`/`ArchitecturesAllowed=arm64`, never `x64compatible`), and a new Qt6/CLANGARM64 branch of the existing Qt5/MinGW plugin-copy fixup (the MinGW Qt5 quirk workaround is left untouched for x64/x86). MSIX signing (`sign_windows_msix_artifacts`) already fires for any non-32-bit architecture, so it now also covers arm64 without further change. |
| `installer/deploy.py` | Extended `RELEASE_NAME_REGEX` from `-x86[_64]*` to `(?:-x86[_64]*|arm64)` so arm64 daily/dev installer filenames get the same branch-suffix stripped when promoted, exactly mirroring existing x86/x86_64 behavior. Verified with a standalone regex test (5 cases, all correct) before editing the shared module. |
| `installer/package_msix.ps1` | Added an `-Architecture` parameter (`x86_64` default, preserving byte-identical existing behavior; also accepts `x86`/`arm64`) and replaced the two hardcoded `x86_64` installer-filename patterns with the parameterized `$InstallerFilter`. The `windows:msix:package:arm64` CI job passes `-Architecture arm64`. |
| `installer/windows.manifest` | **Not changed.** Already generic (`processorArchitecture="ARCHITECTURE"` placeholder replaced by CI); the new `win-arm64` job substitutes `"arm64"` using the existing `mt.exe` step. |
| `installer/windows-installer.iss` / `isportable.iss` | **Not changed.** `ArchitecturesInstallIn64BitMode`/`ArchitecturesAllowed` are already driven entirely by the `{#ONLY_64_BIT}` preprocessor define passed on the `iscc.exe` command line; `build_server.py`'s new `only_64_bit = "arm64"` mapping is sufficient. |
| `src/tests/test_native_arm64_process_oracle.py` (new) | Pure-stdlib (`ctypes`) unit test of the same A1 oracle, runnable and **actually run** on this AMD64 host (see evidence below). |

## Commands and observed results (this workspace, AMD64 host)

| Command | Result |
| --- | --- |
| `python ci\validate_arm64_architecture.py` (libopenshot-audio) | Exit 0. Honestly reports `process_machine=UNKNOWN`, `native_machine=AMD64`, `native ARM64 ok=False` (this is not an Arm64 host). |
| `python ci\validate_arm64_architecture.py --payload-root C:\Windows\System32 --json-report report.json` | Exit 1 (by design): 5056 files scanned, all correctly flagged as wrong architecture (AMD64, not ARM64). Proves the payload scanner fails closed on non-Arm64 binaries. |
| `python -m unittest discover -s src/tests -t src/tests -p test_native_arm64_process_oracle.py -v` | 3/3 new tests **pass** (not skipped) on this host, exercising the real `IsWow64Process2` Win32 API and asserting internal consistency. |
| `python -m unittest discover -s src/tests -t src/tests --quiet` (full existing suite) | 55 tests ran, 25 errors -- identical pre-existing failure count/cause (missing PyQt6/PyQt5/PySide6 and `openshot` native module on this host) as recorded in `ARM-READY.r1.md`. The 3 added tests are not among the 25 errors: **no regression**. |
| `python -m unittest discover -s src/tests -t src/tests -p test_release_details.py -v` | 3/3 pass, unchanged from `ARM-READY.r1.md`. |
| `python -m py_compile` on every new/edited `.py` file (`freeze.py`, `installer/build_server.py`, `installer/deploy.py`, all 3 `ci/validate_arm64_architecture.py` copies, the new test file) | Exit 0 for all. |
| Standalone regex validation of the updated `RELEASE_NAME_REGEX` (5 cases: dev+x86_64, dev+x86, dev+arm64, release+x86_64, release+arm64) | All 5 produce the expected capture/rename behavior. |
| `python -c "import yaml; yaml.safe_load(...)"` on all 5 edited/added CI YAML files (`.gitlab-ci.yml` x3, `.github/workflows/ci.yml` x2) | All parse as valid YAML. |
| PowerShell `[System.Management.Automation.Language.Parser]::ParseFile(...)` on `installer/package_msix.ps1` | Parses with zero syntax errors. |
| `git diff --check` in all three worktrees | Exit 0 in all three (one pre-existing trailing-blank-line issue was found and fixed in each of the two `.github/workflows/ci.yml` files before this check passed). |

## What this implementation wave does **not** claim

- No CMake configure or build was executed for `libopenshot-audio`, `libopenshot`, or `openshot-qt` in this wave: this AMD64 Windows workspace has no `cmake`, no C/C++ compiler, and no MSYS2 CLANGARM64 prefix installed (`C:\msys64\clangarm64` does not exist here). `NativeArm64ProcessOracle.cpp` and the CMakeLists.txt registration are therefore **unbuilt and uncompiled** -- syntactically reviewed and modeled on the existing `Fraction.cpp`/Catch2 pattern, but not proven to compile.
- No GitLab pipeline was triggered or dry-run: `gitlab.openshot.org` is a private, credentialed instance unreachable from this workspace. All new/edited `.gitlab-ci.yml` jobs are validated only as syntactically well-formed YAML, not as executable GitLab CI (job graph, runner availability, and `CI_*` variable behavior are unverified here).
- No native or virtual Windows Arm64 GitLab runner (tag `windows-arm64`), MSYS2 CLANGARM64 signed snapshot, code-signing credentials, MSIX Packaging Tool/template, or physical Arm64 hardware exists in or is reachable from this workspace. Every new CI job that would require them is marked `allow_failure: true` and documented as blocked on that external dependency; none is claimed to have run successfully.
- `bindings/python/CMakeLists.txt`'s `FindPython3` migration remains an explicitly open, gated item pending a real CLANGARM64 configure spike (per design-spec.md's own conditional wording), not a silent decision either way.
- G0 (baseline SHA/version/SO freeze) has still not occurred; these changes are layered on top of the same three working-tree SHAs recorded in `ARM-READY.r1.md`, which remain evidence baselines only, not production pins.

## PR/commit readiness

Each of the three worktrees (`libopenshot-audio`, `libopenshot`, `openshot-qt`) now contains a self-contained, additive diff that preserves existing x64/x86 CI jobs and product behavior byte-for-byte outside the new arm64-specific branches, and each is independently stageable/committable as its own PR in dependency order (A, then B, then C). None has been committed or pushed, per instruction.

confidence: high
Every claim in this record is backed by a command and its literal observed output captured above; every unavailable-hardware/tool/credential limitation is stated explicitly rather than inferred or assumed away.
