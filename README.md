# CuentaCTA

Work in progress: an Android app that automatically counts visible TACTA points from a board photograph.

## Current scope

- TACTA only.
- Android first.
- Temporary games: selected player colors, optional names, one photo, automatic totals.
- A low-confidence image asks for another photo instead of guessing a score.

## Project documentation

- [Product requirements](docs/PRD.md)
- [Technical plan](docs/TECHNICAL_PLAN.md)
- [Visual reference collection](docs/DATA_COLLECTION.md)
- [Roadmap](docs/ROADMAP.md)

Third-party visual references and game materials are intentionally excluded from version control.

## Local scoring proof of concept

The local harness recognizes visible white point dots and refuses to guess
when their card color is uncertain.
Only solid white circles fully inside a card-color region count; value badges,
color-accessibility symbols, borders, and card intersections do not.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m cuentacta.cli ejemplos\partida1.jpg --debug-output artifacts\partida1-debug.jpg --review-output ejemplos\revision --review-answers ejemplos\revision\answers.json
```

The command prints either scores or `retake_required`, and the optional debug
image marks every detected point dot. `--review-output` writes every
uncertain region with filenames such as `partida1-question-01-purple-or-blue.jpg`.
Its `questions.json` lists the selected player colors for each crop plus a
`reject` option for non-points.
An optional `answers.json` maps those filenames to a color or `reject`; its
`assisted_scores` output is provisional and does not bypass `retake_required`.
Expected totals must be recorded before a board photo can be used to measure
scoring accuracy.
