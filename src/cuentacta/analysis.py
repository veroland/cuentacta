"""Detect and count visible TACTA point markers from a board photograph."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import cv2
import numpy as np

ColorName = str

_HUE_REFERENCES: dict[ColorName, int] = {
    "red": 0,
    "orange": 15,
    "green": 60,
    "blue": 105,
    "purple": 140,
    "pink": 167,
}
_MINIMUM_POINT_CONFIDENCE = 0.85


@dataclass(frozen=True)
class PointDetection:
    color: ColorName
    confidence: float
    center: tuple[int, int]
    alternatives: tuple[ColorName, ColorName]


@dataclass(frozen=True)
class AnalysisResult:
    status: str
    scores: dict[ColorName, int] | None
    reason: str | None
    detections: tuple[PointDetection, ...]


class TactaAnalyzer:
    """Count the circular point markers that remain visible on colored cards."""

    def analyze_path(
        self,
        image_path: Path,
        selected_colors: Iterable[ColorName] | None = None,
    ) -> AnalysisResult:
        return self.analyze_image(_read_image(image_path), selected_colors)

    def analyze_image(
        self,
        image: np.ndarray,
        selected_colors: Iterable[ColorName] | None = None,
    ) -> AnalysisResult:
        selected = tuple(selected_colors) if selected_colors is not None else None
        if selected is not None:
            unknown_colors = set(selected).difference(_HUE_REFERENCES)
            if unknown_colors:
                raise ValueError(f"Unsupported selected colors: {sorted(unknown_colors)}")

        detections = tuple(find_visible_points(image))
        if selected is not None:
            detections = tuple(point for point in detections if point.color in selected)
        if not detections:
            return AnalysisResult(
                status="retake_required",
                scores=None,
                reason="No TACTA point markers were visible enough to score.",
                detections=detections,
            )
        if any(point.confidence < _MINIMUM_POINT_CONFIDENCE for point in detections):
            return AnalysisResult(
                status="retake_required",
                scores=None,
                reason="Some visible point markers could not be assigned to a card color confidently.",
                detections=detections,
            )

        scores = {color: 0 for color in selected} if selected is not None else {}
        for point in detections:
            scores[point.color] = scores.get(point.color, 0) + 1
        return AnalysisResult(status="ok", scores=scores, reason=None, detections=detections)


def find_visible_points(image: np.ndarray) -> list[PointDetection]:
    """Find circular, light markers and assign them to their colored card.

    A marker is light and almost unsaturated; the colored ring immediately
    around it determines its owner. This makes the detector independent from
    the printed number, which may describe points hidden by an overlap.
    """

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    enhanced_luminance = _enhance_luminance(image)
    _, bright_pixels = cv2.threshold(enhanced_luminance, 170, 255, cv2.THRESH_BINARY)
    low_saturation = cv2.inRange(hsv, (0, 0, 0), (179, 110, 255))
    enhanced_markers = cv2.bitwise_and(bright_pixels, low_saturation)
    original_markers = cv2.inRange(hsv, (0, 0, 150), (179, 110, 255))

    points = _find_points_in_mask(original_markers, hsv)
    points.extend(_find_points_in_mask(enhanced_markers, hsv))
    return _deduplicate_points(points)


def _find_points_in_mask(mask: np.ndarray, hsv: np.ndarray) -> list[PointDetection]:
    labels, statistics, centers = _connected_components(mask)
    minimum_side = round(min(hsv.shape[:2]) * 0.008)
    maximum_side = round(min(hsv.shape[:2]) * 0.024)

    points: list[PointDetection] = []
    for label, (x, y, width, height, area) in enumerate(statistics[1:], start=1):
        if not (
            150 <= area <= 2_000
            and minimum_side <= width <= maximum_side
            and minimum_side <= height <= maximum_side
        ):
            continue
        circularity = _circularity(labels, label, x, y, width, height)
        if circularity < 0.82:
            continue
        center = tuple(int(round(value)) for value in centers[label])
        color, color_confidence, alternatives = _surrounding_color(
            hsv, center, max(width, height)
        )
        if color is None:
            continue
        confidence = min(1.0, circularity * color_confidence)
        points.append(
            PointDetection(
                color=color,
                confidence=confidence,
                center=center,
                alternatives=alternatives,
            )
        )
    return points


def _deduplicate_points(points: list[PointDetection]) -> list[PointDetection]:
    unique: list[PointDetection] = []
    for point in sorted(points, key=lambda item: item.confidence, reverse=True):
        if any(np.hypot(point.center[0] - existing.center[0], point.center[1] - existing.center[1]) < 20 for existing in unique):
            continue
        unique.append(point)
    return unique


def _enhance_luminance(image: np.ndarray) -> np.ndarray:
    """Raise local contrast without changing the card colors used for ownership."""

    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    luminance, _, _ = cv2.split(lab)
    enhanced = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(luminance)
    return enhanced


def _connected_components(mask: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    count, labels, statistics, centers = cv2.connectedComponentsWithStats(mask)
    if count <= 1:
        return labels, np.empty((0, 5), dtype=np.int32), np.empty((0, 2), dtype=np.float64)
    return labels, statistics, centers


def _circularity(
    labels: np.ndarray,
    label: int,
    x: int,
    y: int,
    width: int,
    height: int,
) -> float:
    component = np.uint8(labels[y : y + height, x : x + width] == label) * 255
    contours, _ = cv2.findContours(component, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return 0.0
    contour = contours[0]
    perimeter = cv2.arcLength(contour, True)
    if perimeter == 0:
        return 0.0
    return float(4 * np.pi * cv2.contourArea(contour) / (perimeter * perimeter))


def _surrounding_color(
    hsv: np.ndarray,
    center: tuple[int, int],
    diameter: int,
) -> tuple[ColorName | None, float, tuple[ColorName, ColorName]]:
    x, y = center
    radius = max(1, diameter // 2)
    y_coordinates, x_coordinates = np.ogrid[: hsv.shape[0], : hsv.shape[1]]
    distance = np.hypot(x_coordinates - x, y_coordinates - y)
    ring = (distance > radius * 0.7) & (distance < radius * 1.5)
    pixels = hsv[ring & (hsv[:, :, 1] > 100) & (hsv[:, :, 2] > 60)]
    if len(pixels) < 20:
        return None, 0.0, ("blue", "purple")

    hue = float(np.median(pixels[:, 0]))
    candidates = sorted(
        ((name, _hue_distance(hue, reference)) for name, reference in _HUE_REFERENCES.items()),
        key=lambda item: item[1],
    )
    color, distance_to_color = candidates[0]
    confidence = max(0.0, 1 - distance_to_color / 18)
    return color, confidence, (candidates[0][0], candidates[1][0])


def _hue_distance(first: float, second: float) -> float:
    distance = abs(first - second)
    return min(distance, 180 - distance)


def _read_image(path: Path) -> np.ndarray:
    image = cv2.imread(str(path))
    if image is None:
        raise ValueError(f"Could not read image: {path}")
    return image
