# Nitor design notes

## The idea

Most display faces put the weight in the verticals. Nitor reverses that: the
verticals are hairlines and every horizontal (arch tops, bowl tops and
bottoms, bars) carries the weight. One rule gives the face its character:
**wherever strokes meet or bottom out, a horizontal band sits there.** Bars
overhang the letter, `v` and `w` sit on a flat band, `x` and `k` carry a band
through their junction, the dots on `i` and `j` are short horizontal bands,
and the punctuation dots are near-square blocks.

On the weight axis the horizontals grow much more than the verticals: from 100
to 900 the horizontal stroke goes from 22 to 132 units (six times), while the
vertical stroke goes from 18 to 40 (just over twice). At 100 the face is a
fine near-monoline; at 900 the horizontals are heavy bands against thin stems,
so a word appears to build up line by line, like stacked scanlines.

## Metrics

Units per em 1000. x-height 560, cap height 740, ascender 800, descender
−210, figures 740. Round overshoot 14.

| Master | Vertical stroke | Horizontal stroke |
|---|---|---|
| Thin (`wght` 100, default) | 18 | 22 |
| Black (`wght` 900) | 40 | 132 |

## Construction

- **Bowls and arches** are bands between an outer ellipse and an inset inner
  ellipse. The inset is thin at the sides (the vertical stroke) and thick at
  the top and bottom (the horizontal stroke), which is what makes the
  contrast reversed.
- **Interpolation:** every arc is drawn with a fixed number of points (40),
  whatever its angle, so the thin and black masters always have the same
  point structure and interpolate cleanly.
- **Stems** are straight hairline rectangles. Diagonals are hairline strokes
  whose ends are cut horizontally.
- **Overhang:** the bars and bands of `e`, `f`, `k`, `t`, `x`, `z`, `A`, `E`,
  `F`, `G`, `H`, `K`, `X`, `Y`, `Z`, `2`, `4` and the arm of `&` run 34 units
  past the stroke they cross.
- **Tails:** `l` and `t` end in a curved tail with a thick bottom and a
  hairline side, the same logic as the bowls. An early square foot made `l`
  read as a capital `L`; the curved tail fixed that.
- **`s` and `S`** have a single diagonal spine joining two bowls. An earlier
  version drew the spine twice and left a bulge at the left.
- **Figures and punctuation** follow the same rules: the `2` has a proper
  diagonal stroke, the `Q` tail crosses its bowl instead of sitting under it
  like an underline, and dots are near-square at every weight so they never
  read as dashes.

## Spacing and kerning

Each glyph has its own side bearings. Kerning is deliberately limited to
collisions: every pair of characters was checked at weights 100 and 900, and
the 91 pairs whose ink would come closer than 28 units get just enough space.
Most are `f` followed by a diagonal or a bracket, and the overhanging bars.

## The ampersand fix

In browser rendering tests the ampersand showed a small flaw: its diagonal
began with a flat cut that stuck out from the lower left of the upper loop,
as a tick at light weights and a corner at heavy ones. The fix starts the
diagonal at the bottom of the upper loop, inside that loop's stroke, where
the near-horizontal stroke covers the cut at every weight. Only the ampersand
changed; every other glyph and every kerning pair stayed identical.

## Quality checks

- Both masters checked for compatible point structure; no zero-area contours.
- Every character has ink at weights 100, 400 and 900, and nothing exceeds
  the vertical metrics.
- Rendered in Chrome from 12 px to 300 px on dark and light grounds,
  including in-between weights, with no seams where overlapping contours meet.
- The final named files keep the shape, variation, metric, character-map and
  kerning tables byte-identical to the accepted proof.

## Known gaps

No hinting, overlapping contours kept, no WOFF2, no accented letters, and a
limited punctuation set. The weakest letters are `k`, `K`, `M`, `N` and `&`,
and the thinnest end of the axis is plainer than the middle and heavy
weights.

## Specimen video

The specimen shows the face on a dark, CRT-like screen with bloom, grain and
scanlines. A beam paints the opening phrase, rows slide sideways at different
weights, a column of words passes through a focus line, and the name builds
from thin to black along the real `wght` axis. Only the camera and the axis
move; every letter is the font.
