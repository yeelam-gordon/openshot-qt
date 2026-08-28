# Appendix: evidence, locks, and fixed references

## Approval and upstream state

- Immutable plan: `hackathon-fleet\agents\hackathon-fix-designer\output\DESIGN.r3.md`.
- Approval: `hackathon-fleet\agents\hackathon-design-risk-reviewer\output\DESIGN-REVIEW.r3.md`, verdict `GO`, `freeze_design: yes`.
- Accepted findings RISK-001 through RISK-008 are resolved by G0-G13. No new finding remained at approval.
- Verified 2026-08-27: issue `openshot-qt#5853` and release PRs `openshot-qt#6075`, `libopenshot#1082`, and `libopenshot-audio#170` were open; published releases remained v3.5.1/v0.7.0/v0.6.0.

Source-proven `develop` baselines on that date were:

| Repository | SHA |
| --- | --- |
| `OpenShot/openshot-qt` | `9cd2b3f3ee9024c3496487a2de30a402515ed659` |
| `OpenShot/libopenshot` | `eac81cf91555438c54fbadef7fdd05bf803f26ee` |
| `OpenShot/libopenshot-audio` | `48516e0b64b9f3ddf2ab79975a42ba2f37023703` |

These commits are evidence baselines, not production pins. G0 selects exact post-4.0 commits and regenerates affected evidence.

## Research and source references

- `C:\s\Demo\ARMCandidate\windows-arm-blocker-analysis.md`
- `C:\s\Demo\ARMCandidate\evidence\blockers-creative-media.md`
- `C:\s\Demo\ARMCandidate\windows-arm-opportunity-ranking.md`
- [MSYS2 environments](https://www.msys2.org/docs/environments/)
- MSYS2 signed `clangarm64.files` repository database and `https://packages.msys2.org/package/mingw-w64-clang-aarch64-<name>`, queried 2026-08-27
- [cx_Freeze#2943](https://github.com/marcelotduarte/cx_Freeze/pull/2943)
- [opencv-python#806](https://github.com/opencv/opencv-python/issues/806), risk context only; this plan uses native MSYS2 OpenCV

Primary code evidence:

- `openshot-qt`: `src\qt_api.py:2284-2486`, `src\windows\export.py:1176-1309`, `freeze.py:142-153,357-443,787-810`, `.gitlab-ci.yml:106-257`, and installer files listed in `files-to-update.md`.
- `libopenshot`: `.gitlab-ci.yml:94-160`, `src\CMakeLists.txt:224-230,358-610`, `bindings\python\CMakeLists.txt:11-140`, and `bindings\python\openshot.i:140-202,252-258`.
- `libopenshot-audio`: `.gitlab-ci.yml:60-110`, `CMakeLists.txt:61-230`.

## Locked BOM and ownership

All rows and transitive PE-producing dependencies enter one signed, cached lock with exact artifact filename/version-release, source and binary URL, SHA-256, SPDX/license, and direct dependencies. The lock digest is embedded as `TOOLCHAIN_LOCK_SHA256` in every producer/application contract. Release jobs verify repository signatures and cached hashes and must not run live `pacman -Syu` or unversioned installs.

| Input | Exact approved pin / policy |
| --- | --- |
| CPython | MSYS2 CLANGARM64 3.14.7-1; native stdlib/extensions only |
| PyQt/sip | `python-pyqt6` 6.11.0-1; `python-pyqt6-sip` 13.12.0-1 |
| Qt | 6.11.2: `qt6-base` 6.11.2-2; SVG/imageformats/multimedia/multimedia-ffmpeg 6.11.2-1 |
| Compiler/runtime | LLVM/Clang 22.1.8-2; libc++ 22.1.8-1; compiler-rt 22.1.8-2; llvm-openmp 22.1.8-1; libwinpthread 14.0.0.r302.gd7f3c5201-1; UCRT |
| Build tools | CMake 4.4.2-2; Ninja 1.13.2-1; SWIG 4.5.0-1 |
| Native libraries | FFmpeg 9.0.1-3; OpenCV 5.0.0-3; Protobuf 35.1-2; ZeroMQ 4.3.5-5; cppzmq 4.11.0-1; babl 0.1.128-1; ImageMagick 7.1.2.30-1; jsoncpp 1.9.8-1 |
| Python app inputs | NumPy 2.5.2-1; PyOpenGL 3.1.10 pure wheel; omit optional PyOpenGL-accelerate |
| cx_Freeze | 8.7.0 sdist, SHA-256 `3d6aed189f96fb6d13182bbc6f33f73d14526fc6fec934286d0456e31faf1543`, built by pinned Arm64 Python/toolchain |
| Producer artifacts | OpenShotAudio 1.0.0/SO 10 and libopenshot 1.0.0/SO 31 at G0-locked SHAs |
| Builder tools | Exact Windows system DLL/SDK/Inno/MSIX/SignTool versions and builder-image digest |

Required policy: preserve WASAPI, FFV1/PCM/Matroska, OpenCV Stabilizer/Tracker/Object Detection, ZeroMQ, babl chroma key, ImageMagick image/text, and system jsoncpp. ASIO stays optional and excluded from baseline. Required feature or license/provenance failure blocks release; it cannot silently disable a feature.

Immutable build evidence includes FFmpeg `-buildconf`, OpenCV build information, Qt build key, `python -VV`, compiler version, and `pacman -Q`.

## Exact Qt package inventory

The package must contain `platforms\qoffscreen.dll`, `platforms\qwindows.dll`, `imageformats\qgif.dll`, `imageformats\qico.dll`, `imageformats\qjpeg.dll`, `imageformats\qsvg.dll`, `iconengines\qsvgicon.dll`, `multimedia\ffmpegmediaplugin.dll`, `Qt6Multimedia.dll`, and their locked closure. `qt6-imageformats` remains pinned for TIFF/WebP/application behavior but does not add an acceptance-plugin filename.

Source loads must resolve below `C:\msys64\clangarm64`; frozen and installed loads must resolve below that stage root. Capture `QLibraryInfo` library/plugin paths, Qt version, required paths/hashes/owners, plugin-loader output, and `PyQt6.sip`. Any alternate binding/backend, duplicate Qt hash/path, out-of-root non-system module, loader warning, unresolved import, foreign machine type, or absolute build-prefix reference fails.

## Fixed G8 fixtures

- Image fixtures: committed 2x2 lossless PNG, JPEG, GIF, ICO, and SVG, each with a canonical RGBA8888 digest.
- Icon fixture: SVG rendered by `qsvgicon.dll` to transparent RGBA8888 at 32x32 with a committed digest.
- Media fixture: RIFF/WAVE with exactly 4,800 stereo `s16le` frames at 48 kHz using the G9 formulas for indexes 0-4799; interleaved PCM SHA-256 `2eefef4340ebac7010fd20389a475c6086faa0fe7acb8f4ab118df4eee3a3704`.
- The media probe uses `QMediaPlayer` + `QAudioBufferOutput`, reaches `LoadedMedia` and `EndOfMedia` within 10 seconds, returns exactly the fixed PCM, and proves `ffmpegmediaplugin.dll` loaded from the stage root.

## Fixed G9 oracle

For frame `n=0..59`, row `y=0..35`, column `x=0..63`: `R=(3*x+5*y+7*n) mod 256`, `G=(11*x+13*y+17*n) mod 256`, `B=(19*x+23*y+29*n) mod 256`, `A=255`. Canonical bytes are tightly packed `bgra` (`B,G,R,A`), stride 256, top-to-bottom, no padding: exactly 60 64x36 frames at `30/1`, time base `1/30`, PTS `n`.

For sample frame `i=0..95999`: `L=((257*i+12345) mod 65536)-32768`, `R=((911*i+23456) mod 65536)-32768`. Canonical audio is exactly 96,000 stereo interleaved two's-complement little-endian `s16` frames at 48 kHz, time base `1/48000`, PTS `i`, chunked as 1,024 samples through PTS 94,208 and a final 768 samples at 95,232. No delay, padding, insertion, truncation, resampling, or tolerance is allowed.

Writer requirements: Matroska with one FFV1 video and one PCM `s16le` audio stream. Video options are `bgra`, level 3, coder 1, context 1, GOP 1, slices 4, slice CRC 1, threads 1, no hardware acceleration. Audio is 48 kHz stereo `s16`, with no resampling/dither. Muxer options are `fflags=+bitexact`, `flush_packets=1`, `avoid_negative_ts=disabled`, zero start, exact metadata `title=OpenShot Arm64 Golden` and `comment=oracle-v1`, no creation time, chapters, or attachments. Output time base is `1/1000`; video PTS is ties-away rounding of `n*1000/30` (`0,33,67,...,1967`); audio starts at PTS 0 and spans exactly 2,000 ms.

Committed aggregate values:

- video SHA-256: `a3602aa3a3e5316d9456c97eb8bafe5c97a692ed5c10f3409db763bfb331b83a`
- PCM SHA-256: `fb240a5aa9dad1572ba742e9a98cd4d33dc078d57c6d2d7cdbfb077df8cb7cd2`
- manifest SHA-256, calculated over the 60 lowercase frame hashes each followed by LF, then the lowercase PCM hash followed by LF: `be4c2c85757437afa5861ff92c121af4ec38ef7fd222371881c92511e5e5b1de`

The authoritative 60 ordered per-frame hashes are:

```text
7aca7dad93170ab65ac6ab5189ac0047ae6d1b5ba92eabb408bdd1bf5096c999
157e95749f0a2aa27f9833b4fee417142607b7622589a9a2e9dc5cead1c18ab8
bd31d1ffd5fe745c72e0c5cf55dbc4cb4ad9538dfa6b019c8781df0e80a1ae26
c015dc09114dae69c187e48bae5ce0145fe0d1df10999c1773f3a60e5feefbce
d8f7e5dd0dd58ddebca4835aab7080bd96c0b1c6cf9129230017654a6bb8b5f5
aa2f0bfa9ccf688c71002dc4a0911ae0fd3249ecb21766ecece3a129a2b2f273
fd623eeddc1708f20627a51c501676b624419972c266536cf856ef718c70a541
38ffc721d935afb064eb8419a23d9c46f612c77d8ea25afd6672ba046af23086
d6d287f9a6f8155a28c83cc569f22eb0d8d0be70324555bffe31b6be84b21e4c
c343e437d13b5ba1627c9a25da10324645452d27ffab20b86be76e22296b7e7e
6c83707b0d1f5e8ee280b5c34880a251ae0658d97ad9d5c3bb4eb93122885133
2c7c7323db3fa7c8923611c01e5f9ffc2c819fc80bedce349a68436c588d1cf9
23064b31565f9beb82ba9d038b397890f36b472e20e0700f34a9d957e088ee06
719ad0720b15bf77d7aca2ba2f138d7ed7e361df0e481e12783a7efebe264864
01de462136bb768877767abf14cd7efb8b016952be5ebc8cdaecb1fed30c355e
2bb697623b8a0ac4f3d713e44f62de6d160c977d660d0c788301a0980e45e1bf
533e6c67612fe04ff68b2389ac7f71ea4c67abc1e19c681d818f409eb5a6927a
9a99a2cb947209cf024378687990902952856598f24186a4668271df55faf63f
c33f87a732dbbaf2dd45817c391f7073ad76dfdb1c511acc79705665eb8c8c21
48056a4968e3a8dd03d265203689e9467bc4ab4eb135522c618a2ffd0b046897
2d3bdc35e058d682f7c1f5d1bcf83b46fc571be834ae807aeddbe99a8b84cc5c
5250299f22e987169dcf2ffdaf05b0e415c369bc7a530ddf1e748108a455dc3e
975844ece04465d7ad45dac921fcb8126059ceaf40b153b7d28871da49e6f8f5
7d8a8ca09580a91012430f7a535b3dea27237779ce18d7f9b3755c68a9e60e9e
4bbea339da2f90b69119afc31d40c5528b328a0235103390a4d8139f927ab407
53bd8419c2e717ddd2e27c6eea4af2c1b1bdcaad1f4c8bedba16d78967835e63
39708aeaae617ad71758b0f0a38e5c5068d87a8ce7bd4b31326d03f3ef718ef8
07a20e6a8b9b232b3e5d5771463983d18ca1f49fefe74034045a71b5150d0536
2f732b3ec23fdff9ea820e3816ab4845dc05be8837b295fdf62386e3082b09b6
66f8e8b8e9c838f07c1bc699c96a7c9ac2475a957db2238336e116ef7df64b5a
6e31b2ed38fbf69d5bf1b8e634572b6f04cd706d8fdcdf0e03ccf61ac0b195f2
89b38fbacfaf6355a5c32a233725aa07cedd6040dc95c045d71b875bb8d17bbd
6674724495e6a4d68a85ae204331abe7080cee9f2aea315011ee15150db9d3c2
7dc7e75a40c5f13ce4e5552282df9df834c329bacfab52a44454653f6fa92379
62c46fb178c28b982e4d09a9f6dcbaafc51ed3bf85862ff7273c77477cdfd763
71b6d90af7e6d099143e75b04a3afdf15865063e84725964ce96d89fe7d35a83
97256fb17b6947a2b3b2bfe320c5a5fff14ff3ef79eb028813e248e9869849c8
20f99727755a090dae05993494072d8fe7fe64a18eb06ae775b813143d145ebf
29624465055fed82935583b502ddc94b9f65d5c93b440d62b3919802e0c2c4bf
de1849d13f9edfd20bcb440c81db7d6e9167776be8608725a76e920488def46e
c354350a82c70c49b2d7372b899329d9fd910631435b86c5229f41de398edc1f
0affad1cdebe86fcf091b690cf43e5d7cb1e268ee03187f9a6921ffe3cdddffd
cfc9ea1267f6a28863f8d83b4a30f69d92839459f7ceb16f1477f8cb579d9f61
e66528c8186f477635aaed7373117de957d719719b7c785e1491df21d1ee80fc
b09e7482be957d8a4f5eba8d98d7e51645de429127af07bb5f846db3c2c97085
9fe7e9c1a57f7ae8633de7f09debb3d9162c23d196f191150baff9655523107b
2b1635672a2910bf94dd7b4e08441b5f84899a126ac98f9dc4433d6441fa1c5c
b051f1f20fb44534e9ade416bf35185bea81b5534d9e8ff86bd810a88bacc9b6
035e33eb703b869d3414ef2b09ecc675c2bcec5554556a25d2795b0296ee8b57
116b8f5ac9817838e5703d8835bf2123250f9f9d3080adb5e349014eebb71358
e2b0732e7688a12b545b582d50009544c05a2274029cac1dcbf2719b412ec1f7
e93e95a6a9fb6b96d7017dc99c0e6470eafc3b2d349456ffc88a075ae84554f0
472eb8c7eef76322c756ab7acd522e56f5fbfb5543ac9d623c927252e15b8346
fb0d49651fe70d577d0d38e4365d3179eb82dadae7adafc0d44a21157dda2904
cb8613f8a0b04c92a9cce65e028fe7061e67ce2bc9e766f05f2864894b2d5b17
55d9dc84e5d7b0dbe6bd6684fcdb86422bca8b2b37039d6b814bb88bc5f236ed
e01d51a469b9466d7bdc9cf07ca7f0ce6d8e34324e497a7292754e7f5d2daf2f
f4fc9652f23d7e157e9d55eafe3a98cb046ee27f6e8f494cfe2bf3cb595b6e25
1adb0707719432627a3df01b0c3d878c5e6818bd161c3b6a11ca887831cfeb3b
74ae9027e48f7a82ec6597cf2e4437019285c7367b66c5d0ed5e34ff6c7e293e
```

The stdlib-only generator must compare all hashes before writer execution and cannot import OpenShot, FFmpeg, Qt, NumPy, or production oracle helpers. Two exports must match all semantic hashes and normalized metadata. Container byte identity, library strings, file timestamps, cluster offsets, packet partitioning, and volatile container metadata are excluded.

Real-writer negative cases cover unavailable codec, `Open()` failure, first/midstream `WriteFrame()` failure, `Close()` failure, and fixed-frame cancellation. Each propagates normal failure/cancel signaling, releases the writer, stops progress, and leaves no success-shaped output.
