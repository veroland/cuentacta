# TACTA automatic score counter

An Android app that calculates each TACTA player's visible points from one board photograph. The first release is a temporary, automatic scoring flow with no accounts or match history.

## Quick path

1. Create a game with the participating colors and optional player names.
2. Take a board photograph.
3. Receive a score total per player, or a clear request to retake the photograph.

## Problem

TACTA scores are the visible white point dots on cards of each player's color. Each dot is worth one point; covered dots do not score. The number in a circle, square, or triangle identifies the card's value and is not itself a point. End-of-game boards can be crowded, rotated, partially covered, and photographed under uneven lighting, so manual counting is slow and error-prone.

## Product scope

| Area | Decision |
| --- | --- |
| Game | TACTA only. |
| Platform | Android first; Google Play is a future release path after reliable validation. |
| Session | Temporary: no account, game history, or saved score history. |
| Players | User selects player count, assigns colors, and may enter names. |
| Result | Automatic total per selected color, with point-by-point review when needed. No direct total editing. |
| Low confidence | The app offers point review when bounded; otherwise it asks for a new photograph instead of inventing a score. |
| Processing | A board photo may be sent to a server for analysis. |

## User flow

1. The user opens **New game**.
2. The user chooses the number of players, then assigns a TACTA color to each player and optionally enters a name.
3. The user takes one photograph of the final board.
4. The app checks that the board is sufficiently visible and sends the image for analysis.
5. The app displays detected visible point dots and one total for each participating color.
6. If bounded uncertainty remains, the user may add a visible missing dot or reject a false detection, assigning only a selected player color.
7. If the image has too many uncertain or missing candidates, the app explains why and asks the user to retake it.

## Acceptance criteria

- A result contains every selected player exactly once.
- A result never includes an unselected color.
- Each visible white point dot contributes one point to its card color.
- A point dot hidden by an overlapping card does not contribute to the total.
- A user may add or reject an individual visible point dot during low-confidence review.
- A user cannot enter or edit a total directly.
- A low-confidence image with too many uncertain candidates results in a retake request, not a guessed score.
- Session data disappears when the user leaves or starts a new game.

## Out of scope

- Other board games.
- Accounts, multiplayer synchronization, score history, rankings, or social sharing.
- iOS.
- Offline analysis in the first release.
- Training or redistributing third-party reference images without verified rights.

## Open product decisions

- Define the acceptable success rate after the first labeled evaluation set exists.
- Define which capture issues receive dedicated guidance (blur, glare, missing board area, or severe overlap).
- Define server operating budget and image-retention policy before any public release.
