# Technical plan

Build an Android client and a Python image-analysis service. Start with a measurable proof of concept before building the complete mobile interface.

## Proposed architecture

| Component | Responsibility | Proposed technology |
| --- | --- | --- |
| Android app | Temporary game setup, camera capture, result display, retake guidance | Kotlin, Jetpack Compose, CameraX |
| API | Receives an image plus the selected TACTA colors and returns typed scores | Python, FastAPI |
| Analysis pipeline | Finds visible point dots, identifies their card color, detects uncertainty, totals scores | Python, OpenCV plus a TACTA-specific recognizer |
| Deployment | Hosts the API for Android clients | To be selected after the proof of concept |

## Analysis contract

The client sends:

```json
{
  "selected_colors": ["green", "pink", "orange"],
  "image": "JPEG image upload"
}
```

The service returns either a result:

```json
{
  "status": "ok",
  "scores": {
    "green": 3,
    "pink": 4,
    "orange": 0
  }
}
```

or a retake response:

```json
{
  "status": "retake_required",
  "reason": "Cards or point dots are not visible enough to score reliably."
}
```

## Delivery phases

### Phase 1 — Visual inventory

- Photograph the 18 cards of one reference color in two non-overlapping 3x3 grids.
- Photograph at least one card of each playable color and the black starting card.
- Reuse the reference-color layouts and values across decks; only the color classification varies.
- Use one card side only: the user confirmed that both sides are visually the same.
- Record a card catalog and the value/color features required for recognition.

### Phase 2 — Analysis proof of concept

- Build a small Python service that accepts a board image.
- Establish a baseline with the supplied examples and labeled reference scenes.
- Return either a complete score object or `retake_required`.
- Measure results only against scenes with known expected totals.

Current baseline: the local Python harness must detect every visible white point dot and assign it to its surrounding card color. It must be calibrated against the recorded board totals. Card-value icons are not score items.

A scoring candidate must be a solid white circle fully inside the owning card-color region. Card-value badges, color-accessibility symbols, borders, and card intersections must be rejected even when they contain white pixels.

### Assisted point review

When uncertainty is bounded, the client displays the photograph with detected
points overlaid. The user may tap a visible missing dot and assign one of the
selected player colors, or tap a false detection and reject it. Review stores
point-level evidence only; it never accepts a manually entered total.

When uncertainty is too broad to review efficiently, such as a dense large
board, the client returns `retake_required` instead.

### Phase 3 — Android proof of concept

- Create the temporary game setup flow.
- Integrate CameraX capture and the analysis endpoint.
- Render scores and retake guidance.

### Phase 4 — Reliability and release preparation

- Test varied table surfaces, lighting, distances, player counts, rotations, and overlaps.
- Set a confidence threshold from measured results.
- Add API abuse limits, image deletion, privacy documentation, and release assets before considering Google Play.

## Key technical rules

- Treat a score as valid only when every selected color has a confident result.
- Do not silently convert low confidence into zero points.
- Permit only point-level add or reject actions during review; never accept a direct total override.
- Delete uploaded board images after analysis unless an explicit future retention policy is approved.
- Keep API responses typed and deterministic; the app must never parse free-form prose as scores.
- Keep the recognition scope fixed to TACTA; do not generalize to other games without a new product decision.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Cards are rotated or partially covered | Count every visible point dot and reject insufficiently visible regions. |
| Reflections, shadows, and blur | Validate capture quality before analysis and request a retake. |
| Few real game images | Build a card catalog, generate synthetic scenes, and label a smaller set of real scenes for evaluation. |
| Incorrect totals | Require a labeled evaluation set before claiming reliability; prefer retake over a guessed result. |
| Public-release privacy/costs | Keep these out of the prototype, then define retention, rate limits, and hosting budget before publication. |
