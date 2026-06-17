# Annotation Format

All coordinates are normalized to `[0, 1]`. Object class IDs use the 80-class
COCO order in `configs/*.data.yaml`.

## Axis And Direction IDs

| ID | Axis |
|---:|---|
| 0 | `O` |
| 1 | `D` |

| ID | Direction |
|---:|---|
| 0 | `LR` |
| 1 | `FR` |
| 2 | `UD` |

## Detector

Path pattern:

```text
annotations/detector/{train,val}/labels/{image_id}.txt
```

Line format:

```text
class_id x_center y_center width height
```

## Axialor

Path pattern:

```text
annotations/axialor/{train,val}/labels/{image_id}.txt
```

Line format:

```text
class_id x_center y_center width height axis_id direction_id
```

## Isegmentator

Path pattern:

```text
annotations/isegmentator/{train,val}/labels/{image_id}.txt
```

Line format:

```text
class_id x1 y1 x2 y2 ... xn yn
```

Each polygon row has at least four vertices.

## Axissegmentator

Path pattern:

```text
annotations/axissegmentator/{train,val}/labels/{image_id}_axisseg.txt
```

Line format:

```text
class_id axis_id direction_id x1 y1 x2 y2 ... xn yn
```

Each polygon row has at least four vertices.

