# Visual reference collection

This guide creates a reliable TACTA card reference set before model work begins.

## Next capture: blue deck

1. Use a plain, contrasting background and even light.
2. Place nine blue cards in a 3x3 grid with visible gaps; do not overlap cards.
3. Hold the camera parallel to the table and include each full card in the frame.
4. Take a second 3x3 photograph for the remaining nine blue cards.
5. Keep the original image resolution; do not crop, filter, or compress the images.

The same pattern will create two images for each of the six color decks: 12 images total. One side per card is enough because both card sides are visually identical.

## Reference sets

| Set | Purpose | Status |
| --- | --- | --- |
| `ejemplos/` | User-provided board, card, rule, and expected-score examples | Available |
| `referencias/lote-01/` | 19 externally sourced images for internal visual review | Available |
| Physical card catalog | Clean visual reference for all card colors and values | Pending |
| Labeled board scenes | Ground truth for measuring score accuracy | Pending |

## Rules for reference images

- Keep source URLs and rights notes in `referencias/lote-01/SOURCES.md`.
- Externally sourced images are for internal review only until rights are independently verified.
- Do not use an image to evaluate accuracy unless its expected score totals are recorded.
- Never use images containing people or private surroundings in a public dataset without permission.

## Capture-quality checklist

- [ ] Every card is fully in frame.
- [ ] No card overlaps another card.
- [ ] The score value and color marker are sharp enough to read when zoomed.
- [ ] No glare covers a value mark.
- [ ] The image is taken from near directly above.
