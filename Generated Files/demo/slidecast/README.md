# OpenShot Windows Arm64 Slidecast

The source package was rendered locally before check-in:

- 1920 x 1080
- 30 fps
- 134.47 seconds
- H.264 video and AAC audio
- burned synchronized subtitles
- six representative frames visually inspected

The generated `build/` directory is intentionally ignored. Rebuild it with:

```powershell
$slidecastRoot = "C:\Users\yeelam\OneDrive - Microsoft\Documents\.copilot\skills\slidecast"
python "$slidecastRoot\scripts\build.py" `
  --storyboard storyboard.json --deck deck.html `
  --package-root . --out build
```

Before the final hackathon render, execute
`..\..\ARM64-TEST-AND-VIDEO-PROMPT.md` on a native Windows Arm64 machine,
replace slide 5's pending evidence, and embed the recorded OpenShot clip.
