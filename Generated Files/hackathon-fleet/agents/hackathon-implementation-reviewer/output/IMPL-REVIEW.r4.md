# IMPL-REVIEW r4

Final independent review of the three-repository Windows Arm64 implementation
after the manager's initial r3 review.

## Findings and dispositions

| ID | Severity | Finding | Disposition |
| --- | --- | --- | --- |
| IMPL-010 | high | The shared validator reported the native-process oracle but did not fail CI when the runner was x64 or emulated. | Resolved: added `--require-native-arm64`; every GitLab and GitHub Arm64 build invocation now requires `(UNKNOWN, ARM64)`. Added passing accept/reject unit tests. |
| IMPL-011 | high | GitHub Arm64 presubmits were permanently disabled and incorrectly claimed hosted Windows Arm64 runners were unavailable. | Resolved: both dependency repos now use `windows-11-arm` with `msys2/setup-msys2@v2` and `msystem: CLANGARM64`. Jobs remain supplemental and non-release. |
| IMPL-012 | high | The proposed CLANGARM64 Catch2 package does not exist, so libopenshot tests would be silently disabled. | Resolved: Catch2 v3.8.1 is checked out, built, and installed before configuring libopenshot; `Catch2_DIR` is explicit. |
| IMPL-013 | high | `freeze.py` preferred `install-arm64` whenever that directory existed, allowing a stale Arm64 tree to contaminate x64/x86 builds. | Resolved: selection now prefers the active `MSYSTEM`, preserving the historical x64-to-x86 fallback when unset. |
| IMPL-014 | high | The MSIX Arm64 job selected an Arm64-named installer but did not set the external template's `ProcessorArchitecture`. | Resolved: Arm64 packaging now requires and sets `ProcessorArchitecture="arm64"` in the generated working template. |
| IMPL-015 | high | `build_server.py` read version metadata only from `install-x64`/`install-x86`, causing a clean Arm64 job to fail before packaging. | Resolved: artifact metadata selection now prefers `install-arm64` for the Arm64 invocation. |
| IMPL-016 | medium | The shared lock omitted native dependencies, pinned the wrong Qt base release, and treated a package group/virtual package as versioned packages. | Resolved: all 24 concrete package entries exist and match current CLANGARM64 versions; all three lock copies are byte-identical. |
| IMPL-017 | medium | The OpenShot job validated upstream dependency artifacts but not the frozen application tree. | Resolved: a second mandatory native/PE scan runs after `freeze.py` and publishes its own report. |
| IMPL-018 | medium | Required Qt6 plugin directories and runtime DLLs were skipped silently when absent. | Resolved: Arm64 staging now requires imageformats, platforms, iconengines, multimedia, and core GUI/widget/SVG/multimedia DLLs, failing explicitly when missing. |

## Verification

- New oracle tests: 5/5 pass.
- Existing release-detail tests: 3/3 pass.
- Broader Python suite: 57 tests, 25 pre-existing errors caused by absent Qt
  bindings/native `openshot`; no new test fails.
- Native-required validator correctly rejects this AMD64 host with exit 1.
- Synthetic Arm64 PE passes; synthetic AMD64 PE fails.
- All 24 locked package names and versions match current MSYS2 CLANGARM64
  package metadata.
- Shared validator and lock are byte-identical across all three repositories.
- All edited CI YAML parses; the MSIX PowerShell script passes AST parsing;
  all changed Python files compile.
- `git diff --check` passes in all three repositories.

## Verdict

**PASS.** Zero open critical/high/medium implementation findings remain.
Native build, package, install, signing, and hardware execution remain
unverified because the production GitLab Arm64 runners, signed package
snapshot, credentials, and physical devices are external to this workspace.

confidence: high
The verdict is supported by direct tests, package metadata checks, syntax
validation, an independent code review, and clean three-repository diffs.
