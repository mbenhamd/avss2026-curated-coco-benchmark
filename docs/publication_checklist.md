# Publication Checklist

Before pushing this package to a public GitHub repository or archiving it on
Zenodo, complete these checks.

## Required Human Approvals

- Confirm the final public repository URL in `CITATION.cff`.
- Confirm the final author and contributor list in `CITATION.cff` and
  `.zenodo.json`.
- Confirm that the axis and direction annotations can be released publicly under
  CC BY 4.0.
- Confirm the final paper title, venue metadata, and citation text once the AVSS
  paper metadata is final.

## Technical Checks

Run:

```bash
python scripts/validate_release.py .
```

The validator must pass before publication.

Expected release properties:

- no COCO images
- no symlinks
- no model weights
- no private paths
- no internal datasets
- no experiment logs or tracker identifiers
- 4,753 train IDs and 528 validation IDs
- 28,659 train objects and 3,125 validation objects per task

## Suggested Release Flow

1. Create an empty public GitHub repository.
2. Copy the contents of this package into that repository root.
3. Commit with a message such as `docs: release avss 2026 curated coco benchmark`.
4. Tag the first release, for example `v1.0.0`.
5. Connect the GitHub repository to Zenodo.
6. Create a GitHub release so Zenodo mints a DOI.
7. Update `CITATION.cff`, `.zenodo.json`, and the README with the final DOI if
   needed, then tag a follow-up metadata release.
