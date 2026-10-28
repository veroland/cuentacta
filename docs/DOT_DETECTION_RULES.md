# Visible point-dot detection

TACTA scoring counts only visible point dots. A point dot contributes one point
to the color region that surrounds it. The printed card-value badge never
contributes a point.

## Scoring rule

1. Count every visible, valid point dot once.
2. Assign the dot to the immediately surrounding card color.
3. Do not count a dot covered by another card.
4. Return `retake_required` when the image cannot identify every detected
   candidate confidently.

## Valid and invalid candidates

| Candidate | Counts? | Recognition cues |
| --- | --- | --- |
| Visible point dot | Yes | Small, solid white or light-gray circle inside a colored card region. |
| Covered point dot | No | Hidden by another card, even if the card's printed value is higher. |
| Card-value badge | No | Larger central circle, square, or triangle containing a number. |
| Color-accessibility symbol | No | Symbol next to the value badge, not a point dot. |
| Card border or intersection | No | White linework, not a solid dot inside a color region. |
| Starting card mark | No | Black starting-card graphics never score. |

## Detection constraints

The detector must not use a global white-or-gray threshold alone. In uneven
lighting, a light-blue card region or a bright table surface can be classified
as low-saturation light pixels and merge with a point dot.

Use these signals together:

1. **Local contrast**: a candidate must be brighter than its immediate card
   region, not merely bright in the whole image.
2. **Local color ownership**: the immediate surrounding region determines the
   player color.
3. **Relative scale**: point dots are smaller than value badges in the same
   card scene.
4. **Badge structure**: a central numbered circle, square, or triangle is not
   a dot even when it contains light pixels.

Do not reject every component with a small internal hole. JPEG compression,
shadows, or glare can create a hole in an otherwise valid point dot.

## Human-assisted review

When automated classification is uncertain, the app may show a zoomed crop
with the candidate circled and offer the selected player colors plus:

`Not a valid point`

The user may also tap a visible missing dot in the photo and assign it a
selected player color. The user does not enter or edit a total manually. A
rejected candidate must not be counted, and a user-added dot must retain its
tap position and selected color as review evidence.

If the number of uncertain or missing candidates is too high for practical
review, the app must request a retake instead.

## Evidence and current limitations

- `ejemplos/celeste1.jpg` and `ejemplos/celeste2.jpg` show the visual
  difference between small score dots and larger numbered value badges.
- `ejemplos/revision/partida1-detected-dots-2.jpg` records missed pink dots in
  yellow and missed blue dots in green.
- Current fixed component filters can miss light-gray dots in light-blue card
  regions because they merge into a larger low-saturation component.
- The current prototype must retain `retake_required` until measured results
  meet the labeled board-scene totals.

## Verification checklist

- [ ] Every counted candidate is a small, visible solid dot.
- [ ] Every counted candidate has a local owning card color.
- [ ] Numbered value badges are excluded.
- [ ] Symbols, borders, intersections, and the starting card are excluded.
- [ ] Ambiguous candidates are reviewed or trigger `retake_required`.
