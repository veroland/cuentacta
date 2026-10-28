import cv2
import numpy as np

from cuentacta.analysis import TactaAnalyzer, _enhance_luminance, find_visible_points
from cuentacta.cli import _apply_answers, _write_review_crops


def test_finds_a_visible_blue_point() -> None:
    image = np.zeros((1_000, 1_000, 3), dtype=np.uint8)
    cv2.circle(image, (500, 500), 22, _bgr_from_hsv(105, 255, 255), thickness=-1)
    cv2.circle(image, (500, 500), 11, (230, 230, 230), thickness=-1)

    points = find_visible_points(image)

    assert len(points) == 1
    assert points[0].color == "blue"


def test_ignores_non_circular_light_marks() -> None:
    image = np.zeros((300, 300, 3), dtype=np.uint8)
    cv2.rectangle(image, (110, 110), (190, 190), _bgr_from_hsv(105, 255, 255), thickness=-1)
    cv2.rectangle(image, (135, 135), (165, 165), (230, 230, 230), thickness=-1)

    assert find_visible_points(image) == []


def test_enhances_local_luminance_without_changing_dimensions() -> None:
    image = np.full((64, 64, 3), 40, dtype=np.uint8)
    image[24:40, 24:40] = 70

    enhanced = _enhance_luminance(image)

    assert enhanced.shape == image.shape[:2]
    assert enhanced[32, 32] > enhanced[0, 0]


def test_analyzer_totals_visible_points_per_selected_color(monkeypatch) -> None:
    analyzer = TactaAnalyzer()
    monkeypatch.setattr(
        "cuentacta.analysis.find_visible_points",
        lambda image: [
            _point("blue", (10, 10)),
            _point("blue", (20, 10)),
            _point("pink", (30, 10)),
        ],
    )

    result = analyzer.analyze_image(np.zeros((100, 100, 3), dtype=np.uint8), ["blue", "pink"])

    assert result.status == "ok"
    assert result.scores == {"blue": 2, "pink": 1}


def test_analyzer_returns_retake_when_no_points_are_visible() -> None:
    result = TactaAnalyzer().analyze_image(np.zeros((100, 100, 3), dtype=np.uint8))

    assert result.status == "retake_required"
    assert result.scores is None


def test_analyzer_returns_retake_for_a_low_confidence_point(monkeypatch) -> None:
    monkeypatch.setattr(
        "cuentacta.analysis.find_visible_points",
        lambda image: [
            _point("blue", (10, 10), confidence=0.7),
        ],
    )

    result = TactaAnalyzer().analyze_image(np.zeros((100, 100, 3), dtype=np.uint8))

    assert result.status == "retake_required"
    assert result.scores is None


def test_writes_named_review_crop_for_an_uncertain_point(tmp_path) -> None:
    image = np.zeros((400, 400, 3), dtype=np.uint8)
    point = _point("blue", (200, 200), confidence=0.6)

    _write_review_crops(image, [point], tmp_path, "partida1")

    assert (tmp_path / "partida1-question-01-blue-or-purple.jpg").exists()


def test_review_answers_reclassify_or_reject_a_point() -> None:
    questions = [
        _point("blue", (10, 10), confidence=0.6),
        _point("purple", (20, 10), confidence=0.5),
    ]
    answers = {
        "partida1-question-01-blue-or-purple.jpg": "purple",
        "partida1-question-02-purple-or-blue.jpg": "reject",
    }

    reviewed = _apply_answers(questions, questions, answers, "partida1")

    assert [point.color for point in reviewed] == ["purple"]


def _bgr_from_hsv(hue: int, saturation: int, value: int) -> tuple[int, int, int]:
    hsv = np.uint8([[[hue, saturation, value]]])
    return tuple(int(value) for value in cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0, 0])


def _point(color: str, center: tuple[int, int], confidence: float = 1.0):
    from cuentacta.analysis import PointDetection

    return PointDetection(
        color=color,
        confidence=confidence,
        center=center,
        alternatives=(color, "purple" if color != "purple" else "blue"),
    )
