"""Detect and count visible TACTA point dots from a board photograph."""

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
    color: ColorName | None
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
    """Count the visible white point dots that remain visible on colored cards."""

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
            detections = tuple(
                point for point in detections if point.color is None or point.color in selected
            )
        if not detections:
            return AnalysisResult(
                status="retake_required",
                scores=None,
                reason="No TACTA point dots were visible enough to score.",
                detections=detections,
            )
        if any(point.confidence < _MINIMUM_POINT_CONFIDENCE for point in detections):
            return AnalysisResult(
                status="retake_required",
                scores=None,
                reason="Some visible point dots could not be assigned to a card color confidently.",
                detections=detections,
            )

        scores = {color: 0 for color in selected} if selected is not None else {}
        for point in detections:
            scores[point.color] = scores.get(point.color, 0) + 1
        return AnalysisResult(status="ok", scores=scores, reason=None, detections=detections)


def find_visible_points(image: np.ndarray) -> list[PointDetection]:
    """Find circular, light point dots and assign them to their colored card.

    A point dot is light and almost unsaturated; the colored region immediately
    around it determines its owner. Card-value icons are larger and must not
    be counted as points.
    """

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    enhanced_luminance = _enhance_luminance(image)
    _, bright_pixels = cv2.threshold(enhanced_luminance, 170, 255, cv2.THRESH_BINARY)
    low_saturation = cv2.inRange(hsv, (0, 0, 0), (179, 110, 255))
    enhanced_dots = cv2.bitwise_and(bright_pixels, low_saturation)
    original_dots = cv2.inRange(hsv, (0, 0, 150), (179, 110, 255))
    local_dots = _local_contrast_mask(image)

    points = _find_points_in_mask(original_dots, hsv)
    points.extend(_find_points_in_mask(enhanced_dots, hsv))
    points.extend(_find_points_in_mask(local_dots, hsv))
    return _deduplicate_points(points)


def _find_points_in_mask(mask: np.ndarray, hsv: np.ndarray) -> list[PointDetection]:
    labels, statistics, centers = _connected_components(mask)
    minimum_side = max(3, round(min(hsv.shape[:2]) * 0.004))
    maximum_side = max(8, round(min(hsv.shape[:2]) * 0.02))

    points: list[PointDetection] = []
    for label, (x, y, width, height, area) in enumerate(statistics[1:], start=1):
        if not (
            15 <= area <= 2_000
            and minimum_side <= width <= maximum_side
            and minimum_side <= height <= maximum_side
        ):
            continue
        if area / (width * height) < 0.55:
            continue
        circularity = _circularity(labels, label, x, y, width, height)
        if circularity < 0.75:
            continue
        if _has_large_hole(labels, label, x, y, width, height):
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


def _has_large_hole(
    labels: np.ndarray,
    label: int,
    x: int,
    y: int,
    width: int,
    height: int,
) -> bool:
    component = np.uint8(labels[y : y + height, x : x + width] == label) * 255
    contours, hierarchy = cv2.findContours(component, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    if hierarchy is None:
        return False
    outer_area = max(
        (cv2.contourArea(contour) for contour, (_, _, _, parent) in zip(contours, hierarchy[0]) if parent < 0),
        default=0.0,
    )
    hole_area = sum(
        cv2.contourArea(contour)
        for contour, (_, _, _, parent) in zip(contours, hierarchy[0])
        if parent >= 0
    )
    return outer_area > 0 and hole_area / outer_area > 0.25


def _surrounding_color(
    hsv: np.ndarray,
    center: tuple[int, int],
    diameter: int,
) -> tuple[ColorName | None, float, tuple[ColorName, ColorName]]:
    x, y = center
    radius = max(1, diameter // 2)
    y_coordinates, x_coordinates = np.ogrid[: hsv.shape[0], : hsv.shape[1]]
    distance = np.hypot(x_coordinates - x, y_coordinates - y)
    ring = (distance > radius) & (distance < radius * 1.3)
    colored_ring = ring & (hsv[:, :, 1] > 40) & (hsv[:, :, 2] > 60)
    ring_area = np.count_nonzero(ring)
    if np.count_nonzero(colored_ring) < 20 or np.count_nonzero(colored_ring) / ring_area < 0.35:
        return None, 0.0, ("blue", "purple")
    pixels = hsv[colored_ring]

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


def _local_contrast_mask(image: np.ndarray) -> np.ndarray:
    """Find bright compact features relative to their immediate surroundings."""

    luminance = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)[:, :, 0]
    background = cv2.GaussianBlur(luminance, (0, 0), 9)
    contrast = cv2.subtract(luminance, background)
    _, mask = cv2.threshold(contrast, 18, 255, cv2.THRESH_BINARY)
    return mask


def _read_image(path: Path) -> np.ndarray:
    image = cv2.imread(str(path))
    if image is None:
        raise ValueError(f"Could not read image: {path}")
    return image
