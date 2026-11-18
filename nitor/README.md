# Nitor

Reverse-contrast variable display face (weight axis `wght` 100-900): hairline
verticals, weight carried by the horizontals. Original drawings made in this
project. The fonts, their build source and the font documentation are licensed
under the SIL Open Font License 1.1 with Reserved Font Name "Nitor" (see
../OFL.txt and ../LICENSE); the specimen video and its scripts in nitor/video/
are not licensed, even though their build commands are listed below. No
packaged release has been published.

Family name selected by Karan on 2026-11-18. The shapes and kerning are exactly
the accepted D1 RC2 proof; only names and metadata changed.

## Files (built into `nitor/out/`, not committed)
| File | What |
|---|---|
| `fonts/Nitor-VF.ttf` | variable font, `wght` 100-900 (named instances Thin 100, Regular 400, Black 900) |
| `fonts/Nitor-Thin.ttf`, `Nitor-Regular.ttf`, `Nitor-Black.ttf` | static cuts at 100 / 400 / 900 |
| `fonts/validation.json` | name records, table-identity checks vs RC2, coverage |
| `video/Nitor-specimen.mp4` | 24.5 s, 1080x1350, 30 fps, silent specimen |

Coverage: 78 glyphs, 77 characters (a-z A-Z 0-9 space ! " & ' ( ) , - . / : ; ? and en dash).
Known gaps: no hinting, overlapping contours, no WOFF2, kerning covers collision pairs only, no accented letters.

## Rebuild from source
Uses the python.org Python 3.11 with fontTools 4.39.4 and Pillow 9.5.0 as already installed, plus
macOS Swift/AVFoundation for the video. Nothing else needs installing.

```sh
P=/Library/Frameworks/Python.framework/Versions/3.11/bin/python3.11
$P -B drift1/build.py          # masters -> drift1/out/fonts/DriftD1-VF.ttf (+ instances)
$P -B drift1/rc1.py            # collision kerning + QA -> drift1/out/rc1/
$P -B drift1/rc2.py            # ampersand fix, same kerning -> drift1/out/rc2/
$P -B nitor/build_nitor.py     # names/metadata only -> nitor/out/fonts/ (+ validation.json)

# video (frames go to any scratch folder)
$P -B nitor/video/make_frames_nitor.py nitor/out/fonts/Nitor-VF.ttf <frames_dir> nitor/out/video/frame-qa.json
swift nitor/video/encode.swift encode <frames_dir> 735 30 nitor/out/video/Nitor-specimen.mp4 6000000
swift nitor/video/encode.swift stats nitor/out/video/Nitor-specimen.mp4 nitor/out/video/encoded-frame-stats.csv
```

Note: the build steps write fixed output paths; run them in a copy of the
project if existing outputs must be kept byte-for-byte (fontTools stamps build
timestamps into `head`).
A from-scratch run of this chain in a scratch copy reproduced all four Nitor
font files with byte-identical `glyf`, `loca`, `gvar`, `hmtx`, `hhea`, `maxp`,
`cmap`, `GPOS`, `post`, `OS/2`, `name` and `fvar` tables.
