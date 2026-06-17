# Dataset Card

Public repository: https://github.com/mbenhamd/avss2026-curated-coco-benchmark

Zenodo DOI: pending public archive release.

## Dataset Summary

The AVSS 2026 curated COCO benchmark is a public, COCO-derived evaluation subset
for comparing detection, segmentation, and orientation-aware multitask models on
the same image IDs. It uses COCO object classes and adds two orientation label
families:

- axis: `O` or `D`
- direction: `LR`, `FR`, or `UD`

The package provides text annotations and split definitions only. Images must be
provided by a local official COCO installation.

## Dataset Composition

| Split | Images | Objects |
|---|---:|---:|
| Train | 4,753 | 28,659 |
| Val | 528 | 3,125 |
| Total | 5,281 | 31,784 |

The object labels follow the standard 80-class COCO order listed in
`configs/*.data.yaml`.

## Orientation Distribution

| Label family | Count | Share |
|---|---:|---:|
| Axis `D` | 30,986 | 97.49% |
| Axis `O` | 798 | 2.51% |
| Direction `FR` | 14,254 | 44.85% |
| Direction `LR` | 14,227 | 44.76% |
| Direction `UD` | 3,303 | 10.39% |

This benchmark is strongly diagonal-dominant. Results should be interpreted with
that class imbalance in mind.

## Intended Uses

- Reproduce the AVSS 2026 curated COCO benchmark splits and labels.
- Compare detection, instance-segmentation, and orientation-aware multitask
  models on the same COCO image subset.
- Audit annotation formats and aggregate benchmark statistics.

## Out Of Scope

- The archive is not a general replacement for COCO.
- The archive is not an image redistribution.
- The archive does not include private datasets, trained weights, training logs,
  or private training-framework source code.

## Data Sources

Images are from COCO and are not redistributed here. Object annotations are
COCO-derived. Axis and direction labels are released as part of this benchmark
package, subject to the repository license files and citation requirements.

## Ethical And Legal Notes

COCO images may contain people and real-world scenes. Because the COCO Consortium
does not own the images, this package deliberately excludes images and provides
only annotations, split IDs, and scripts that operate on a user-managed local
COCO installation.
