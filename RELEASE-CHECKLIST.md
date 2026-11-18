# Nitor release checklist

The repository is **karank2512/nitor** (private, default branch `main`).
It is **not** publicly released. Ticked items are done; everything unticked is
still open. The fonts' shapes and kerning are accepted and must not change;
every remaining fix below is names, metadata or documentation only.

## Done
- [x] Repository renamed from `original-font` to `nitor`, keeping its history,
      content and private visibility; the old URL redirects.
- [x] No document depends on the repository name.
- [x] Final fonts named consistently: family `Nitor`; `Nitor-Thin`,
      `Nitor-Regular`, `Nitor-Black`; variable font `Nitor-VF` (`wght` 100–900,
      default 100); version 1.000; 78 glyphs, 77 characters.
- [x] README and DESIGN claims checked against the files (axis, coverage,
      kerning pairs, metrics, video length and size, WOFF tables, build
      commands).
- [x] All README links resolve to files in the repository; no external links.
- [x] No secrets, tokens, local user paths or session material committed;
      the PNG images carry no metadata chunks and the MP4 no metadata atoms.
- [x] README "Installing" now states plainly that no licence and no
      permission to use, install or embed the fonts has been granted.
- [x] `nitor/video/make_frames_nitor.py` now describes its real source: it is
      complete on its own and is what produced `video/Nitor-specimen.mp4`.
- [x] Independent read-only review completed; its findings are reflected here.

## Owner decisions (open; blocking any public release)
- [ ] **Licence.** None is granted (LICENSE, README, font name ID 13).
- [ ] **Copyright holder.** "To be confirmed"; font name ID 0 holds a
      placeholder.
- [ ] **Git history.** Commits carry the author's name and email, and the
      development folders (`stage0/`, `r4/`, `diag/`, `drift1/`) contain
      working titles and personal references. Decide whether the history and
      those folders may become public as they are (`drift1/` is needed by the
      build).
- [ ] **Visibility.** Stays private until the decisions above are made.

## Fixes that follow the decisions (names, metadata, docs only)
- [ ] Rebuild the four fonts' name records with the chosen copyright (ID 0)
      and licence (ID 13, plus licence URL ID 14), and replace the
      "PRIVATE PROOF" / "Private; not a public release" strings in IDs 0, 10
      and 13. Set the embedding setting (`fsType`, currently 2, restricted) to
      match the licence. Regenerate the WOFF files and verify that `glyf`,
      `gvar`, `hmtx`, `cmap` and `GPOS` stay byte-identical.
- [ ] Update LICENSE, the README "Status" and "Licence and author" sections,
      and the "Installing" note to match the chosen licence.
- [ ] `nitor/README.md` and `nitor/build_nitor.py` mention working titles, a
      personal name and a time zone; reword them if the repository goes
      public.
- [ ] Optional: add a STAT table and PostScript names for the variable font's
      named instances; consider WOFF2 (needs the Brotli module, which would be
      an install decision).
