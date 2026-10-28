# Visual reference collection

This guide creates a reliable TACTA card reference set before model work begins.

## Captured reference: blue deck

1. `ejemplos/celeste1.jpg` contains nine blue cards in a non-overlapping 3x3 grid.
2. `ejemplos/celeste2.jpg` contains the remaining nine blue cards in a non-overlapping 3x3 grid.
3. Together, these photos cover the 18 card layouts and values 1–9 used by every color deck.
4. The original images are retained without cropping, filtering, or compression.

`ejemplos/colores.jpg` provides a color reference for each playable deck and the black starting card. Because the card layouts and values are identical across decks, additional full-deck photos are not needed for the proof of concept. One side per card is enough because both card sides are visually identical.

## Reference sets

| Set | Purpose | Status |
| --- | --- | --- |
| `ejemplos/` | User-provided board, card, rule, and expected-score examples | Available |
| `referencias/lote-01/` | 19 externally sourced images for internal visual review | Available |
| Physical card catalog | Card layouts, values, and deck colors | Complete for proof of concept |
| `partida1.jpg` | Labeled board scene | Pink 12, blue 15, purple 2 |
| `partida2.jpg` | Labeled board scene | Purple 3, orange 10, pink 12, blue 11 |
| `partida3.jpg` | Difficult labeled board scene | Blue 53, pink 54, orange/yellow 29, green 43, red 40, purple 58 |

## Rules for reference images

- Keep source URLs and rights notes in `referencias/lote-01/SOURCES.md`.
- Externally sourced images are for internal review only until rights are independently verified.
- Do not use an image to evaluate accuracy unless its expected score totals are recorded.
- Never use images containing people or private surroundings in a public dataset without permission.

## Capture-quality checklist

- [ ] Every card is fully in frame.
- [ ] No card overlaps another card.
- [ ] Every visible point dot and its card color are sharp enough to read when zoomed.
- [ ] No glare covers a visible point dot.
- [ ] Labels exclude value badges, color-accessibility symbols, card borders, and card intersections.
- [ ] The image is taken from near directly above.
