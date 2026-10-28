# Delivery roadmap

The next milestone is evidence that the visual analysis can count TACTA scores reliably. App polish and publication come after that proof exists.

## Milestones

| Milestone | Outcome | Status |
| --- | --- | --- |
| Product definition | Android-only, TACTA-only, temporary automatic scoring flow | Complete |
| Reference review | First batch of 19 board/reference images reviewed | In progress |
| Card catalog | Blue deck layouts and values plus a reference for every playable color | Complete for proof of concept |
| Scoring proof of concept | Local detection harness returns a score or requests a retake; calibration labels pending | In progress |
| Android proof of concept | New game, capture, result, and retake screens | Not started |
| Reliability validation | Measured performance on labeled scenes | Not started |
| Google Play preparation | Privacy, operational, and store-release requirements | Not started |

## Immediate next action

Calibrate visible-point-dot detection against the recorded totals in `partida1.jpg` and `partida2.jpg`. Do not return a score until every detected point dot has a confident card-color assignment.

## Definition of a usable proof of concept

- It accepts a final-board photo and the selected colors.
- It returns a total per selected color or explicitly requests a retake.
- It is tested only on images with known expected totals.
- It records failures so the next data-collection pass targets the missing visual conditions.
