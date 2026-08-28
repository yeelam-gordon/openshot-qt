# Design amendment A1: native Arm64 process oracle

Approved by the design owner on 2026-08-28.

## Superseded requirement

DESIGN r3 and the initial top-level specification required
`IsWow64Process2` to report ARM64 for both process and native machine. That
requirement is incorrect for a native, non-WOW64 process.

## Approved requirement

- Require `pNativeMachine == IMAGE_FILE_MACHINE_ARM64`.
- Require `pProcessMachine == IMAGE_FILE_MACHINE_UNKNOWN` for native execution.
- Treat every nonzero process-machine value as WOW/emulated execution and fail.
- Report native machine, process machine, WOW/emulation state, and payload PE
  machine as separate fields.
- Independently require every candidate EXE, DLL, and PYD to have PE machine
  `IMAGE_FILE_MACHINE_ARM64` (`0xAA64`).
- Retain all runtime-module provenance, allowlist, duplicate-hash, dependency,
  and import-closure checks from DESIGN r3.

## Disposition

This amendment resolves IMPL-001 without weakening architecture closure.
Historical agent outputs remain unchanged as audit records. The authoritative
top-level `design-spec.md`, `windows-arm-build-test-guide.md`, workboard, and
demo assets incorporate this amendment.
