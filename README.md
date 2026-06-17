# AVSS 2026 Curated COCO Benchmark

Public repository: https://github.com/mbenhamd/avss2026-curated-coco-benchmark

Zenodo DOI: pending public archive release.

This repository contains the public benchmark definition for the AVSS 2026 curated
COCO evaluation of four related vision tasks:

- object detection (`detector`)
- object detection with axis and direction labels (`axialor`)
- instance segmentation (`isegmentator`)
- instance segmentation with axis and direction labels (`axissegmentator`)

The archive contains annotations, split definitions, metadata, protocol
configuration, and reconstruction scripts. It does not contain COCO images,
training-framework source code, experiment logs, private paths, credentials, model
weights, or internal datasets.

## Contents

```text
annotations/
  detector/{train,val}/labels/
  axialor/{train,val}/labels/
  isegmentator/{train,val}/labels/
  axissegmentator/{train,val}/labels/
configs/
  *.data.yaml
  benchmark_protocol.yaml
docs/
  annotation_format.md
  redistribution.md
metadata/
  results.csv
  results.md
  stats.json
scripts/
  reconstruct_dataset.py
  validate_release.py
splits/
  split_ids.json
  train_ids.txt
  val_ids.txt
```

## Benchmark Size

| Split | Images | Images with matches | Images without matches | Objects |
|---|---:|---:|---:|---:|
| Train | 4,753 | 4,676 | 77 | 28,659 |
| Val | 528 | 512 | 16 | 3,125 |
| Total | 5,281 | 5,188 | 93 | 31,784 |

All image identifiers are 12-digit COCO image IDs. The image files must be
obtained from the official COCO distribution by the user.

## Reconstruct A Local Dataset

Download COCO images through the official COCO channels, then point the
reconstruction script at the directory containing the JPEG files. For the
benchmark used here, this is the COCO 2017 train image directory.

```bash
python scripts/reconstruct_dataset.py \
  --coco-image-dir /path/to/coco/train2017 \
  --output-root ./data
```

By default, the script creates symlinks to the local COCO images. Use
`--copy-images` only if you need a self-contained local working copy. Do not
publish the copied images as part of this benchmark repository.

## Validate Before Release

```bash
python scripts/validate_release.py .
```

The validator checks that the package contains no image files, no symlinks, no
known private path tokens, and the expected split and annotation counts.

## Licensing

Code in `scripts/` is released under the MIT License. Benchmark annotations,
splits, metadata, and documentation are released under CC BY 4.0 unless a file
states otherwise. COCO images are not included; users must follow the COCO and
source-image terms for any local image use.

See `LICENSE`, `LICENSES/`, and `docs/redistribution.md`.
