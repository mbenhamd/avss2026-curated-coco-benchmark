#!/usr/bin/env python3
"""Reconstruct local AVSS 2026 curated COCO task directories.

The script never downloads or redistributes COCO images. It links or copies from
a local COCO image directory supplied by the user.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


TASKS = {
    "detector": {
        "config": "detector.data.yaml",
    },
    "axialor": {
        "config": "axialor.data.yaml",
    },
    "isegmentator": {
        "config": "isegmentator.data.yaml",
    },
    "axissegmentator": {
        "config": "axissegmentator.data.yaml",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build local task directories from this benchmark package and COCO images."
    )
    parser.add_argument(
        "--package-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Root of this benchmark package.",
    )
    parser.add_argument(
        "--coco-image-dir",
        type=Path,
        required=True,
        help="Directory containing official COCO JPEG images, for example train2017.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("data/avss2026_curated_coco"),
        help="Directory where reconstructed task roots will be written.",
    )
    parser.add_argument(
        "--tasks",
        nargs="+",
        choices=sorted(TASKS),
        default=sorted(TASKS),
        help="Task directories to reconstruct.",
    )
    parser.add_argument(
        "--copy-images",
        action="store_true",
        help="Copy COCO images instead of creating symlinks.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace an existing output root.",
    )
    return parser.parse_args()


def load_split_ids(package_root: Path) -> dict[str, list[str]]:
    split_path = package_root / "splits" / "split_ids.json"
    with split_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return {
        "train": [str(image_id) for image_id in payload["train_ids"]],
        "val": [str(image_id) for image_id in payload["val_ids"]],
    }


def prepare_output_root(output_root: Path, overwrite: bool) -> None:
    if output_root.exists():
        if not overwrite:
            raise FileExistsError(f"{output_root} already exists. Use --overwrite to replace it.")
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True)


def write_image_reference(source: Path, target: Path, copy_images: bool) -> None:
    if copy_images:
        shutil.copy2(source, target)
    else:
        target.symlink_to(source.resolve())


def copy_labels(package_root: Path, task: str, split: str, destination: Path) -> None:
    source_dir = package_root / "annotations" / task / split / "labels"
    if not source_dir.is_dir():
        raise FileNotFoundError(f"Missing label directory: {source_dir}")
    destination.mkdir(parents=True, exist_ok=True)
    for label_file in sorted(source_dir.glob("*.txt")):
        shutil.copy2(label_file, destination / label_file.name)


def reconstruct_task(
    package_root: Path,
    coco_image_dir: Path,
    output_root: Path,
    task: str,
    split_ids: dict[str, list[str]],
    copy_images: bool,
) -> None:
    task_root = output_root / task
    task_root.mkdir(parents=True)
    shutil.copy2(package_root / "configs" / TASKS[task]["config"], task_root / "data.yaml")

    for split, image_ids in split_ids.items():
        image_dir = task_root / split / "images"
        label_dir = task_root / split / "labels"
        image_dir.mkdir(parents=True)
        copy_labels(package_root, task, split, label_dir)

        manifest_lines = []
        for image_id in image_ids:
            source = coco_image_dir / f"{image_id}.jpg"
            if not source.is_file():
                raise FileNotFoundError(f"Missing COCO image: {source}")
            target = image_dir / source.name
            write_image_reference(source, target, copy_images)
            manifest_lines.append(f"{split}/images/{source.name}")

        (task_root / f"{split}.txt").write_text(
            "\n".join(manifest_lines) + "\n",
            encoding="utf-8",
        )


def main() -> None:
    args = parse_args()
    package_root = args.package_root.resolve()
    coco_image_dir = args.coco_image_dir.resolve()
    output_root = args.output_root.resolve()

    if not package_root.is_dir():
        raise FileNotFoundError(f"Package root does not exist: {package_root}")
    if not coco_image_dir.is_dir():
        raise FileNotFoundError(f"COCO image directory does not exist: {coco_image_dir}")

    split_ids = load_split_ids(package_root)
    prepare_output_root(output_root, args.overwrite)
    for task in args.tasks:
        reconstruct_task(
            package_root=package_root,
            coco_image_dir=coco_image_dir,
            output_root=output_root,
            task=task,
            split_ids=split_ids,
            copy_images=args.copy_images,
        )

    print(f"Reconstructed {len(args.tasks)} task root(s) under {output_root}")


if __name__ == "__main__":
    main()

