from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np


@dataclass
class Track:
    """Simple motion track for likely watermark text regions."""

    id: int
    bbox: Tuple[int, int, int, int]
    velocity: Tuple[float, float]
    missed: int = 0


def _iou(box_a: Tuple[int, int, int, int], box_b: Tuple[int, int, int, int]) -> float:
    ax, ay, aw, ah = box_a
    bx, by, bw, bh = box_b

    x1 = max(ax, bx)
    y1 = max(ay, by)
    x2 = min(ax + aw, bx + bw)
    y2 = min(ay + ah, by + bh)

    if x2 <= x1 or y2 <= y1:
        return 0.0

    inter = (x2 - x1) * (y2 - y1)
    union = aw * ah + bw * bh - inter
    return inter / union if union > 0 else 0.0


def _center(box: Tuple[int, int, int, int]) -> Tuple[float, float]:
    x, y, w, h = box
    return (x + (w / 2.0), y + (h / 2.0))


def _detect_text_candidates(frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Emphasize bright text-like regions while tolerating animation/blink.
    tophat = cv2.morphologyEx(
        gray,
        cv2.MORPH_TOPHAT,
        cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9)),
    )
    thresh = cv2.adaptiveThreshold(
        tophat,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        25,
        -5,
    )

    # Connect character components.
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 3))
    mask = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates: List[Tuple[int, int, int, int]] = []

    h, w = gray.shape
    frame_area = h * w

    for contour in contours:
        x, y, bw, bh = cv2.boundingRect(contour)
        area = bw * bh
        aspect = bw / max(bh, 1)

        # Heuristic filter for watermark-like text/graphics.
        if area < 200 or area > frame_area * 0.12:
            continue
        if bh < 10 or bw < 20:
            continue
        if aspect < 1.2:
            continue

        # Watermarks typically live away from central action.
        cx, cy = _center((x, y, bw, bh))
        margin_x = 0.2 * w
        margin_y = 0.2 * h
        is_near_edge = (
            cx < margin_x
            or cx > (w - margin_x)
            or cy < margin_y
            or cy > (h - margin_y)
        )
        if not is_near_edge:
            continue

        candidates.append((x, y, bw, bh))

    return candidates


def _match_tracks(
    tracks: List[Track], detections: List[Tuple[int, int, int, int]], next_id: int
) -> Tuple[List[Track], int]:
    assigned = set()

    for track in tracks:
        best_idx = -1
        best_score = 0.0

        # Predict next position for blinking/missing frames.
        tx, ty, tw, th = track.bbox
        vx, vy = track.velocity
        pred = (int(tx + vx), int(ty + vy), tw, th)

        for idx, det in enumerate(detections):
            if idx in assigned:
                continue
            score = _iou(pred, det)
            if score > best_score:
                best_score = score
                best_idx = idx

        if best_idx >= 0 and best_score > 0.1:
            det = detections[best_idx]
            assigned.add(best_idx)
            old_cx, old_cy = _center(track.bbox)
            new_cx, new_cy = _center(det)
            track.velocity = (new_cx - old_cx, new_cy - old_cy)
            track.bbox = det
            track.missed = 0
        else:
            track.missed += 1
            x, y, w, h = track.bbox
            vx, vy = track.velocity
            track.bbox = (int(x + vx), int(y + vy), w, h)

    # Spawn new tracks from unmatched detections.
    for idx, det in enumerate(detections):
        if idx in assigned:
            continue
        tracks.append(Track(id=next_id, bbox=det, velocity=(0.0, 0.0), missed=0))
        next_id += 1

    # Keep tracks for a while to survive blinking text.
    tracks = [t for t in tracks if t.missed <= 8]
    return tracks, next_id


def _expand_box(box: Tuple[int, int, int, int], frame_shape: Tuple[int, int, int]) -> Tuple[int, int, int, int]:
    x, y, w, h = box
    frame_h, frame_w = frame_shape[:2]
    pad_x = max(4, int(w * 0.15))
    pad_y = max(4, int(h * 0.25))

    nx = max(0, x - pad_x)
    ny = max(0, y - pad_y)
    nx2 = min(frame_w, x + w + pad_x)
    ny2 = min(frame_h, y + h + pad_y)
    return nx, ny, nx2 - nx, ny2 - ny


def remove_watermark_from_image(input_path: Path, output_path: Path) -> None:
    frame = cv2.imread(str(input_path))
    if frame is None:
        raise ValueError("Could not read image.")

    detections = _detect_text_candidates(frame)
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)

    for box in detections:
        x, y, w, h = _expand_box(box, frame.shape)
        cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)

    if np.count_nonzero(mask) > 0:
        result = cv2.inpaint(frame, mask, 5, cv2.INPAINT_TELEA)
    else:
        result = frame

    cv2.imwrite(str(output_path), result)


def remove_watermark_from_video(input_path: Path, output_path: Path) -> None:
    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        raise ValueError("Could not open video.")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

    tracks: List[Track] = []
    next_id = 1

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        detections = _detect_text_candidates(frame)
        tracks, next_id = _match_tracks(tracks, detections, next_id)

        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        for track in tracks:
            x, y, w, h = _expand_box(track.bbox, frame.shape)
            cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)

        if np.count_nonzero(mask) > 0:
            cleaned = cv2.inpaint(frame, mask, 5, cv2.INPAINT_TELEA)
        else:
            cleaned = frame

        writer.write(cleaned)

    cap.release()
    writer.release()
