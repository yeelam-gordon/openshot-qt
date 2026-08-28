# Windows Arm64 validation and demo prompt

Use this prompt from a **native Windows 11 Arm64 machine** with GitHub Copilot
CLI, Git, GitHub CLI, PowerShell, MSYS2, Node.js, Python, and FFmpeg available.
It validates the three fork branches, preserves raw evidence, records a real
OpenShot launch, and renders the pre-authored Slidecast package under
`Generated Files\demo\slidecast`.

## One-time checkout

```powershell
New-Item -ItemType Directory -Force C:\src\openshot-arm64 | Out-Null
Set-Location C:\src\openshot-arm64
git clone -b feature/windows-arm64-native https://github.com/yeelam-gordon/libopenshot-audio.git
git clone -b feature/windows-arm64-native https://github.com/yeelam-gordon/libopenshot.git
git clone -b hackathon/windows-arm64-demo https://github.com/yeelam-gordon/openshot-qt.git OpenShot
```

For later refreshes:

```powershell
git -C C:\src\openshot-arm64\libopenshot-audio pull --ff-only
git -C C:\src\openshot-arm64\libopenshot pull --ff-only
git -C C:\src\openshot-arm64\OpenShot pull --ff-only
```

## Run Copilot CLI

```powershell
Set-Location C:\src\openshot-arm64\OpenShot
copilot --yolo --experimental --autopilot --max-autopilot-continues 50 `
  -p "Read Generated Files\ARM64-TEST-AND-VIDEO-PROMPT.md and execute the Agent prompt section completely. Do not stop at planning."
```

## Agent prompt

You are the Windows Arm64 validation and demo owner for the OpenShot hackathon.
Work autonomously and do not claim success without command output and artifacts.

### Inputs

- `C:\src\openshot-arm64\libopenshot-audio`
- `C:\src\openshot-arm64\libopenshot`
- `C:\src\openshot-arm64\OpenShot`
- PRs:
  - https://github.com/OpenShot/libopenshot-audio/pull/171
  - https://github.com/OpenShot/libopenshot/pull/1089
  - https://github.com/OpenShot/openshot-qt/pull/6094
- Runbook: `Generated Files\windows-arm-build-test-guide.md`
- Slidecast package: `Generated Files\demo\slidecast`
- Slidecast skill:
  `C:\Users\yeelam\OneDrive - Microsoft\Documents\.copilot\skills\slidecast\SKILL.md`

### Rules

1. Confirm the host is native Windows Arm64 before building:

   ```powershell
   python ci\validate_arm64_architecture.py --require-native-arm64
   ```

   The required result is `process_machine=UNKNOWN`,
   `native_machine=ARM64`, and exit code 0. Stop if this fails.
2. Create `Generated Files\arm64-evidence\<UTC timestamp>\` and save every
   command, stdout/stderr, exit code, package version, binary inventory,
   screenshot, and video there.
3. Never weaken a test, disable a feature, substitute x64 binaries, or treat
   emulation as native evidence.
4. Follow the repositories in dependency order: audio, library/binding,
   application/package.
5. Do not use signing credentials unless the human explicitly confirms they
   are test credentials intended for this run. Unsigned ZIP/Inno/MSIX evidence
   is sufficient for the hackathon.
6. Update demo statements from `PENDING` only after the corresponding evidence
   exists. If a gate fails, present the failure and next action honestly.

### Environment

Install/update MSYS2, then install the concrete packages listed in
`ci\windows-arm64-packages.lock`. Verify `pacman -Q` matches every locked
version. The lock's hash column is intentionally unverified until maintainers
publish a signed snapshot; record this as a release limitation, not a local
build failure.

Use the CLANGARM64 shell and prefix. Set:

```powershell
$env:MSYSTEM = "CLANGARM64"
$env:Path = "C:\msys64\clangarm64\bin;C:\msys64\usr\bin;$env:Path"
$env:OPENSHOT_QT_API = "pyqt6"
```

### Build and test

Execute the detailed G0-G13 runbook, adapting only private GitLab/signing steps
to local directories. At minimum:

1. Build/install `libopenshot-audio` to `build\install-arm64`; run CTest and:

   ```powershell
   python ci\validate_arm64_architecture.py --require-native-arm64 `
     --payload-root build\install-arm64 --require-payload `
     --json-report build\arm64-architecture-report.json
   ```

2. Build/install `libopenshot` against that exact audio install with
   `USE_QT6=ON`; build and run Catch2 tests; validate every installed PE.
3. Copy the exact libopenshot Python/DLL artifacts into OpenShot's
   `build\install-arm64`, run the targeted Python tests, freeze the application,
   and validate the complete frozen directory.
4. Produce an unsigned Arm64 installer and MSIX if local release tooling is
   available. Verify installer/MSIX metadata says `arm64` and recursively scan
   extracted payloads.
5. Install or launch from the frozen directory with an isolated profile.
   Verify `import openshot`, PyQt6 startup, `QWidget` creation, normal OpenShot
   launch, and a deterministic small export. Preserve both OpenShot logs.

### Capture the real application

After a successful native launch, capture 15-25 seconds showing:

- Task Manager/details or the validator output proving native Arm64.
- OpenShot launching.
- Importing/opening the tiny test project.
- Starting and completing the deterministic export.

Use FFmpeg desktop capture if available:

```powershell
ffmpeg -y -f gdigrab -framerate 30 -i desktop -t 20 `
  -c:v libx264 -preset veryfast -pix_fmt yuv420p `
  "Generated Files\demo\slidecast\assets\openshot-arm64-demo.mp4"
```

Crop sensitive windows before recording and show no credentials, tokens, email,
or unrelated desktop content.

### Finalize the Slidecast

1. Read the Slidecast skill file above.
2. Update `Generated Files\demo\slidecast\deck.html` slide `s5` and the matching
   `storyboard.json` narration with exact native results and measured evidence.
3. If the application recording exists, set slide `s5`'s `embeddedVideo` to:

   ```json
   {
     "src": "assets/openshot-arm64-demo.mp4",
     "mode": "box",
     "box": {"x": 930, "y": 245, "w": 850, "h": 478},
     "startStepId": "s5-2",
     "pauseDeck": true,
     "audio": "mute"
   }
   ```

4. Install only missing Slidecast dependencies:

   ```powershell
   $slidecastRoot = "C:\Users\yeelam\OneDrive - Microsoft\Documents\.copilot\skills\slidecast"
   pip install -r "$slidecastRoot\scripts\requirements.txt"
   npm --prefix "$slidecastRoot\scripts" install
   npx --prefix "$slidecastRoot\scripts" playwright install chromium
   ```

5. Render:

   ```powershell
   Set-Location "C:\src\openshot-arm64\OpenShot\Generated Files\demo\slidecast"
   python "$slidecastRoot\scripts\build.py" `
     --storyboard storyboard.json --deck deck.html `
     --package-root . --out build
   ```

6. Verify `build\final.mp4` with `ffprobe`, sample frames at every slide
   midpoint, confirm subtitles do not overlap slide content, and confirm the
   recording is visible and correctly cropped.
7. Copy the final MP4, subtitle file, resolved manifest, input audit manifest,
   and an evidence index into the timestamped evidence directory.

### Finish

Update `Generated Files\windows-arm-build-test-guide.md`,
`Generated Files\hackathon-fleet\workboard.md`, and
`Generated Files\demo\impact-evidence.md` with exact results. Commit evidence
and demo-source updates only to `hackathon/windows-arm64-demo`; do not push
machine-generated build trees, dependency caches, secrets, or large raw
captures. Push the branch and report:

- native build/test/package verdict;
- exact failed gates, if any;
- artifact paths and SHA-256 values;
- final MP4 path and duration;
- PR links and current review status.
