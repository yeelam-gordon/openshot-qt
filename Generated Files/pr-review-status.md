# Pull request and review status

Verified 2026-08-28.

| Layer | Upstream PR | Reviewed head | Mirror review | Convergence |
| --- | --- | --- | --- | --- |
| libopenshot-audio | https://github.com/OpenShot/libopenshot-audio/pull/171 | `d572b7fdd9b25dad705336a4424ac814ae725971` | https://github.com/yeelam-gordon/libopenshot-audio/pull/1 | `true`; 0 open threads |
| libopenshot | https://github.com/OpenShot/libopenshot/pull/1089 | `29e8bedfbdb600792b114676bb42681b35876adc` | https://github.com/yeelam-gordon/libopenshot/pull/1 | round-cap hand-off; 0 open threads |
| openshot-qt | https://github.com/OpenShot/openshot-qt/pull/6094 | `ea204fac7bc48450f471567fb9cf1f379ad25768` | https://github.com/yeelam-gordon/openshot-qt/pull/1 | `true`; 0 open threads |

The upstream PR heads match these SHAs. Audio and application reached scripted
Copilot convergence. Library review reached the round-cap circuit breaker
after resolving all open threads and proving the native build; further
dependency-runtime work was explicitly handed off rather than expanding scope.

## Native CI evidence

- Audio hosted Arm64 workflow:
  https://github.com/yeelam-gordon/libopenshot-audio/actions/runs/33169651801
- Attempt 2 result: **success**.
- Native `windows-11-arm` runner installed the exact CLANGARM64 package specs,
  configured and built OpenShotAudio with Clang 22.1.8, ran tests, installed
  the library, and passed native-host/payload architecture validation.
- The initial attempt exposed the missing optional ASIO SDK include. The fix
  defines and exports `JUCE_ASIO=0` when `ASIO::SDK` is unavailable, retaining
  WASAPI support without claiming ASIO support.

- Library hosted Arm64 workflows compiled the full libopenshot library,
  Python binding, OpenCV 5 code, FFmpeg 9 code, examples, and 516 test targets.
- Latest measured CTest result: **512/516 pass**.
- Residual failures are isolated to:
  - two FFmpeg 9 spherical metadata round-trip tests;
  - two ImageMagick 7 ImageWriter process crashes.
- These are recorded as focused dependency-runtime follow-ups, not hidden or
  disabled.

## Remaining machine validation

Run `ARM64-TEST-AND-VIDEO-PROMPT.md` on a native Windows 11 Arm64 machine to
complete the libopenshot, Python/Qt, frozen application, render, Inno, MSIX,
install, launch, and recording gates. Signing/publication remains
maintainer-owned.
