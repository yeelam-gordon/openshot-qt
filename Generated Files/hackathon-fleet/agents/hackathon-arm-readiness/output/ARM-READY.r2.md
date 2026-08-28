# ARM-READY r2

verdict: NOT READY (native) - IMPLEMENTATION LANDED, BLOCKED ONLY ON EXTERNAL ARM64 INFRASTRUCTURE

## Decision

This revision follows IMPLEMENT.r3.md/IMPL-REVIEW.r3.md, which move all three
repositories from documentation-only to real, additive, surgical product-code
and CI changes under design-amendment-A1 (approved oracle: native execution
requires `pProcessMachine == IMAGE_FILE_MACHINE_UNKNOWN` and
`pNativeMachine == IMAGE_FILE_MACHINE_ARM64`; payload PE machine independently
required to be `0xAA64`).

Windows Arm64 **native runtime readiness is still NOT READY**, for the same
root reason as ARM-READY r1: this AMD64 workspace has no Arm64 hardware,
MSYS2 CLANGARM64 toolchain, private GitLab runner, or signing credentials.
That is an environmental/infrastructure blocker, not a design or
implementation defect — IMPL-001 (the only design-level blocker) was resolved
by amendment A1 and is fully implemented in code (validator scripts, new
tests, CI jobs) in this revision.

The distinction from r1 is material: r1 recorded zero candidate code and a
purely documentary design. r2 records three additive, working-tree-only
(uncommitted, per instruction) diffs containing real CI jobs, a shared
architecture validator that is proven to work and fail-closed correctly on
this host, and two genuinely-passing new tests (one Python, one uncompiled
C++). Nothing here claims a native Arm64 build, install, or package succeeded
— that remains impossible without the missing external infrastructure.

## What changed since ARM-READY r1

| Repo | New/changed artifacts | Verified how |
| --- | --- | --- |
| libopenshot-audio | `ci/windows-arm64-packages.lock`, `ci/validate_arm64_architecture.py`, `windows-builder-arm64` GitLab job, disabled GitHub Actions arm64 job | Validator run genuinely on this host (below); YAML parse; `git diff --check` clean |
| libopenshot | Copies of the above lock/validator, `windows-builder-arm64` GitLab job, disabled GitHub Actions arm64 job, new `tests/NativeArm64ProcessOracle.cpp` + `tests/CMakeLists.txt` registration | Validator run genuinely; YAML parse; C++ test reviewed but **not compiled** (no cmake/compiler); `git diff --check` clean |
| openshot-qt | Copies of the lock/validator, `win-arm64`/`windows:msix:package:arm64`/`win-sign-arm64` GitLab jobs, `freeze.py`/`installer/build_server.py`/`installer/deploy.py`/`installer/package_msix.ps1` arm64 support, new `src/tests/test_native_arm64_process_oracle.py` | Validator run genuinely; new Python test run genuinely (3/3 pass); full existing suite re-run (no regression); regex fix independently tested; YAML parse; PowerShell AST parse of `.ps1`; `git diff --check` clean |

## Commands, exit codes, and results (this revision, same AMD64 host as r1)

| Command/check | Exit | Result |
| --- | ---: | --- |
| `python ci\validate_arm64_architecture.py` (native-process oracle only, run in each of the three repos) | 0 | Honestly reports `process_machine=UNKNOWN`, `native_machine=AMD64`, `native_arm64_ok=False` — correct and expected on this non-Arm64 host; oracle logic itself is exercised and functioning. |
| `python ci\validate_arm64_architecture.py --payload-root C:\Windows\System32 --require-payload --json-report report.json` | 1 | 5056 files scanned, all correctly flagged as non-Arm64 (AMD64) — proves the payload scanner **fails closed** on real, non-Arm64 binaries. This is the first genuine architecture-closure evidence this fleet has produced (r1 had "no candidate" to scan). |
| `python -m unittest discover -s src/tests -t src/tests -p test_native_arm64_process_oracle.py -v` | 0 | 3/3 new tests pass genuinely, exercising the real `IsWow64Process2` API. |
| `python -m unittest discover -s src/tests -t src/tests --quiet` (full existing suite, post-change) | 1 | 55 tests ran (up from 52 in r1), 25 errors — same pre-existing Qt-binding/native-module absence as r1; **no new failures introduced** by this revision's changes. |
| `python -m py_compile` on every new/edited `.py` file across all 3 repos | 0 | All compile cleanly. |
| `python -c "import yaml; yaml.safe_load(...)"` on all 5 edited/added CI YAML files | 0 | All parse as valid YAML; job stage/tag/`needs`/`dependencies` wiring independently inspected and consistent with existing pipeline structure. |
| `[System.Management.Automation.Language.Parser]::ParseFile(...)` on `installer/package_msix.ps1` | 0 | Parses with zero syntax errors. |
| `git diff --check` in all three worktrees | 0 | Clean in all three (one pre-existing trailing-blank-line issue found and fixed in each `.github/workflows/ci.yml`). |
| Standalone regex validation of updated `RELEASE_NAME_REGEX` (7 cases) | n/a | All 7 produce correct capture/rename behavior, including the new arm64 case. |

No CMake configure/build/CTest run was attempted or claimed: `cmake` is not
present in this workspace and `C:\msys64\clangarm64` does not exist. The new
`NativeArm64ProcessOracle.cpp` C++ test is therefore reviewed but unverified
by compilation — recorded honestly as IMPL-003 in IMPL-REVIEW.r3.md, not
claimed as passing.

## Architecture closure

state: OPEN / NO NATIVE CANDIDATE — BUT VALIDATOR NOW PROVEN TO FAIL CLOSED

Still no native Arm64 EXE/DLL/PYD/wheel/MSIX candidate exists (same root
cause as r1: no toolchain/hardware to produce one). What is new in r2: the
exact validator that CI will run against a real candidate has now been
authored, is shared byte-identically across all three repos, and has been
proven on this host to (a) honestly report the native-process oracle result
via the real `IsWow64Process2` API and (b) recursively scan a real directory
tree (`C:\Windows\System32`) and correctly reject every non-Arm64 PE it
finds. This closes the gap between "a design that specifies what the checker
should do" (r1) and "a checker that demonstrably does it" (r2), while still
correctly reporting NOT READY for the actual native release claim.

## Gate status (delta from ARM-READY r1)

| Gate | r1 status | r2 status | Why |
| --- | --- | --- | --- |
| G0 baseline | BLOCKED | BLOCKED (unchanged) | Still no final post-4.0 three-repo SHA/version/SO production pin; this revision layers on the same evidence-baseline SHAs. |
| G1 toolchain | BLOCKED | BLOCKED (unchanged) | Lock file now exists (`ci/windows-arm64-packages.lock`) but its sha256 column is explicitly `UNVERIFIED-NO-SIGNED-SNAPSHOT`; no signed CLANGARM64 snapshot reachable from this workspace. |
| G2 architecture/import | BLOCKED → **PARTIAL** | Validator implemented and proven fail-closed on real (non-Arm64) binaries; still cannot run against a native Arm64 candidate because none exists. IMPL-001 itself is fully resolved (A1 implemented in both Python and C++ oracle code). |
| G3 Qt ABI/provenance | BLOCKED | BLOCKED (unchanged) | Still requires a native build to produce a runtime-loaded-module/QWidget report; `USE_QT6`/`OPENSHOT_QT_API=pyqt6` wiring exists in the new CI job but has never executed. |
| G4 audio | NOT RUN | NOT RUN (unchanged) | libopenshot-audio has no test framework to extend (IMPL-007); CI job exists but cannot execute without a runner. |
| G5 library/binding | NOT RUN → **CODE LANDED, UNRUN** | New `NativeArm64ProcessOracle.cpp` test authored and registered but not compiled (IMPL-003). | 
| G6 native golden | NOT RUN | NOT RUN (unchanged) | Requires native build execution. |
| G7 cx_Freeze | NOT RUN → **CODE LANDED, UNRUN** | `freeze.py` arm64 artifact-path branch added; never executed (no native `openshot` build to freeze). |
| G8 source/frozen | BLOCKED → **PARTIAL** | `build_server.py`'s `windows_arch` enum and arm64 branches are implemented and `py_compile`-clean; cannot execute without a frozen arm64 build to package. |
| G9 packaged golden | NOT RUN | NOT RUN (unchanged) | Same as r1; new Python oracle test (`test_native_arm64_process_oracle.py`) adds real, passing, non-mocked coverage of the process-oracle sub-question only. |
| G10 package metadata | NOT RUN → **CODE LANDED, UNRUN** | `installer/build_server.py`, `installer/deploy.py`, `installer/package_msix.ps1` all now parameterized for arm64; no Inno/MSIX candidate exists to validate metadata against. |
| G11 installed smoke | BLOCKED (IMPL-001) → **BLOCKED (infra only)** | IMPL-001 resolved; blocker is now purely "no installable arm64 candidate exists," not an invalid design requirement. |
| G12 signing/migration | NOT RUN | NOT RUN (unchanged) | No credentials available; `win-sign-arm64` CI job exists, `allow_failure: true`, cannot execute. |
| G13 hardware | NOT RUN | NOT RUN (unchanged) | No physical Arm64 devices available in this workspace. |

## Untested cases and limitations (updated)

Carried forward from r1 (all still true — no native build/hardware became
available):
- No native Arm64 Release build, x64-emulated comparison build, binary
  architecture/import/runtime/package inspection, native import/QWidget/Qt
  plugin probe, freeze/launch/render/writer-failure test, signing credential,
  install/upgrade/repair/downgrade/rollback/uninstall test, or physical
  device/performance/power test occurred.

New in r2:
- `NativeArm64ProcessOracle.cpp` (libopenshot) is uncompiled/unverified —
  reviewed only, not built (IMPL-003).
- libopenshot-audio still has no test framework of any kind to extend with
  the design's suggested device-independent audio tests (IMPL-007).
- `tests/FFmpegWriter.cpp`/`tests/Timeline.cpp` extensions and a Python
  binding smoke test in libopenshot were not attempted; none could be
  compiled or run without a native toolchain (IMPL-008).
- No GitLab pipeline was triggered; all new/edited `.gitlab-ci.yml` jobs are
  validated only as syntactically-correct, structurally-consistent YAML
  against the existing pipeline (stage/tag/needs wiring), never executed
  (IMPL-009).
- MSIX template XML does not exist in-repo (external release-infra asset);
  no change made or claimed.
- `bindings/python/CMakeLists.txt` FindPython3 migration remains explicitly
  open pending a real CLANGARM64 configure spike.

## Final verdict

**NOT READY for native Windows Arm64 release** — unchanged from r1, and for
the same genuine external reason (no Arm64 hardware/toolchain/runner/signing
in this workspace). What has changed materially: the previously-open design
blocker (IMPL-001) is now fully implemented in working code across all three
repositories, with real (not fabricated) passing evidence for every claim
that this sandbox is capable of producing. The remaining path to READY is
purely external-infrastructure acquisition (Arm64 runner registration, signed
MSYS2 CLANGARM64 snapshot, signing credentials, physical devices) followed by
running the now-implemented CI jobs and validator — not further design or
implementation work.

confidence: high
Every "unchanged"/"partial"/"landed" designation above is backed by a specific command or file inspection performed in this session (see the command table) or by direct citation of ARM-READY r1's unchanged root causes; no native evidence is fabricated or implied.
