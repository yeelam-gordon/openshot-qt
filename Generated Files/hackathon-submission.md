# Microsoft Global Hackathon 2026 - Project Submission

Event: Microsoft Global Hackathon 2026  
Form: default submission type, form `00013`, version 13  
Submission URL: https://innovation-studio.microsoft.com/events/hackathon2026/submissions/projects

Copy each answer into the matching live form field. Update the native-results
paragraph and video only after running
`Generated Files\ARM64-TEST-AND-VIDEO-PROMPT.md` on Windows Arm64.

## Step 1 - Basics

### Project Name *(required, text, max 140, field `fixed-title`)*

OpenShot Native Windows on Arm64

### Tagline *(required, text, max 160, field `fixed-tagline`)*

Bring OpenShot's complete Python, Qt, C++, audio, render, installer, and MSIX stack to native Windows Arm64 without x64 emulation.

### Description *(optional, markdown, field `fixed-description`)*

```markdown
**Problem**

OpenShot has no native Windows Arm64 release. Windows-on-Arm users must run the
x64 application through emulation even though the application spans a
performance-sensitive media stack. Upstream issue
[OpenShot/openshot-qt#5853](https://github.com/OpenShot/openshot-qt/issues/5853)
tracks the request.

**Why this is difficult**

This is not a single compiler switch. The release chain crosses three
repositories:

1. `libopenshot-audio`
2. `libopenshot` and its SWIG Python extension
3. `openshot-qt`, cx_Freeze, Inno Setup, MSIX, and signing

CPython, PyQt6/Qt6, FFmpeg, OpenCV, ImageMagick, ZeroMQ, babl, every native
library, and every packaged EXE/DLL/PYD must use one compatible Arm64 ABI.

**What we built**

- A native MSYS2 CLANGARM64 build lane for each repository.
- GitHub-hosted `windows-11-arm` presubmits for the dependency repositories.
- A shared package/version lock and fail-closed architecture validator.
- Correct native-process detection: `IsWow64Process2` must return
  `(processMachine=UNKNOWN, nativeMachine=ARM64)`.
- Independent recursive payload verification requiring PE machine `0xAA64`
  for every EXE, DLL, and PYD.
- Arm64-aware artifact discovery, cx_Freeze, Inno installer naming, MSIX
  `ProcessorArchitecture`, and signing-stage wiring.
- Post-freeze validation so a foreign binary cannot hide inside an
  Arm64-labeled package.
- A repeatable Windows Arm64 build/test guide and a pre-authored animated
  Slidecast demo pipeline.

**Pull requests**

- Audio: https://github.com/OpenShot/libopenshot-audio/pull/171
- Core library/binding: https://github.com/OpenShot/libopenshot/pull/1089
- Application/packaging: https://github.com/OpenShot/openshot-qt/pull/6094

The changes are separated in dependency order and preserve existing x64/x86
lanes. Copilot Code Review converged on current-head mirror PRs in all three
forks, with every finding fixed or explicitly dispositioned.

**Evidence today**

- Shared validator unit tests pass independently in all three repositories.
- Copilot review converged with zero open threads on all three current PR
  heads; upstream PR heads match the reviewed SHAs.
- The GitHub-hosted Windows Arm64 audio presubmit completed successfully,
  including exact package installation, native CLANGARM64 compilation, tests,
  installation, and architecture validation.
- The native-host gate correctly rejects an AMD64 host.
- Synthetic Arm64 payloads pass and AMD64 payloads fail.
- All locked MSYS2 CLANGARM64 package versions were checked against current
  package metadata.
- The pre-generated Slidecast renders successfully at 1920x1080, 30 fps, with
  synchronized narration and subtitles.

**Native-result placeholder - update after the Arm64 run**

The code and CI paths are PR-ready, and the first dependency layer now has a
successful hosted native Arm64 build. Full-chain libopenshot/OpenShot import,
render, installer, MSIX, install, launch, and hardware evidence remain pending
until the checked-in Arm64 handoff prompt is executed on a native Windows 11
Arm64 machine. Official signing and publication remain maintainer-owned.

**Definition of done**

A native Arm64 machine builds the dependency chain, passes the native-host and
recursive PE checks, launches OpenShot, completes the deterministic render,
produces an Arm64 package, and records the evidence in the final narrated demo.
Official upstream merge or signed publication is not required for the
hackathon deliverable.
```

### Keywords *(optional, tags, field `default-keywords`)*

Windows on Arm, OpenShot, Arm64, Qt6, Python, C++, FFmpeg, Open Source, CI/CD, Release Engineering

### Recruiting *(optional, roles, field `default-open-roles`)*

Windows Arm64 hardware tester; C++/Qt media build engineer; release and signing maintainer

### Executive Challenge *(required, dynamic live catalog)*

Select the closest live challenge for **Windows on Arm / Copilot+ PCs / open
source ecosystem enablement**. This catalog is populated by live search and
cannot be safely preselected from the saved form schema.

### Topic Challenges *(optional, dynamic live catalog, up to 5)*

Search for relevant topics such as Windows, Open Source, Developer
Productivity, Media, Accessibility, or Sustainability.

### Video *(required, video, field `custom-1783618131684-6wl2xx`)*

Use the final output produced on the Arm64 machine:

`Generated Files\demo\slidecast\build\final.mp4`

The checked-in source deck already renders as a 2:14 narrated draft. Before
upload, run the Arm64 handoff prompt so slide 5 and the embedded application
clip contain real native evidence instead of `PENDING`.

## Step 2 - Additional information

### Hacking On *(required, keywords, field `custom-1783618182153-76oo1g`)*

C++, Python, Qt6, CMake, MSYS2, CLANGARM64, FFmpeg, GitHub Actions, GitLab CI, Inno Setup, MSIX

### Who is this for? *(required, select, field `custom-1783618242924-abtdb0`)*

**Consumers**

### Venue *(required, select, field `custom-1783618430773-p04el3`)*

**Greater China Region - Shanghai**

### Problem or opportunity statement *(required, text, field `custom-1783618909399-eestbp`)*

OpenShot has no native Windows Arm64 release, so Copilot+ PC and other Windows-on-Arm users run a performance-sensitive video editor through x64 emulation. The gap crosses three repositories and the full Python, Qt, C++, audio, rendering, installer, and MSIX dependency chain. This project adds fail-closed native Arm64 build and packaging paths while preserving existing x64/x86 releases.

### Writing Code *(required, select, field `custom-1783618919359-iurwr8`)*

**Yes**

### If this is a feature within an existing Microsoft product or service *(optional, text, field `custom-1784047582479-jtlpdb`)*

N/A - OpenShot is an independent third-party open-source project. The work
improves the Windows-on-Arm application ecosystem.

### Briefly describe what you made and how you made it *(optional, textarea, field `custom-1784047418953-o01cra`)*

Implemented a coordinated native Windows Arm64 release path across
libopenshot-audio, libopenshot, and openshot-qt. Added CLANGARM64 CI lanes,
hosted Arm64 presubmits, exact package-version verification, corrected
IsWow64Process2 semantics, recursive PE architecture checks, and Arm64-aware
freeze, Inno, MSIX, and signing plumbing. Opened three dependency-ordered
upstream pull requests and ran repeated Copilot Code Review rounds on mirror
PRs. Added a checked-in Arm64 validation prompt and pre-generated Slidecast
deck so a native machine can build, test, record the real app, and render the
final narrated video reproducibly.

### Code repository *(optional, URL, field `custom-1784584386445-zqikfv`)*

https://github.com/OpenShot/openshot-qt/pull/6094

## Outstanding items you must complete manually

1. Select the required **Executive Challenge** from the live search catalog.
2. Optionally select up to five **Topic Challenges**.
3. Run `Generated Files\ARM64-TEST-AND-VIDEO-PROMPT.md` on native Windows
   Arm64 and replace the native-result placeholder with exact evidence.
4. Upload the final `Generated Files\demo\slidecast\build\final.mp4`.
5. Update the Code repository field if a different project/fork URL is
   preferred.
6. Click **Submit** in the authenticated browser session.
