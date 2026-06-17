#!/usr/bin/env python3
"""Validate that the public benchmark package is safe to release."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


EXPECTED_SPLITS = {
    "train": {
        "images": 4753,
        "objects": 28659,
    },
    "val": {
        "images": 528,
        "objects": 3125,
    },
}

TASKS = ("detector", "axialor", "isegmentator", "axissegmentator")

FORBIDDEN_SUFFIXES = {
    ".bmp",
    ".gif",
    ".jpeg",
    ".jpg",
    ".npy",
    ".onnx",
    ".png",
    ".pt",
    ".pth",
    ".tif",
    ".tiff",
    ".webp",
    ".engine",
}

FORBIDDEN_TEXT = (
    "/ho" + "me/",
    "/scr" + "atch/",
    "COCO_Final_" + "Output",
    "mben" + "hamdoune",
    "WP" + "N",
    "X-" + "ray",
    "x-" + "ray",
    "HC" + "VM",
    "ml" + "flow",
    "ml" + "runs",
    "node" + "54",
    "gpuh" + "100p",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the public release package.")
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=Path("."),
        help="Package root to validate.",
    )
    return parser.parse_args()


def read_text_for_scan(path: Path) -> str:
    if path.stat().st_size > 8_000_000:
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def validate_no_forbidden_files(root: Path) -> list[str]:
    errors: list[str] = []
    for path in root.rglob("*"):
        if path.is_symlink():
            errors.append(f"Symlink is not allowed: {path.relative_to(root)}")
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append(f"Forbidden release artifact: {path.relative_to(root)}")
            continue
        text = read_text_for_scan(path)
        for token in FORBIDDEN_TEXT:
            if token in text:
                errors.append(f"Forbidden token {token!r} in {path.relative_to(root)}")
    return errors


def count_non_empty_lines(path: Path) -> int:
    total = 0
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                total += 1
    return total


def read_label_rows(path: Path) -> list[list[str]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(stripped.split())
    return rows


def validate_int(
    token: str,
    low: int,
    high: int,
    label: str,
    path: Path,
    line_number: int,
) -> list[str]:
    try:
        value = int(token)
    except ValueError:
        return [f"{path}:{line_number} invalid {label}: {token!r}"]
    if value < low or value > high:
        return [f"{path}:{line_number} {label} out of range: {value}"]
    return []


def validate_coord(token: str, path: Path, line_number: int) -> list[str]:
    try:
        value = float(token)
    except ValueError:
        return [f"{path}:{line_number} invalid coordinate: {token!r}"]
    if value < 0.0 or value > 1.0:
        return [f"{path}:{line_number} coordinate out of range: {value}"]
    return []


def validate_row_format(task: str, row: list[str], path: Path, line_number: int) -> list[str]:
    errors: list[str] = []
    if task == "detector":
        if len(row) != 5:
            return [f"{path}:{line_number} detector row has {len(row)} columns, expected 5"]
        errors.extend(validate_int(row[0], 0, 79, "class_id", path, line_number))
        for token in row[1:]:
            errors.extend(validate_coord(token, path, line_number))
        return errors

    if task == "axialor":
        if len(row) != 7:
            return [f"{path}:{line_number} axialor row has {len(row)} columns, expected 7"]
        errors.extend(validate_int(row[0], 0, 79, "class_id", path, line_number))
        for token in row[1:5]:
            errors.extend(validate_coord(token, path, line_number))
        errors.extend(validate_int(row[5], 0, 1, "axis_id", path, line_number))
        errors.extend(validate_int(row[6], 0, 2, "direction_id", path, line_number))
        return errors

    if task == "isegmentator":
        if len(row) < 9 or len(row) % 2 == 0:
            return [f"{path}:{line_number} invalid polygon row length: {len(row)}"]
        errors.extend(validate_int(row[0], 0, 79, "class_id", path, line_number))
        for token in row[1:]:
            errors.extend(validate_coord(token, path, line_number))
        return errors

    if task == "axissegmentator":
        if len(row) < 11 or len(row) % 2 == 0:
            return [f"{path}:{line_number} invalid axis-polygon row length: {len(row)}"]
        errors.extend(validate_int(row[0], 0, 79, "class_id", path, line_number))
        errors.extend(validate_int(row[1], 0, 1, "axis_id", path, line_number))
        errors.extend(validate_int(row[2], 0, 2, "direction_id", path, line_number))
        for token in row[3:]:
            errors.extend(validate_coord(token, path, line_number))
        return errors

    return [f"Unknown task: {task}"]


def validate_splits(root: Path) -> list[str]:
    errors: list[str] = []
    split_path = root / "splits" / "split_ids.json"
    if not split_path.is_file():
        return ["Missing splits/split_ids.json"]

    with split_path.open("r", encoding="utf-8") as handle:
        split_payload = json.load(handle)

    for split, expected in EXPECTED_SPLITS.items():
        key = f"{split}_ids"
        ids = [str(image_id) for image_id in split_payload.get(key, [])]
        if len(ids) != expected["images"]:
            errors.append(f"{key} has {len(ids)} ids, expected {expected['images']}")

        txt_path = root / "splits" / f"{split}_ids.txt"
        if not txt_path.is_file():
            errors.append(f"Missing {txt_path.relative_to(root)}")
            continue
        txt_ids = [line.strip() for line in txt_path.read_text(encoding="utf-8").splitlines()]
        if txt_ids != ids:
            errors.append(f"{txt_path.relative_to(root)} does not match split_ids.json")

    return errors


def validate_annotations(root: Path) -> list[str]:
    errors: list[str] = []
    for task in TASKS:
        for split, expected in EXPECTED_SPLITS.items():
            label_dir = root / "annotations" / task / split / "labels"
            if not label_dir.is_dir():
                errors.append(f"Missing label directory: {label_dir.relative_to(root)}")
                continue
            label_files = sorted(label_dir.glob("*.txt"))
            if len(label_files) != expected["images"]:
                errors.append(
                    f"{label_dir.relative_to(root)} has {len(label_files)} files, "
                    f"expected {expected['images']}"
                )
            line_count = sum(count_non_empty_lines(path) for path in label_files)
            if line_count != expected["objects"]:
                errors.append(
                    f"{label_dir.relative_to(root)} has {line_count} objects, "
                    f"expected {expected['objects']}"
                )
            for path in label_files:
                for line_number, row in enumerate(read_label_rows(path), start=1):
                    errors.extend(
                        validate_row_format(
                            task=task,
                            row=row,
                            path=path.relative_to(root),
                            line_number=line_number,
                        )
                    )
    return errors


def validate_cross_task_alignment(root: Path) -> list[str]:
    errors: list[str] = []
    for split in EXPECTED_SPLITS:
        detector_dir = root / "annotations" / "detector" / split / "labels"
        axialor_dir = root / "annotations" / "axialor" / split / "labels"
        iseg_dir = root / "annotations" / "isegmentator" / split / "labels"
        axisseg_dir = root / "annotations" / "axissegmentator" / split / "labels"

        detector_ids = sorted(path.stem for path in detector_dir.glob("*.txt"))
        axialor_ids = sorted(path.stem for path in axialor_dir.glob("*.txt"))
        iseg_ids = sorted(path.stem for path in iseg_dir.glob("*.txt"))
        axisseg_ids = sorted(
            path.name.replace("_axisseg.txt", "") for path in axisseg_dir.glob("*.txt")
        )

        if detector_ids != axialor_ids:
            errors.append(f"{split} detector and axialor image IDs differ")
        if detector_ids != iseg_ids:
            errors.append(f"{split} detector and isegmentator image IDs differ")
        if detector_ids != axisseg_ids:
            errors.append(f"{split} detector and axissegmentator image IDs differ")

        for image_id in detector_ids:
            detector_rows = read_label_rows(detector_dir / f"{image_id}.txt")
            axialor_rows = read_label_rows(axialor_dir / f"{image_id}.txt")
            iseg_rows = read_label_rows(iseg_dir / f"{image_id}.txt")
            axisseg_rows = read_label_rows(axisseg_dir / f"{image_id}_axisseg.txt")
            row_counts = {len(detector_rows), len(axialor_rows), len(iseg_rows), len(axisseg_rows)}
            if len(row_counts) != 1:
                errors.append(f"{split}/{image_id} object count differs across tasks")
                continue
            for row_number, (detector, axialor, iseg, axisseg) in enumerate(
                zip(detector_rows, axialor_rows, iseg_rows, axisseg_rows),
                start=1,
            ):
                if detector != axialor[:5]:
                    errors.append(f"{split}/{image_id}:{row_number} detector/axialor mismatch")
                if iseg[0] != axisseg[0] or iseg[1:] != axisseg[3:]:
                    errors.append(f"{split}/{image_id}:{row_number} polygon mismatch")
                if detector[0] != iseg[0]:
                    errors.append(f"{split}/{image_id}:{row_number} class mismatch")
    return errors


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        print(f"Package root does not exist: {root}", file=sys.stderr)
        return 2

    errors = []
    errors.extend(validate_no_forbidden_files(root))
    errors.extend(validate_splits(root))
    errors.extend(validate_annotations(root))
    errors.extend(validate_cross_task_alignment(root))

    if errors:
        print("Release validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Release validation passed: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
