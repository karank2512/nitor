# Nitor release checklist

The repository is **karank2512/nitor** (public, default branch `main`).
No packaged release (tag or GitHub release) has been published. Ticked items
are done; everything unticked is still open. The fonts' shapes and kerning are accepted and must not change;
every remaining fix below is names, metadata or documentation only.

## Done
- [x] Repository renamed from `original-font` to `nitor`, keeping its history
      and content; the old URL redirects.
- [x] No document depends on the repository name.
- [x] Final fonts named consistently: family `Nitor`; `Nitor-Thin`,
      `Nitor-Regular`, `Nitor-Black`; variable font `Nitor-VF` (`wght` 100–900,
      default 100); 78 glyphs, 77 characters.
- [x] README and DESIGN claims checked against the files (axis, coverage,
      kerning pairs, metrics, video length and size, WOFF tables, build
      commands).
- [x] All README links resolve to files in the repository; no external links.
- [x] No secrets, tokens, local user paths or session material committed;
      the PNG images carry no metadata chunks and the MP4 no metadata atoms.
- [x] `nitor/video/make_frames_nitor.py` describes its real source: it is
      complete on its own and is what produced `video/Nitor-specimen.mp4`.
- [x] **Licence (owner-approved):** SIL Open Font License 1.1 with Reserved
      Font Name "Nitor", covering the fonts, the font build source and the
      font documentation. Official text in `OFL.txt`; scope in `LICENSE`.
- [x] **Copyright notice (owner-approved):** "Copyright (c) 2026, Karan
      Kapur, with Reserved Font Name "Nitor"." It states the claimed holder; it
      is not a certification of legal ownership.
- [x] Fonts rebuilt at version 1.001 with names and metadata only: name IDs
      0 (copyright), 10 (description), 13 (licence) and 14 (licence URL) set,
      and `fsType` changed from 2 (restricted) to 0 (installable). `glyf`,
      `gvar`, `hmtx`, `cmap` and `GPOS` (and `loca`, `hhea`, `maxp`, `post`,
      `fvar`) are byte-identical to the accepted 1.000 fonts; WOFF files
      regenerated.
- [x] Licence header comments added to the font build source files.
- [x] README, LICENSE and `nitor/README.md` updated to the licence and its
      scope.

- [x] **Visibility (owner-approved):** the repository is public, with its
      history and development folders (`stage0/`, `r4/`, `diag/`, `drift1/`)
      as they are. History contains superseded working names and earlier
      private-proof font metadata.

## Open
- [ ] **Specimen media.** The images in `images/` and the video in `video/`
      (and its scripts in `nitor/video/`) are deliberately not licensed: they
      can be viewed, but no reuse permission is granted. Licensing them is a
      separate decision.
- [ ] **Packaged release.** No tag or GitHub release has been published.

## Remaining tidy-ups (docs only)
- [ ] `nitor/README.md` and `nitor/build_nitor.py` still mention working
      titles of the intermediate build steps; reword or explain them.
- [ ] Optional: add a STAT table and PostScript names for the variable font's
      named instances; consider WOFF2 (needs the Brotli module, which would be
      an install decision); check the name "Nitor" against existing font
      names and trademarks.
