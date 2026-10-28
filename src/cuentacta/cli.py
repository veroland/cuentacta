"""Command-line harness for inspecting the proof-of-concept recognizer."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path

import cv2

from .analysis import TactaAnalyzer, _read_image


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a TACTA board photograph.")
    parser.add_argument("image", type=Path)
    parser.add_argument("--colors", nargs="*")
    parser.add_argument("--debug-output", type=Path)
    parser.add_argument("--review-output", type=Path)
    parser.add_argument("--review-answers", type=Path)
    args = parser.parse_args()

    analyzer = TactaAnalyzer()
    image = _read_image(args.image)
    result = analyzer.analyze_image(image, args.colors)
    questions = _review_questions(result.detections)
    answers = _read_answers(args.review_answers)
    reviewed = _apply_answers(result.detections, questions, answers, args.image.stem)
    print(
        json.dumps(
            {
                "status": result.status,
                "scores": result.scores,
                "reason": result.reason,
                "detections": [detection.__dict__ for detection in result.detections],
                "assisted_scores": _score_points(reviewed) if answers else None,
            },
            indent=2,
        )
    )
    if args.debug_output:
        _write_debug_image(image, result.detections, args.debug_output)
    if args.review_output:
        _write_review_crops(image, questions, args.review_output, args.image.stem)


def _write_debug_image(image, detections, output: Path) -> None:
    for detection in detections:
        label = f"{detection.color} point ({detection.confidence:.2f})"
        cv2.circle(image, detection.center, 12, (255, 255, 255), 3)
        cv2.putText(
            image,
            label,
            (detection.center[0] + 15, detection.center[1]),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 0, 0),
            5,
            cv2.LINE_AA,
        )
        cv2.putText(
            image,
            label,
            (detection.center[0] + 15, detection.center[1]),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output), image)


def _write_review_crops(image, questions, output: Path, image_stem: str) -> None:
    """Write the most uncertain color regions as named review questions."""

    output.mkdir(parents=True, exist_ok=True)
    for index, detection in enumerate(questions, start=1):
        crop = _crop_region(image, detection.center, radius=140)
        label = f"{detection.alternatives[0]} or {detection.alternatives[1]}?"
        cv2.putText(crop, label, (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 5, cv2.LINE_AA)
        cv2.putText(crop, label, (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.imwrite(str(output / _question_name(image_stem, index, detection)), crop)


def _crop_region(image, center: tuple[int, int], radius: int):
    x, y = center
    padded = cv2.copyMakeBorder(image, radius, radius, radius, radius, cv2.BORDER_REFLECT)
    x, y = x + radius, y + radius
    return padded[y - radius : y + radius, x - radius : x + radius].copy()


def _review_questions(detections):
    return sorted(
        (detection for detection in detections if detection.confidence < 0.85),
        key=lambda detection: detection.confidence,
    )[:6]


def _read_answers(path: Path | None) -> dict[str, str]:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _apply_answers(detections, questions, answers: dict[str, str], image_stem: str):
    answers_by_center = {
        question.center: answers[_question_name(image_stem, index, question)]
        for index, question in enumerate(questions, start=1)
        if _question_name(image_stem, index, question) in answers
    }
    reviewed = []
    for detection in detections:
        answer = answers_by_center.get(detection.center)
        if answer == "reject":
            continue
        reviewed.append(replace(detection, color=answer) if answer else detection)
    return reviewed


def _question_name(image_stem: str, index: int, detection) -> str:
    return (
        f"{image_stem}-question-{index:02d}-"
        f"{detection.alternatives[0]}-or-{detection.alternatives[1]}.jpg"
    )


def _score_points(detections) -> dict[str, int]:
    scores: dict[str, int] = {}
    for detection in detections:
        scores[detection.color] = scores.get(detection.color, 0) + 1
    return scores


if __name__ == "__main__":
    main()
