# TACTA dot scoring correction
Branch: `fix/tacta-dot-scoring`. Delivery strategy: ask-on-risk. Test runner: `.\.venv\Scripts\python.exe -m pytest -q`.
Correct the local prototype so it totals every visible point dot by player color, using the official rulebook as the source of truth.

## Specs

S1. "recuerda que cuentas todos los puntos. Revisa nuevamente todo porque estas contando mal"
   - Every visible white point dot counts as one point for the owning card color; covered dots do not count.
   - The number inside a circle, square, or triangle is the card's total value, not a score item to count.
   - Official acceptance example from `ejemplos/TACTA_Reglas.pdf`, page 6: green 8, red 7, purple 7, blue 5, pink 5, orange 0.

S2. "claro si revisa lo que esté mal, las reglas están en el manual"
   - The PRD, technical documentation, CLI terminology, detector, and tests must agree with the official manual.
   - The user-selected player colors remain known at game setup; uncertain dot ownership remains reviewable and may be rejected when it is not a point.

## Tasks
- T1 | S1-S2 | inline — audit and correct rule/documentation contract | done | docs corrected; manual verified
- T2 | S1-S2 | inline — replace value-icon counting with visible-dot detection and regression tests | partial | 14 tests pass; official example still over-detects 39 candidates versus 32 expected

## Log
L1. recuerda que cuentas todos los puntos. Revisa nuevamente todo porque estas contando mal
L2. claro si revisa lo que esté mal, las reglas están en el manual
L3. Evidence: manual page 2 defines every visible white dot as one point; page 6 gives the official six-color example totals. Current prototype detects value icons and reports one per candidate, so it is invalid for scoring.
L4. Corrected README and technical documents to describe dots, not value icons. The detector now targets small filled light components; synthetic outlined-badge and number-badge regression tests pass.
L5. The official example's assigned-color counts now match the manual: green 8, red 7, purple 7, blue 5, pink 5, orange 0. Six candidates remain unassigned, so T2 remains partial and the CLI must retain `retake_required` until they are resolved.
